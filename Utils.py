import pandas as pd

def csv_to_excel(csv_filename, excel_filename):
    # 读取CSV文件
    try:
        df = pd.read_csv(csv_filename)
    except FileNotFoundError:
        print(f"[ERROR] 找不到文件: {csv_filename}")
        return

    # 创建一个Excel文件并将数据写入其中
    try:
        with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Papers')
        print(f"[INFO] 成功将 {csv_filename} 写入 {excel_filename}")
    except Exception as e:
        print(f"[ERROR] 写入Excel文件时出错: {e}")

def sample_papers(input_csv='dblp_papers_search_results_archive.csv', output_xlsx='sampled_papers.xlsx', sample_ratio=0.15):
    # 读取 CSV 文件
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"[ERROR] 找不到文件: {input_csv}")
        return

    # 打印总数和进行采样
    total_papers = len(df)
    print(f"[INFO] 总共有 {total_papers} 篇论文")

    # 随机采样 15%
    sampled_df = df.sample(frac=sample_ratio, random_state=42)
    print(f"[INFO] 采样了 {len(sampled_df)} 篇论文")

    # 将采样的结果保存为 Excel
    sampled_df.to_excel(output_xlsx, index=False, encoding='utf-8')
    print(f"[INFO] 采样结果已保存到 {output_xlsx}")

if __name__ == "__main__":
    # 文件名定义
    csv_filename = 'dblp_papers_search_results_archive2.csv'  # 你之前生成的CSV文件
    excel_filename = 'dblp_papers_search_results_archive.xlsx'  # 转换后的Excel文件名

    # 执行转换
    # csv_to_excel(csv_filename, excel_filename)

    sample_papers("dblp_papers_search_results_archive2.csv")