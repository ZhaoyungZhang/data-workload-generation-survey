'''
Author: ZhaoyangZhang
Date: 2024-10-20 12:46:54
LastEditors: Do not edit
LastEditTime: 2024-10-28 14:14:38
FilePath: /findPapers/filter_papers.py
'''
import pandas as pd
import re
from tqdm import tqdm

# Define a function to generate regex pattern from a keyword
def generate_pattern_from_keyword(keyword):
    # Generalize "generate" to match generate, generating, generated, etc.
    keyword = keyword.replace('generate', r'generat\w*')
    # Generalize "query" to match both "query" and "queries"
    keyword = keyword.replace('query', r'quer(?:y|ies)')
    # Generalize "workload" to match "workload" and "workloads"
    keyword = keyword.replace('workload', r'workload(?:s|)')
    # Allow optional plural forms for "database/databases"
    keyword = keyword.replace('database', r'databases?')
    # Generalize "synthesize" to match "synthesize", "synthesizing", etc.
    keyword = keyword.replace('synthesize', r'synthes\w*')
    # Add word boundaries to match specific phrases like "database generator"
    keyword = keyword.replace('database generator', r'database(?:s)? generat\w*')
    keyword = keyword.replace('cardinality constraint', r'cardinality constraint(?:s|)')
    # For "generate xxx database", where "xxx" is a single word
    keyword = keyword.replace('generate database', r'generat\w* \w+ databases?')
    # Strictly limit "generate xxx queries" format, only allowing one word between them
    keyword = keyword.replace('generate queries', r'\bgenerat\w* (\w+\s){0,2}quer(?:y|ies)\b')
    
    # Return the regex pattern with word boundaries to avoid partial matches
    return rf'\b{keyword}\b'


# Load relevance keywords from CSV files
def load_keywords(file_path):
    # Load the keywords CSV and extract the 'Keyword' column, convert to lowercase
    keywords_df = pd.read_csv(file_path)
    return set(keywords_df['Keyword'].str.lower().dropna())

# Load keywords for relevance 0 and 1, including the additional ones
print("Loading keywords from CSV files...")

# Load irrelevant keywords
irrelevant_keywords = load_keywords('outputs/filter_5/keywords_relevance_0.csv')
irrelevant_keywords_addition = load_keywords('outputs/filter_5/keywords_relevance_0_addition.csv')

# Combine irrelevant keywords with additions
irrelevant_keywords.update(irrelevant_keywords_addition)

# Load relevant keywords
relevant_keywords = load_keywords('outputs/filter_5/keywords_relevance_1.csv')
relevant_keywords_addition = load_keywords('outputs/filter_5/keywords_relevance_1_addition.csv')

# Combine relevant keywords with additions
relevant_keywords.update(relevant_keywords_addition)

# Generate regex patterns from relevant keywords
print("Generating regex patterns from relevant keywords...")
relevant_patterns = [generate_pattern_from_keyword(keyword) for keyword in relevant_keywords]

# Load papers data from the DBLP file
print("Loading DBLP papers data...")
papers_data = pd.read_csv('datas/survery_paper_list_full_abstract.csv', encoding='utf-8')

# Remove duplicate papers based on the 'paper_title' column
print("Removing duplicates based on paper title...")
papers_data_deduped = papers_data.drop_duplicates(subset='paper_title', keep='first')

# Function to filter papers based on keywords in titles + abstracts
def filter_papers(papers_df, irrelevant_keywords, relevant_patterns):
    irrelevant_papers = []
    relevant_papers = []
    unfiltered_papers = []

    # Iterate through the papers using tqdm to show progress
    for _, row in tqdm(papers_df.iterrows(), total=len(papers_df)):
        # Combine paper title and abstract for filtering
        text_to_check = f"{str(row['paper_title']).lower().strip()} {str(row['abstract']).lower().strip()}"

        # Initialize reason
        row['reason'] = 'checked title + abstract'

        # Create a list to store details about matches
        match_details = []

        # Check for irrelevant keywords
        for keyword in irrelevant_keywords:
            if keyword in text_to_check:
                match_details.append(f"matched irrelevant keyword: '{keyword}' in text")

        # Check for relevant patterns using re.finditer() to capture the matching text
        for pattern in relevant_patterns:
            for match in re.finditer(pattern, text_to_check):
                matched_text = match.group()
                match_details.append(f"matched relevant pattern: '{pattern}' with text: '{matched_text}'")

        # If any irrelevant keywords are matched, classify as irrelevant
        if any(keyword in text_to_check for keyword in irrelevant_keywords):
            row['reason'] += f", {', '.join([detail for detail in match_details if 'irrelevant' in detail])}"
            irrelevant_papers.append(row)
        # If relevant patterns are matched, classify as relevant
        elif any(re.search(pattern, text_to_check) for pattern in relevant_patterns):
            row['reason'] += f", {', '.join([detail for detail in match_details if 'relevant' in detail])}"
            relevant_papers.append(row)
        # If neither relevant nor irrelevant, classify as unfiltered
        else:
            row['reason'] += ', no keywords matched'
            unfiltered_papers.append(row)

    return pd.DataFrame(irrelevant_papers), pd.DataFrame(relevant_papers), pd.DataFrame(unfiltered_papers)

# Filter the papers
print("Filtering papers based on keywords and patterns...")
irrelevant_papers, relevant_papers, unfiltered_papers = filter_papers(
    papers_data_deduped, irrelevant_keywords, relevant_patterns
)

# Specify the columns to keep (assuming you want all original columns plus 'reason')
columns_to_keep = ['ID', 'topic', 'paper_title', 'conference_year', 'conference', 'authors', 'link', 'abstract', 'reason']

# Remove unnecessary columns before saving
irrelevant_papers_filtered = irrelevant_papers[columns_to_keep]
relevant_papers_filtered = relevant_papers[columns_to_keep]
unfiltered_papers_filtered = unfiltered_papers[columns_to_keep]

# Save the results to CSV files
print("Saving filtered results...")
irrelevant_papers_filtered.to_csv('outputs/filter_5/irrelevant_papers.csv', index=False, encoding='utf-8')
relevant_papers_filtered.to_csv('outputs/filter_5/relevant_papers.csv', index=False, encoding='utf-8')
unfiltered_papers_filtered.to_csv('outputs/filter_5/unfiltered_papers.csv', index=False, encoding='utf-8')

print("Filtering completed. Files saved to 'outputs/' folder.")
