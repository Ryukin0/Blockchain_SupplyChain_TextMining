import os
import requests
import pandas as pd
import time
from pathlib import Path

# ========== 基本参数 ==========
YEAR = 2023  # 按照年份进行链接抓取，此处可输入2018-2026
SAVE_FOLDER = Path.home() / "Desktop" / "年报链接获取"
SAVE_FOLDER.mkdir(exist_ok=True)
FINAL_PATH = SAVE_FOLDER / f"{YEAR}_年报链接.xlsx"

ANNOUNCE_URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
COMPANY_INFO_URL = "http://www.cninfo.com.cn/new/data/companyList.json"

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'http://www.cninfo.com.cn/',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}

# ========== 获取公司信息 ==========
def get_company_info():
    print("正在加载上市公司行业信息（新版接口）...")
    url = "http://www.cninfo.com.cn/new/data/companyList.json"
    res = requests.get(url, headers=headers)
    try:
        data = res.json()
    except Exception as e:
        print("❌ 返回数据不是JSON:", e)
        return pd.DataFrame(columns=["公司代码", "公司简称", "行业"])

    df_list = []
    company_blocks = data.get("companyList", [])
    for block in company_blocks:
        if isinstance(block, dict) and "stockList" in block:
            sub_list = block["stockList"]
            if isinstance(sub_list, list) and len(sub_list) > 0:
                df = pd.DataFrame(sub_list)
                df_list.append(df)
    if not df_list:
        print("⚠️ 未从接口获取到公司信息，请检查网络或接口结构。")
        return pd.DataFrame(columns=["公司代码", "公司简称", "行业"])

    all_info = pd.concat(df_list, ignore_index=True)
    rename_map = {}
    for col in all_info.columns:
        if "code" in col.lower(): rename_map[col] = "公司代码"
        if "zwjc" in col.lower() or "简称" in col: rename_map[col] = "公司简称"
        if "industry" in col.lower(): rename_map[col] = "行业"
    all_info = all_info.rename(columns=rename_map)

    all_info["公司代码"] = all_info["公司代码"].astype(str)
    print(f"✅ 共加载 {len(all_info)} 家上市公司。")
    return all_info[["公司代码", "公司简称", "行业"]]

# ========== 获取年报函数（断点续采） ==========
def get_annual_reports(plate, company_info):
    print(f"\n📦 开始采集 {plate} 板块 {YEAR} 年年报信息...")

    temp_path = SAVE_FOLDER / f"temp_{plate}_{YEAR}.csv"
    all_data = []

    # 如果存在临时文件，则从上次进度继续
    start_page = 1
    if temp_path.exists():
        df_temp = pd.read_csv(temp_path)
        all_data = df_temp.to_dict('records')
        start_page = (len(all_data) // 30) + 1
        print(f"🔁 检测到断点，续采第 {start_page} 页（已采 {len(all_data)} 条）")

    params = {
        'stock': '',
        'tabName': 'fulltext',
        'plate': plate,
        'category': 'category_ndbg_szsh',
        'seDate': f'{YEAR}-01-01~{YEAR}-12-31',
        'pageNum': 1,
        'pageSize': 30,
        'column': 'szse',
    }

    MAX_PAGES = 100
    for page in range(start_page, MAX_PAGES + 1):
        params['pageNum'] = page
        try:
            res = requests.post(ANNOUNCE_URL, data=params, headers=headers, timeout=15)
            if res.status_code != 200:
                print(f"⚠️ 第{page}页请求异常，状态码 {res.status_code}")
                break

            json_data = res.json()
            if not isinstance(json_data, dict) or "announcements" not in json_data:
                print(f"⚠️ 第{page}页返回空或结构异常，退出循环。")
                break

            announcements = json_data.get("announcements", [])
            if not announcements:
                print(f"✅ 第{page}页为空，说明该板块已采完。")
                break

            for ann in announcements:
                title = ann.get('announcementTitle', '')
                if any(x in title for x in ['摘要', '英文版', '公告', '提示', '补充', '更正']):
                    continue
                if 'ST' in ann.get('secName', ''):
                    continue
                record = {
                    '公司代码': ann.get('secCode'),
                    '公司简称': ann.get('secName'),
                    '公告标题': title,
                    '公告日期': ann.get('announcementTime'),
                    'PDF链接': 'http://static.cninfo.com.cn/' + ann.get('adjunctUrl', '')
                }
                all_data.append(record)

            # 每 10 页保存一次进度
            if page % 10 == 0:
                pd.DataFrame(all_data).to_csv(temp_path, index=False)
                print(f"💾 已保存中间结果（第 {page} 页）")

            print(f"→ 已获取第 {page} 页，共 {len(all_data)} 条")
            time.sleep(0.8)

        except requests.exceptions.Timeout:
            print(f"⏳ 第{page}页请求超时，跳过。")
            continue
        except Exception as e:
            print(f"❌ 第{page}页出错: {e}")
            time.sleep(2)
            continue

    df = pd.DataFrame(all_data)
    if not df.empty:
        df = df.merge(company_info, on=["公司代码", "公司简称"], how="left")
        df = df[~df["行业"].isin(["房地产业", "金融业"])]
    return df

# ========== 主程序 ==========
if __name__ == "__main__":
    company_info = get_company_info()
    plates = ["szse", "sse", "bj"]  # 深市、沪市、北交所
    final_df_list = []

    for p in plates:
        df_plate = get_annual_reports(p, company_info)
        if not df_plate.empty:
            final_df_list.append(df_plate)
        time.sleep(2)

    if final_df_list:
        final_df = pd.concat(final_df_list, ignore_index=True)
        final_df.to_excel(FINAL_PATH, index=False)
        print(f"\n✅ 已保存最终文件: {FINAL_PATH}")
        print(f"共采集 {len(final_df)} 条符合条件的年报链接。")
    else:
        print("⚠️ 未采集到任何数据，请检查接口结构或网络。")
