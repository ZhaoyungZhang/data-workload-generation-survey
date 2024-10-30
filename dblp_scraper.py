import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm
import os

# 配置重试策略，处理网络错误和 SSL 握手错误
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

# 配置重试策略，处理网络错误和 SSL 握手错误
def configure_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

# 初始化 CSV 文件
def initialize_csv(filename):
    df = pd.DataFrame(columns=["ID", "topic", "paper_title", "conference_year", "conference", "authors", "link"])
    df.to_csv(filename, index=False, encoding="utf-8")

# 实时保存找到的论文到 CSV
def save_to_csv(filename, results):
    file_exists = os.path.isfile(filename)  # 检查文件是否已经存在
    df = pd.DataFrame(results)
    df.to_csv(filename, mode='a', header=False, index=False, encoding="utf-8")

# 生成查询 URL（关键词用下划线连接，表示 AND）
def generate_search_url(keyword, conference):
    search_keyword = f"{keyword.replace(' ', '_')}_{conference}"
    return f"https://dblp.org/search?q={search_keyword}"

def extract_year(entry):
    """从条目中提取论文年份."""
    year_element = entry.find("span", {"itemprop": "datePublished"})
    if year_element:
        return year_element.text.strip()
    return "Unknown"

def extract_authors(entry):
    """从条目中提取作者列表，确保只提取作者而不包含标题。"""
    authors = entry.select('span[itemprop="author"] span[itemprop="name"]')
    return ", ".join([author.text.strip() for author in authors])


def extract_link(entry):
    """从条目中提取论文链接."""
    link_element = entry.select_one("li.ee a[itemprop='url']")
    return link_element['href'] if link_element else "No Link Available"

def search_and_save(session, keywords, conferences, year_range, target_count, csv_filename):
    all_results = []
    paper_id = 1  # 论文 ID 计数器
    total_combinations = len(keywords) * len(conferences)

    with tqdm(total=total_combinations, desc="Searching", ncols=100) as pbar:
        for keyword in keywords:
            for conference in conferences:
                search_url = generate_search_url(keyword, conference)
                print(f"\n[INFO] 正在搜索：{search_url}")

                try:
                    response = session.get(search_url, timeout=5)
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    print(f"[WARNING] 请求失败：{e}")
                    print(f"[INFO] 请求失败，暂停几秒后重试...")
                    time.sleep(random.uniform(2, 3))  # 仅在失败时等待一段随机时间
                    pbar.update(1)
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                entries = soup.select("li.entry")
                print(f"[INFO] 匹配条目数：{len(entries)}")

                results = []
                for entry in entries:
                    paper_title = entry.select_one(".title").text if entry.select_one(".title") else "No Title"
                    conference_year = extract_year(entry)
                    authors = extract_authors(entry)
                    link = extract_link(entry)

                    if conference_year != "Unknown" and conference_year not in year_range:
                        print(f"[DEBUG] 过滤掉年份：{conference_year}")
                        continue

                    results.append({
                        "ID": paper_id,
                        "topic": f"{keyword} {conference}",
                        "paper_title": paper_title,
                        "conference_year": conference_year,
                        "conference": conference,  # 确保使用外部的 conference 变量
                        "authors": authors,
                        "link": link
                    })

                    paper_id += 1

                if results:  # 确保有结果才保存
                    save_to_csv(csv_filename, results)
                    print(f"[INFO] 已保存 {len(results)} 篇论文，当前总数：{paper_id - 1} 篇")
                else:
                    print(f"[INFO] 未找到符合条件的论文。")

                if paper_id - 1 >= target_count:
                    print("[INFO] 达到目标数量，停止爬取。")
                    pbar.close()
                    return
                pbar.update(1)


# 主函数入口
def main():
    # 定义关键词列表
    keywords = [
        "Data generat", "Data synthes", "Data augment", "Data simulat", "Data replay",
        "Database generat", "Database synthes", "Database augment", "Database simulat", "Database replay",
        "Table generat", "Table synthes", "Table augment", "Tabular data generat", 
        "Tabular data synthes", "Tabular data augment", "Query generat", "Query synthes",
        "Query augment", "Query simulat", "Query replay", "Workload generat", 
        "Workload synthes", "Workload augment", "Workload simulat", "Workload replay",
        "Benchmark generat", "Benchmark synthes", "Benchmark augment", "Benchmark simulat", 
        "Benchmark replay"
    ]

    # 定义会议和期刊列表
    conferences_journals = [
        "SIGMOD", "VLDB", "ICDE", "CIDR", "DASFAA", "SIGKDD", 
        "TODS", "TOIS", "TKDE", "VLDBJ",
        "PLDI", "POPL", "FSE", "SOSP", "OOPSLA", "ASE", "ICSE", "ISSTA", "OSDI",
        "TOPLAS", "TOSEM", "TSE", "TSC", "FSE", "JACM", "Proc.IEEE", "SCIS"
    ]

    year_range = list(map(str, range(2004, 2025)))
    target_count = 2000
    csv_filename = "dblp_papers_search_results.csv"

    # 初始化 CSV 文件
    initialize_csv(csv_filename)

    # 配置网络会话
    session = configure_session()

    # 执行搜索并保存结果
    search_and_save(session, keywords, conferences_journals, year_range, target_count, csv_filename)

    print(f"[INFO] CSV 文件已生成：{csv_filename}")

# 如果当前模块是主程序，则执行 main()
if __name__ == "__main__":
    main()