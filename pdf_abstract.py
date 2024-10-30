import requests
import fitz  # PyMuPDF
import csv
import os
from tqdm import tqdm

# 下载 PDF 文件
def download_pdf(pdf_url, save_path):
    response = requests.get(pdf_url)
    with open(save_path, 'wb') as f:
        f.write(response.content)
    print(f"PDF downloaded: {save_path}")

# 从 PDF 中提取第一页的文本
def extract_text_from_first_page(pdf_path):
    doc = fitz.open(pdf_path)  # 打开 PDF
    page = doc.load_page(0)  # 加载第一页
    text = page.get_text()  # 提取第一页的文本
    return text

# 从 PDF 文本中提取摘要
def extract_abstract(text):
    abstract_start = text.lower().find("abstract")
    if abstract_start != -1:
        # 查找摘要结束位置（通常以 "Introduction" 或 1000 字符结束）
        abstract_end = text.lower().find("introduction", abstract_start)  
        if abstract_end == -1:
            abstract_end = abstract_start + 1000  # 如果没有找到 introduction，截取1000字符以内的内容
        
        abstract = text[abstract_start:abstract_end].strip()

        # 过滤掉多余的 "Abstract" 词汇
        abstract = abstract.replace("ABSTRACT", "").replace("Abstract", "").strip()

        # 处理换行符，移除多余的换行，使其连成一段
        abstract = " ".join(abstract.splitlines())

        # 去除不相关内容，比如 PVLDB Reference Format 等
        abstract = abstract.split("PVLDB Reference Format")[0].strip()

        return abstract
    return "Abstract not found"

# 主函数：从 CSV 中读取数据，处理并生成新的 CSV
def process_papers(input_csv, output_csv):
    # 创建 downloads 文件夹，如果不存在的话
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    # 读取输入 CSV 文件
    with open(input_csv, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames  # 获取表头

        # 打开输出 CSV 文件
        with open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            # 使用 tqdm 进行进度显示
            for row in tqdm(reader, desc="Processing papers"):
                link = row['link']
                
                # 如果链接不是以 .pdf 结尾，直接跳过，写入原始数据
                if not link.endswith('.pdf'):
                    writer.writerow(row)
                    continue

                # 获取文件名（从 URL 中提取文件名）
                pdf_filename = link.split('/')[-1]
                save_path = os.path.join('downloads', pdf_filename)

                # 下载 PDF 文件
                download_pdf(link, save_path)

                # 提取 PDF 中的摘要
                try:
                    text = extract_text_from_first_page(save_path)
                    abstract = extract_abstract(text)
                except Exception as e:
                    abstract = f"Error extracting abstract: {str(e)}"

                # 更新摘要字段
                row['abstract'] = abstract

                # 写入新 CSV 文件
                writer.writerow(row)

# 示例：输入 CSV 文件路径，处理并输出新的 CSV 文件
input_csv = 'datas/merged_papers.csv'  # 输入文件路径
output_csv = 'datas/updated_papers_with_abstract.csv'  # 输出文件路径

# 处理论文数据
process_papers(input_csv, output_csv)
