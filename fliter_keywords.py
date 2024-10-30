'''
Author: ZhaoyangZhang
Date: 2024-10-18 20:13:48
LastEditors: Do not edit
LastEditTime: 2024-10-20 12:48:41
FilePath: /findPapers/fliter_keywords.py
'''
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

# Load CSV file and skip problematic lines with the new parameter
file_path = 'datas/sample_labeled_papers.csv'
data = pd.read_csv(file_path, encoding='ISO-8859-1', on_bad_lines='skip', delimiter='\t', engine='python')

# Separate the keywords based on relevance
data_cleaned = data[['Relevance', 'Keywords']].dropna()

# Function to split keywords by ',' while keeping full phrases intact
def split_keywords(kw_series):
    keywords = kw_series.str.split(',').apply(lambda x: [keyword.strip().lower() for keyword in x if keyword.strip()])
    return keywords.explode().dropna()

# Function to count keyword frequency
def count_keyword_frequency(keywords):
    return dict(Counter(keywords))

# Split keywords into relevance = 0 and relevance = 1
keywords_relevance_0 = split_keywords(data_cleaned[data_cleaned['Relevance'] == 0]['Keywords'])
keywords_relevance_1 = split_keywords(data_cleaned[data_cleaned['Relevance'] == 1]['Keywords'])

# Calculate the keyword frequencies for both relevance categories
keyword_freq_0 = count_keyword_frequency(keywords_relevance_0)
keyword_freq_1 = count_keyword_frequency(keywords_relevance_1)

# Save keyword frequencies to CSV files
pd.DataFrame(list(keyword_freq_0.items()), columns=['Keyword', 'Frequency']).to_csv('outputs/keywords_relevance_0.csv', index=False)
pd.DataFrame(list(keyword_freq_1.items()), columns=['Keyword', 'Frequency']).to_csv('outputs/keywords_relevance_1.csv', index=False)

# Function to create and display a word cloud
def create_wordcloud(keywords, title, filename):
    text = ', '.join(keywords)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    plt.savefig(filename)
    plt.show()

# Create word clouds for both relevance categories
if not keywords_relevance_0.empty:
    create_wordcloud(keywords_relevance_0, 'Word Cloud for Relevance = 0 (Unrelated)', 'outputs/wordcloud_relevance_0.png')

if not keywords_relevance_1.empty:
    create_wordcloud(keywords_relevance_1, 'Word Cloud for Relevance = 1 (Related)', 'outputs/wordcloud_relevance_1.png')
