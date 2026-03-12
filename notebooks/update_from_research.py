import json

# ========================
# Update 06_feature_engineering.ipynb
# ========================
with open('06_feature_engineering.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

new_cells = []
for cell in nb['cells']:
    
    # 1. Fix trust_score target issue
    if cell['cell_type'] == 'code' and "y = df['trust_score']" in ''.join(cell.get('source', [])):
        cell['source'] = [line.replace("df['trust_score']", "df['fake_label']") for line in cell['source']]
    
    # Update structured_features variable to include all new features
    if cell['cell_type'] == 'code' and 'structured_features = df[' in ''.join(cell.get('source', [])):
        new_source = """structured_features = df[
    [
        # NLP
        "review_length_log",
        "unique_word_ratio",
        "sentiment_score",
        "sentiment_extreme",
        "repetition_ratio",
        "hyperbolic_ratio",
        "exclamation_count",
        "question_count",

        # rating context
        "rating_deviation",

        # user behaviour
        "user_review_count",
        "user_rating_variance",
        "user_extreme_ratio",
        "user_review_frequency",
        "user_product_diversity",

        # product context
        "product_review_count",
        "product_rating_std",
        "product_popularity_log",
        "product_user_diversity",

        # temporal
        "days_since_first_review",
        "review_density",
        "review_time_gap",
        "burst_indicator"
    ]
]

structured_features.head()"""
        cell['source'] = [line + '\n' for line in new_source.split('\n')]
        cell['source'][-1] = cell['source'][-1].strip()

    # Pre-insert sections before Select Structured Features
    if cell['cell_type'] == 'markdown' and '## Select Structured Features' in ''.join(cell.get('source', [])):
        
        # Unique Word Ratio
        new_cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': ['### Unique Word Ratio\n']})
        new_cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': [
            "def unique_word_ratio(text):\n",
            "    words = str(text).split()\n",
            "    if len(words) == 0:\n",
            "        return 0\n",
            "    return len(set(words)) / len(words)\n",
            "\n",
            "df['unique_word_ratio'] = df['clean_review'].apply(unique_word_ratio)\n"
        ]})
        
        # Punctuation & Log length
        new_cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': ['### Punctuation & Log Length\n']})
        new_cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': [
            "import numpy as np\n",
            "df['exclamation_count'] = df['clean_review'].str.count('!').fillna(0)\n",
            "df['question_count'] = df['clean_review'].str.count(r'\\\\?').fillna(0)\n",
            "df['review_length_log'] = np.log1p(df['review_length'])\n"
        ]})
        
        # Behavioral Extensions
        new_cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': ['### Behavioral Extensions\n']})
        new_cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': [
            "df['extreme_rating'] = df['rating'].isin([1,5]).astype(int)\n",
            "df['user_extreme_ratio'] = df.groupby('user_id')['extreme_rating'].transform('mean')\n",
            "\n",
            "df['user_daily_reviews'] = df.groupby(['user_id','review_day'])['user_id'].transform('count')\n",
            "df['user_burst_flag'] = (df['user_daily_reviews'] > 3).astype(int)\n"
        ]})
        
        # Product Extensions
        new_cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': ['### Product Extensions\n']})
        new_cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': [
            "df['product_rating_std'] = df.groupby('product_id')['rating'].transform('std').fillna(0)\n",
            "df['product_popularity_log'] = np.log1p(df['product_review_count'])\n"
        ]})
        
        # Temporal Extensions
        new_cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': ['### Temporal Extensions\n']})
        new_cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': [
            "df = df.sort_values(['product_id','review_date'])\n",
            "df['prev_review_time'] = df.groupby('product_id')['review_date'].shift(1)\n",
            "df['review_time_gap'] = (df['review_date'] - df['prev_review_time']).dt.days.fillna(0)\n"
        ]})
        
        # Graph / Diversity Extensions
        new_cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': ['### Graph / Diversity Extensions\n']})
        new_cells.append({'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': [
            "df['user_product_diversity'] = df.groupby('user_id')['product_id'].transform('nunique')\n",
            "df['product_user_diversity'] = df.groupby('product_id')['user_id'].transform('nunique')\n"
        ]})
        

    new_cells.append(cell)


nb['cells'] = new_cells

with open('06_feature_engineering.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print('Updated 06_feature_engineering.ipynb smoothly.')

# ========================
# Update 09_unified_classifier_comparison.ipynb
# ========================
with open('09_unified_classifier_comparison.ipynb', 'r', encoding='utf-8') as f:
    nb09 = json.load(f)

new_x_numeric = """# Text feature
X_text = df_filtered["review_text"].astype(str)

# Numeric trust signals
num_feature_names = [
    # NLP
    "review_length_log",
    "unique_word_ratio",
    "sentiment_score",
    "sentiment_extreme",
    "repetition_ratio",
    "hyperbolic_ratio",
    "exclamation_count",
    "question_count",

    # rating context
    "rating_deviation",

    # user behaviour
    "user_review_count",
    "user_rating_variance",
    "user_extreme_ratio",
    "user_review_frequency",
    "user_product_diversity",

    # product context
    "product_review_count",
    "product_rating_std",
    "product_popularity_log",
    "product_user_diversity",

    # temporal
    "days_since_first_review",
    "review_density",
    "review_time_gap",
    "burst_indicator"
]

X_numeric = df_filtered[num_feature_names]

# Target
y = df_filtered["fake_label"]

print("Text samples:", len(X_text))
print("Numeric features:", X_numeric.shape)"""

# Change x numeric loading
for cell in nb09['cells']:
    if cell['cell_type'] == 'code':
        source_str = "".join(cell.get('source', []))
        if 'X_numeric = df_filtered' in source_str:
            cell['source'] = [line + '\n' for line in new_x_numeric.split('\n')]
            cell['source'][-1] = cell['source'][-1].strip()

# Change it to read the featured dataset instead of trust scored dataset
for cell in nb09['cells']:
    if cell['cell_type'] == 'code' and 'trust_scored_dataset.csv' in ''.join(cell.get('source', [])):
        cell['source'] = [line.replace('trust_scored_dataset.csv', 'featured_dataset.csv') for line in cell['source']]


with open('09_unified_classifier_comparison.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb09, f, indent=1)

print('Updated 09_unified_classifier_comparison.ipynb smoothly.')
