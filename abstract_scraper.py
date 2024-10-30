'''
Author: ZhaoyangZhang
Date: 2024-10-18 16:31:07
LastEditors: Do not edit
LastEditTime: 2024-10-18 22:48:45
FilePath: /findPapers/abstract_scraper.py
'''
import requests
import unittest
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm

# 配置重试策略，处理网络错误和 SSL 握手错误
def configure_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

# 初始化会话
session = configure_session()

# 用户代理 (User-Agent)，模拟浏览器请求
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

# 定义抓取 ACM Digital Library 摘要的函数
def get_acm_abstract(url):
    try:
        response = session.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        abstracts_div = soup.find('div', id='abstracts')
        if abstracts_div:
            abstract_section = abstracts_div.find('section', id='abstract')
            abstract_div = abstract_section.find('div', role='paragraph')
            if abstract_div:
                return abstract_div.get_text(strip=True)
            else:
                return "Abstract content not found."
        else:
            return "Abstracts section not found."
    except Exception as e:
        return f"Error: {str(e)}"
    
# 定义抓取 IEEE Xplore 摘要的函数，并添加调试输出
def get_ieee_abstract(url):
    try:
        response = session.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 输出完整的 HTML 结构，以便调试
        print("===== HTML content =====")
        print(soup.prettify()[:5000])  # 输出前5000字符的HTML，防止输出过长
        print("========================")

        # 通过 class 为 "document-abstract" 的 section 元素查找摘要部分
        abstract_section = soup.find('section', class_='document-abstract')
        if abstract_section:
            print("Found abstract section.")
            abstract_span = abstract_section.find('span', class_='xplmathjax')
            if abstract_span:
                print("Found abstract span.")
                return abstract_span.get_text(strip=True)
            else:
                print("Abstract span not found.")
                return "Abstract content not found."
        else:
            print("Abstract section not found.")
            return "Abstract section not found."
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return f"Error: {str(e)}"

# 定义抓取 SpringerLink 摘要的函数
def get_springer_abstract(url):
    try:
        response = session.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找摘要的 <section id="Abs1"> 元素
        abstract_section = soup.find('section', {'id': 'Abs1'})
        if abstract_section:
            full_abstract = abstract_section.get_text(strip=True)
            return full_abstract
        else:
            return "Abstract content not found."
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return f"Error: {str(e)}"

# 处理不同平台的函数，使用类似 switch-case 的方式
def get_abstract(url):
    # 定义映射关系 (类似于 switch-case)
    platforms = {
        # '10.1145': get_acm_abstract,
        # '10.1109': get_ieee_abstract,
        '10.1007': get_springer_abstract  # SpringerLink
    }

    # 判断 URL 并调用相应的函数
    for key, func in platforms.items():
        if key in url:
            # 随机等待以避免被封禁，模拟真实用户行为
            time.sleep(random.uniform(0, 1))
            return func(url)
    
    return "None"

# 读取 Excel 文件并抓取摘要
def process_excel(file_path):
    df = pd.read_excel(file_path)

    # 使用 tqdm 显示进度条
    abstracts = []
    for link in tqdm(df['link'], desc="Processing Links", ncols=100):
        abstract = get_abstract(link)
        abstracts.append(abstract)

        # 输出成功抓取的链接和摘要
        if abstract != "None":
            print(f"Successfully retrieved abstract for: {link}")
            print(f"Abstract: {abstract[:150]}...")  # 只输出前150个字符，防止摘要过长
        else:
            print(f"Skipped (non-supported link): {link}")

    # 新增 'abstract' 列
    df['abstract'] = abstracts

    # 将结果保存为 CSV 文件
    output_path = file_path.replace(".xlsx", "_with_abstracts.csv")
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Processed file saved to: {output_path}")

# 主函数入口
if __name__ == "__main__":
    # 示例文件路径
    file_path = 'datas/dblp_papers_search_results_archive.xlsx'
    process_excel(file_path)

    # 执行 unittest
    # unittest.main()