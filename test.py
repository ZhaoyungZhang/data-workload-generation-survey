'''
Author: ZhaoyangZhang
Date: 2024-10-18 21:08:30
LastEditors: Do not edit
LastEditTime: 2024-10-22 17:32:34
FilePath: /findPapers/test.py
'''
# 主函数，只调用merge功能
from merge import merge_ieee_data
from ieee_search import search_ieee_articles


# 调用merge功能
# merge_ieee_data('datas/updated_papers_with_ieee.csv', 'datas/merged_papers.csv')

search_ieee_articles('datas/dblp_papers_deduplicated_with_new_id.csv', 'datas/updated_papers_with_ieee.csv', start_id=66)

# search_papers()