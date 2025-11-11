import os
import fitz  # PyMuPDF
from tqdm import tqdm

# ======================
# 路径配置
# ======================
YEAR = 2018
BASE_DIR = "/Users/qqqqq/Desktop/ppppp/年报"
PDF_DIR = os.path.join(BASE_DIR, f"年报PDF_{YEAR}_有效")
TXT_DIR = os.path.join(BASE_DIR, f"年报TXT_{YEAR}")
os.makedirs(TXT_DIR, exist_ok=True)

# ======================
# PDF 转 TXT
# ======================
def pdf_to_txt(pdf_path, txt_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            page_text = page.get_text("text").strip()
            if len(page_text) > 30:  # 跳过空页或图片页
                text += page_text + "\n"
        doc.close()

        if text.strip():
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
            return True
        else:
            return False
    except Exception as e:
        print(f"❌ 转换失败: {pdf_path}, 错误: {e}")
        return False

# ======================
# 批量执行转换
# ======================
pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]

for pdf_file in tqdm(pdf_files, desc=f"PDF 转 TXT ({YEAR})"):
    pdf_path = os.path.join(PDF_DIR, pdf_file)
    txt_name = pdf_file.replace(".pdf", ".txt")
    txt_path = os.path.join(TXT_DIR, txt_name)

    if not os.path.exists(txt_path):  # 防止重复转换
        success = pdf_to_txt(pdf_path, txt_path)
        if not success:
            print(f"⚠️ 跳过空文件: {pdf_file}")

print(f"✅ 已完成 {YEAR} 年所有 PDF → TXT 转换！")
print(f"📁 输出目录: {TXT_DIR}")
