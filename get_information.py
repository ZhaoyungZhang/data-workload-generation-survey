'''
Author: ZhaoyangZhang
Date: 2024-10-20 16:25:20
LastEditors: Do not edit
LastEditTime: 2024-10-22 10:14:21
FilePath: /findPapers/get_information.py
'''
import requests
import re
from bs4 import BeautifulSoup


def single_information(airtcle_number):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 '
                      'Safari/537.36 Edg/108.0.1462.46 '
    }
    url = 'https://ieeexplore.ieee.org/document/' + str(airtcle_number)
    params = {
    }
    res = requests.get(url=url, params=params, headers=headers)
    page_text = res.text
    return page_text

def get_springer_information(doi_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }
    res = requests.get(doi_url, headers=headers)
    page_text = res.text
    return page_text

def get_springer_abstract(page_text):
    soup = BeautifulSoup(page_text, 'html.parser')
    abstract_section = soup.find('section', {'id': 'Abs1'})  # This is based on Springer Link's HTML structure.
    if abstract_section:
        abstract = abstract_section.text.strip()
        return abstract
    return "Abstract not found"

def get_title(page_text):
    ex = '"title":"(.+?)"'
    article_title = re.findall(ex, page_text, re.S)
    for title in article_title:
        if title != 'true' and title != 'false':
            return title.replace("<inf>", "").replace("</inf>", "")


def get_abstract(page_text):
    ex = '"abstract":"(.+?)",'
    article_abstract = re.findall(ex, page_text, re.S)
    for abstract in article_abstract:
        if abstract != 'true' and abstract != 'false':
            return abstract


def get_published(page_text):
    ex = '"publicationTitle":"(.+?)"'
    article_published = re.findall(ex, page_text, re.S)
    for published in article_published:
        if published != 'true' and published != 'false':
            return published


def get_date(page_text):
    ex = '"insertDate":"(.+?)"'
    article_date = re.findall(ex, page_text, re.S)
    for date in article_date:
        if date != 'true' and date != 'false':
            return date


def get_kwd(page_text):
    ex = '"type":"IEEE Keywords","kwd":(.+?)}'
    article_kwd = re.findall(ex, page_text, re.S)
    for kwd in article_kwd:
        if kwd != 'true' and kwd != 'false':
            return kwd.replace('[', '').replace(']', '')

