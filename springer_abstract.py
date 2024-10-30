import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import time
import random

# 爬取函数，根据 DOI 获取摘要
def get_full_abstract(doi_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }
    
    try:
        response = requests.get(doi_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # 查找摘要部分的内容
            abstract_section = soup.find('div', class_='c-article-section__content')
            
            if abstract_section:
                # 提取摘要的文本内容
                abstract = abstract_section.get_text(strip=True)
                return abstract  # 直接返回摘要内容
            else:
                return "No abstract section found."
        else:
            return f"Failed to retrieve page, status code: {response.status_code}"
    
    except requests.exceptions.RequestException as e:
        # 捕获所有请求异常并返回错误信息
        return f"Error: {str(e)}"

# 读取 CSV 文件并逐行处理
def update_abstracts(csv_file, output_file, start_id):
    # 读取 CSV 文件
    df = pd.read_csv(csv_file)
    
    # 使用 tqdm 来显示进度条，从指定 ID 开始处理
    for index, row in tqdm(df[df['ID'] >= start_id].iterrows(), total=df[df['ID'] >= start_id].shape[0]):
        link = row['link']
        
        # 如果 link 不包含 10.1007，跳过处理
        if '10.1007' not in link:
            continue
        
        # 如果 abstract 是 None 或 'None'，尝试爬取新的摘要
        if pd.isna(row['abstract']) or row['abstract'] == 'None':
            new_abstract = get_full_abstract(link)
            df.at[index, 'abstract'] = new_abstract  # 更新摘要
            
            # 每次更新摘要后，立刻写回 CSV 文件，避免数据丢失
            df.to_csv(output_file, index=False)
            
            # 随机等待0到1秒，避免爬取过快被封
            time.sleep(random.uniform(0, 1))

# 处理文件
input_csv = 'datas/updated_papers_with_abstract.csv'
output_csv = 'datas/updated_papers_with_abstract_updated.csv'

# 从指定 ID 开始处理
start_id = int(input("请输入开始处理的ID: "))  # 用户输入的起始 ID
update_abstracts(input_csv, output_csv, start_id)
