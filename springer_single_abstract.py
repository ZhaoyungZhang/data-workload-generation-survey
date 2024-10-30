'''
Author: ZhaoyangZhang
Date: 2024-10-19 11:49:19
LastEditors: Do not edit
LastEditTime: 2024-10-22 18:00:04
FilePath: /findPapers/springer_single_abstract.py
'''
import requests
from bs4 import BeautifulSoup

def get_full_abstract(doi_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }
    
    response = requests.get(doi_url, headers=headers)
    
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

# 输入 DOI 页面链接
doi_url = "https://doi.org/10.1007/978-3-030-93663-1_12"
# 手动输入doi
doi_url = input("Enter the DOI URL: ")
abstract = get_full_abstract(doi_url)
print(abstract)