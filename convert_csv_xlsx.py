'''
Author: ZhaoyangZhang
Date: 2024-10-18 22:03:46
LastEditors: Do not edit
LastEditTime: 2024-10-18 22:05:12
FilePath: /findPapers/convert_csv_xlsx.py
'''
import pandas as pd

def csv_to_xlsx(csv_file_path, xlsx_file_path):
    # 读取 CSV 文件
    df = pd.read_csv(csv_file_path)
    
    # 将 DataFrame 保存为 Excel 文件
    df.to_excel(xlsx_file_path, index=False)

# 示例用法
csv_file_path = 'datas/dblp_papers_search_results_archive_with_abstracts.csv'  # 你的 CSV 文件路径
xlsx_file_path = 'datas/dblp_papers_search_results_archive_with_abstracts.xlsx'  # 输出的 XLSX 文件路径

csv_to_xlsx(csv_file_path, xlsx_file_path)

print(f"CSV 已成功转换为 XLSX 并保存至: {xlsx_file_path}")
