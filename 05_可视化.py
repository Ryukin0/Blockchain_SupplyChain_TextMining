import os
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from tqdm import tqdm
import jieba

# ========== 路径配置 ==========
YEAR = 2018
BASE_DIR = "/Users/qqqqq/Desktop/ppppp/年报"
TXT_DIR = os.path.join(BASE_DIR, f"年报TXT_{YEAR}")
OUTPUT_DIR = os.path.join(BASE_DIR, f"分析结果_{YEAR}")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ========== 自定义关键词体系 ==========
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

# 扁平化关键词列表
keywords = [w for group in keyword_groups.values() for w in group]

# ========== 统计 ==========
all_counts = Counter()
txt_files = [f for f in os.listdir(TXT_DIR) if f.endswith(".txt")]

for txt_file in tqdm(txt_files, desc=f"统计关键词 ({YEAR})"):
    txt_path = os.path.join(TXT_DIR, txt_file)
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()
        words = jieba.lcut(text)
        word_count = Counter(words)
        for kw in keywords:
            all_counts[kw] += word_count[kw]
    except Exception as e:
        print(f"❌ 文件读取失败: {txt_file}, 错误: {e}")

# ========== 标准化 ==========
total = sum(all_counts.values())
norm_freq = {k: v / total for k, v in all_counts.items()}

df = pd.DataFrame({
    "关键词": list(norm_freq.keys()),
    "标准化频率": list(norm_freq.values()),
    "原始计数": [all_counts[k] for k in norm_freq.keys()]
}).sort_values(by="标准化频率", ascending=False)

df.to_excel(os.path.join(OUTPUT_DIR, f"词频统计_{YEAR}.xlsx"), index=False)

# ===== 字体支持 =====
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.sans-serif'] = ['Heiti TC', 'SimHei']

# ========== 可视化1：关键词柱状图 ==========
words = df["关键词"]
freqs = df["原始计数"]

plt.figure(figsize=(13, 7))
colors = [
    "#E24A33" if any(x in w for x in ["链", "加密", "可信", "共识"]) else "#4A90E2"
    for w in words
]
bars = plt.bar(words, freqs, color=colors, edgecolor="black", alpha=0.85)

plt.title(f"{YEAR} 年企业年报高频词统计\n（区块链 / 加密算法 / 可信计算相关词汇高亮）", fontsize=18, fontweight="bold", pad=20)
plt.xlabel("关键词", fontsize=14)
plt.ylabel("出现次数", fontsize=14)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.5)

for bar in bars:
    plt.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + 1,
             f"{int(bar.get_height())}",
             ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, f"词频统计_{YEAR}.png"), dpi=300, bbox_inches='tight')
plt.show()

# ========== 可视化2：词云 ==========
wc = WordCloud(
    font_path="/System/Library/Fonts/STHeiti Medium.ttc",
    width=800, height=600,
    background_color="white",
    colormap="viridis"
)
wc.generate_from_frequencies(all_counts)
wc.to_file(os.path.join(OUTPUT_DIR, f"词云_{YEAR}.png"))

print(f"✅ {YEAR} 年关键词分析完成！")
print(f"📊 结果保存路径: {OUTPUT_DIR}")

# ========== 可视化3 & 4：可信度指数 ==========
trust_path = os.path.join(OUTPUT_DIR, f"数据可信度指数_{YEAR}.xlsx")
if os.path.exists(trust_path):
    trust_df = pd.read_excel(trust_path)
    trust_df = trust_df[trust_df["Trust_Index"] >= 0]

    # 分布图
    plt.figure(figsize=(10, 6))
    plt.hist(trust_df["Trust_Index"], bins=30, color="#6EC6CA", edgecolor="black", alpha=0.8)
    plt.title(f"{YEAR} 年企业年报“数据可信度指数”分布", fontsize=18, fontweight="bold", pad=20)
    plt.xlabel("Trust_Index（可信度指数）", fontsize=14)
    plt.ylabel("企业数量", fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"可信度指数分布_{YEAR}.png"), dpi=300, bbox_inches='tight')
    plt.show()

    # Top 20
    top20 = trust_df.sort_values(by="Trust_Index", ascending=False).head(20)
    plt.figure(figsize=(12, 8))
    bars = plt.barh(top20["公司简称"], top20["Trust_Index"], color="#FFB74D", alpha=0.85)
    plt.gca().invert_yaxis()
    plt.title(f"{YEAR} 年“可信度指数”最高的20家企业", fontsize=18, fontweight="bold", pad=20)
    plt.xlabel("Trust_Index", fontsize=14)
    plt.ylabel("公司简称", fontsize=14)
    for bar in bars:
        plt.text(bar.get_width() + 0.0005,
                 bar.get_y() + bar.get_height()/2,
                 f"{bar.get_width():.4f}",
                 va='center', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"可信度前20企业_{YEAR}.png"), dpi=300, bbox_inches='tight')
    plt.show()

    print(f"✅ 可信度指数分布与Top20图已生成！")
else:
    print(f"⚠️ 未找到 {trust_path}，跳过可信度可视化。")
