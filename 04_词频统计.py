import os
import re
import pandas as pd
from tqdm import tqdm
from collections import Counter

# ===== 参数配置 =====
YEAR = 2018
BASE_DIR = "/Users/qqqqq/Desktop/ppppp/年报"
TXT_DIR = os.path.join(BASE_DIR, f"年报TXT_{YEAR}")  # 确认你的TXT文件夹名
OUTPUT_PATH = os.path.join(BASE_DIR, f"{YEAR}_年报词频统计.xlsx")

# ===== 定义关键词体系 =====
keyword_groups = {
    "区块链相关": ["区块链", "分布式账本", "智能合约", "去中心化", "链上", "比特币", "以太坊"],
    "数字化转型": ["数字化", "数智化", "信息化", "智能化", "大数据", "云计算", "人工智能", "物联网", "数字平台"],
    "供应链治理": ["供应链", "上游", "下游", "供应商", "物流", "协同", "链条", "溯源", "产业链", "链主企业"],
    "信用与信任": ["信用", "信任", "信誉", "合规", "透明", "可信", "信用体系", "信用管理", "风险控制"]
}

# ===== 统计函数 =====
def count_keywords(text, keyword_groups):
    text = re.sub(r"\s+", "", text)  # 去除空格和换行
    counts = {}
    for group, words in keyword_groups.items():
        total = 0
        for w in words:
            total += text.count(w)
        counts[group] = total
    counts["总字数"] = len(text)
    return counts

# ===== 批量遍历TXT文件 =====
records = []
txt_files = [f for f in os.listdir(TXT_DIR) if f.endswith(".txt")]

for txt_file in tqdm(txt_files, desc=f"统计{YEAR}年年报关键词"):
    company_code, company_name = txt_file.replace(".txt", "").split("_", 1)
    txt_path = os.path.join(TXT_DIR, txt_file)
    try:
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        result = count_keywords(text, keyword_groups)
        result["公司代码"] = company_code
        result["公司简称"] = company_name
        records.append(result)
    except Exception as e:
        print(f"⚠️ 读取失败: {txt_file}，错误: {e}")

# ===== 保存结果 =====
df = pd.DataFrame(records)
df = df[["公司代码", "公司简称"] + list(keyword_groups.keys()) + ["总字数"]]
df.to_excel(OUTPUT_PATH, index=False)
print(f"✅ 已完成 {YEAR} 年年报关键词词频统计！结果保存至：{OUTPUT_PATH}")
