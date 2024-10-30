'''
Author: ZhaoyangZhang
Date: 2024-10-20 20:59:33
LastEditors: Do not edit
LastEditTime: 2024-10-22 09:59:22
FilePath: /findPapers/ieee_search.py
'''
import csv
from get_articlelist import airtcle_list
from get_information import single_information, get_title, get_abstract, get_springer_information, get_springer_abstract
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import requests

# 创建带有重试机制的session
def create_session():
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    return session

# 文章搜索功能
def search_ieee_articles(input_file, output_file, start_id=None):
    session = create_session()

    with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_file, mode='a', newline='', encoding='utf-8') as outfile:  # 使用 'a' 模式来追加写入

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['IEEE_Search_Index']  # 添加新的索引列
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        if outfile.tell() == 0:
            writer.writeheader()

        for row in reader:
            current_id = int(row['ID'])
            if start_id and current_id < start_id:
                continue

            if "10.1109" in row['link']:
                searchword = row['paper_title'].rstrip('.')
                Airtcle_List = airtcle_list(searchword)

                exact_match = None
                if Airtcle_List:
                    for article_number in Airtcle_List:
                        page_text = single_information(article_number)
                        title = get_title(page_text)
                        if title.lower() == searchword.lower():
                            exact_match = (title, get_abstract(page_text))
                            break
                    if exact_match:
                        row['IEEE_Search_Index'] = f"{exact_match[0]}: {exact_match[1]}"
                    else:
                        row['IEEE_Search_Index'] = f"{title}: {get_abstract(page_text)}"
                else:
                    row['IEEE_Search_Index'] = "No results found"
            else:
                row['IEEE_Search_Index'] = "Not an IEEE article"

            writer.writerow(row)

    print("Finished updating the CSV file!")


def search_papers(input_file, output_file, start_id=None):
    session = create_session()

    with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_file, mode='a', newline='', encoding='utf-8') as outfile:  

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['Search_Index']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        if outfile.tell() == 0:
            writer.writeheader()

        for row in reader:
            current_id = int(row['ID'])
            if start_id and current_id < start_id:
                continue

            if "10.1007" in row['link']:  # Checking for Springer DOI
                doi_url = row['link']
                page_text = get_springer_information(doi_url)
                abstract = get_springer_abstract(page_text)
                row['Search_Index'] = f"{row['paper_title']}: {abstract}"

            elif "10.1109" in row['link']:  # This is for IEEE
                searchword = row['paper_title'].rstrip('.')
                Airtcle_List = airtcle_list(searchword)

                exact_match = None
                if Airtcle_List:
                    for article_number in Airtcle_List:
                        page_text = single_information(article_number)
                        title = get_title(page_text)
                        if title.lower() == searchword.lower():
                            exact_match = (title, get_abstract(page_text))
                            break
                    if exact_match:
                        row['Search_Index'] = f"{exact_match[0]}: {exact_match[1]}"
                    else:
                        row['Search_Index'] = f"{title}: {get_abstract(page_text)}"
                else:
                    row['Search_Index'] = "No results found"
            else:
                row['Search_Index'] = "Not a supported article"

            writer.writerow(row)

    print("Finished updating the CSV file!")
