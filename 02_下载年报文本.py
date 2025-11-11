import os
import time
import random
import requests
import pandas as pd
import fitz  # 用于检测PDF有效性
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# ========== 参数设置 ==========
YEAR = 2020
BASE_DIR = "/Users/qqqqq/Desktop/ppppp/年报"
EXCEL_PATH = os.path.join(BASE_DIR, "年报链接获取", f"{YEAR}_年报链接.xlsx")
PDF_DIR = os.path.join(BASE_DIR, f"年报PDF_{YEAR}")
VALID_DIR = os.path.join(BASE_DIR, f"年报PDF_{YEAR}_有效")  # ✅ 有效PDF目录
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(VALID_DIR, exist_ok=True)

# ========== 下载函数 ==========
def download_pdf(row):
    name = f"{row['公司代码']}_{row['公司简称']}.pdf"
    pdf_path = os.path.join(PDF_DIR, name)
    link = str(row['PDF链接']).strip()

    # 修正链接拼接
    link = link.replace("cninfo.com.cnhttp", "cninfo.com.cn")
    link = link.replace("http://", "https://")
    url = link if link.startswith("http") else "https://static.cninfo.com.cn" + link

    if os.path.exists(pdf_path):
        return f"✅ 已存在 {name}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
        "Accept": "application/pdf",
        "Referer": "https://www.cninfo.com.cn/",
    }

    for attempt in range(2):
        try:
            r = requests.get(url, headers=headers, timeout=12)
            if r.status_code == 200 and "application/pdf" in r.headers.get("Content-Type", ""):
                with open(pdf_path, "wb") as f:
                    f.write(r.content)
                return f"✅ 成功 {name}"
            else:
                return f"⚠️ 非PDF或无效链接 {name} ({r.status_code})"
        except Exception as e:
            time.sleep(1)
            if attempt == 1:
                return f"❌ 失败 {name}: {e}"

# ========== 并发下载 ==========
df = pd.read_excel(EXCEL_PATH)
print(f"📄 共 {len(df)} 条年报链接，开始下载 {YEAR} 年 PDF ...")

results = []
with ThreadPoolExecutor(max_workers=12) as executor:
    futures = [executor.submit(download_pdf, row) for _, row in df.iterrows()]
    for i, future in enumerate(tqdm(as_completed(futures), total=len(futures))):
        results.append(future.result())
        time.sleep(random.uniform(0.05, 0.2))  # 防反爬

# ========== 下载结果统计 ==========
success = [r for r in results if "✅ 成功" in r or "✅ 已存在" in r]
failed = [r for r in results if "❌" in r]
print(f"\n✅ 成功 {len(success)} 份 | ❌ 失败 {len(failed)} 份 | 总计 {len(df)}")

# =====================================================
# ✅ 新增部分：下载完成后自动检测PDF完整性
# =====================================================

print(f"\n🔍 正在检测 PDF 有效性，请稍候...")

bad_files = []
for pdf_file in tqdm(os.listdir(PDF_DIR), desc="检测PDF文件"):
    if not pdf_file.endswith(".pdf"):
        continue
    src_path = os.path.join(PDF_DIR, pdf_file)
    try:
        with fitz.open(src_path) as doc:
            if len(doc) == 0:
                raise ValueError("空文件")
        # 检测通过：移动到有效目录
        os.rename(src_path, os.path.join(VALID_DIR, pdf_file))
    except Exception as e:
        bad_files.append((pdf_file, str(e)))

# 记录坏文件日志
bad_log_path = os.path.join(BASE_DIR, f"坏文件日志_{YEAR}.txt")
with open(bad_log_path, "w", encoding="utf-8") as f:
    for name, err in bad_files:
        f.write(f"{name}\t{err}\n")

print(f"\n✅ 检测完成！有效PDF：{len(os.listdir(VALID_DIR))} 份 | 坏文件：{len(bad_files)} 份")
print(f"📁 坏文件日志已保存：{bad_log_path}")
print(f"📂 有效文件目录：{VALID_DIR}")
