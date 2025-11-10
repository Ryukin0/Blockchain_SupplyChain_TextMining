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

# ========== 自定义关键词 ==========
keywords = [
    "区块链", "数字化", "数智化", "智能化", "人工智能",
    "数据", "可信", "信任", "供应链", "信用", "透明", "追溯", "共享"
]

# ========== 读取并统计 ==========
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

# ========== 标准化（归一化） ==========
total = sum(all_counts.values())
norm_freq = {k: v / total for k, v in all_counts.items()}

# 转换为 DataFrame
df = pd.DataFrame({
    "关键词": list(norm_freq.keys()),
    "标准化频率": list(norm_freq.values()),
    "原始计数": [all_counts[k] for k in norm_freq.keys()]
}).sort_values(by="标准化频率", ascending=False)

# 保存结果
df.to_excel(os.path.join(OUTPUT_DIR, f"词频统计_{YEAR}.xlsx"), index=False)

# ===== 中文字体支持（Mac / Windows都适用）=====
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.sans-serif'] = ['Heiti TC', 'SimHei']  # Mac用Heiti，Win用SimHei

# ========== 可视化1：关键词柱状图 ==========
words = df["关键词"]
freqs = df["原始计数"]

plt.figure(figsize=(12, 7))
bars = plt.bar(words, freqs, color="#4A90E2", edgecolor="black", alpha=0.85)

plt.title(f"企业年报高频词统计（{YEAR}年度）", fontsize=18, fontweight="bold", pad=20)
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
plt.savefig(os.path.join(OUTPUT_DIR, f"词频统计_{YEAR}_美化版.png"), dpi=300, bbox_inches='tight')
plt.show()

# ========== 可视化2：词云 ==========
wc = WordCloud(
    font_path="/System/Library/Fonts/STHeiti Medium.ttc",
    width=800, height=600,
    background_color="white"
)
wc.generate_from_frequencies(all_counts)
wc.to_file(os.path.join(OUTPUT_DIR, f"词云_{YEAR}.png"))

print(f"✅ {YEAR} 年关键词分析完成！")
print(f"📊 结果保存路径: {OUTPUT_DIR}")
