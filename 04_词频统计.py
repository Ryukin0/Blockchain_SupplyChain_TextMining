import os
import re
import jieba
import pandas as pd
from tqdm import tqdm
from collections import Counter

# ===== 参数配置 =====
YEAR = 2018
BASE_DIR = "/Users/qqqqq/Desktop/ppppp/年报"
TXT_DIR = os.path.join(BASE_DIR, f"年报TXT_{YEAR}")
OUTPUT_DIR = os.path.join(BASE_DIR, f"分析结果_{YEAR}")
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"{YEAR}_年报词频统计.xlsx")

# ===== 定义关键词体系 =====
keyword_groups = {
    "区块链相关": [
        "区块链", "分布式账本", "智能合约", "去中心化", "联盟链", "公有链", "私有链",
        "上链", "链上", "链改", "链端", "链条数据", "链上数据", "链上交易",
        "加密存证", "电子存证", "溯源系统", "数字凭证", "数据确权", "数据共享平台",
        "可信计算", "加密算法", "加密技术", "哈希算法", "密码学", "零知识证明",
        "共识算法", "共识机制", "节点共识", "智能节点", "隐私保护", "数据安全", "国密算法", "防篡改"
    ],

    "数字化转型": [
        "数字化", "数智化", "信息化", "智能化", "大数据", "云计算", "人工智能", 
        "物联网", "数字平台", "数字基础设施", "自动化", "机器学习"
    ],

    "供应链治理": [
        "供应链", "上游", "下游", "供应商", "物流", "协同", "链条", "溯源",
        "产业链", "链主企业", "供应链金融", "流通管理"
    ],

    "信用与信任": [
        "信用", "信任", "信誉", "合规", "透明", "可信", "信用体系", "信用管理",
        "风险控制", "验证", "共享", "安全", "隐私", "防篡改", "共识"
    ]
}

# ===== 统计函数 =====
def count_keywords(text, keyword_groups):
    text = re.sub(r"\s+", "", text)
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
trust_indices = []

txt_files = [f for f in os.listdir(TXT_DIR) if f.endswith(".txt")]

trust_words = ["可信", "透明", "追溯", "信任", "验证", "共享", "安全", "隐私", "防篡改", "共识"]

for txt_file in tqdm(txt_files, desc=f"统计{YEAR}年年报关键词"):
    try:
        company_code, company_name = txt_file.replace(".txt", "").split("_", 1)
        txt_path = os.path.join(TXT_DIR, txt_file)

        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        # ---- 1. 关键词统计 ----
        result = count_keywords(text, keyword_groups)
        result["公司代码"] = company_code
        result["公司简称"] = company_name
        records.append(result)

        # ---- 2. 信任指数计算 ----
        words = jieba.lcut(text)
        word_count = Counter(words)
        total_words = len(words)
        trust_sum = sum(word_count[w] for w in trust_words if w in word_count)
        trust_index = trust_sum / total_words if total_words > 0 else 0
        trust_indices.append({
            "公司代码": company_code,
            "公司简称": company_name,
            "Trust_Index": trust_index
        })

    except Exception as e:
        print(f"⚠️ 读取失败: {txt_file}，错误: {e}")

# ===== 保存结果 =====
df = pd.DataFrame(records)
df = df[["公司代码", "公司简称"] + list(keyword_groups.keys()) + ["总字数"]]
df.to_excel(OUTPUT_PATH, index=False)

trust_df = pd.DataFrame(trust_indices)
trust_df.to_excel(os.path.join(OUTPUT_DIR, f"数据可信度指数_{YEAR}.xlsx"), index=False)

print(f"✅ 已完成 {YEAR} 年年报关键词词频统计！结果保存至：{OUTPUT_PATH}")
print(f"✅ 数据可信度指数已生成！保存至：数据可信度指数_{YEAR}.xlsx")
