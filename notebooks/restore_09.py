import json

with open('09_unified_classifier_comparison.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

fe_code = """print("Computing behavioral features...")
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()

# 1. sentiment_extreme
def get_sentiment(text):
    return analyzer.polarity_scores(str(text))['compound']
df['sentiment_score'] = df['clean_review_text'].fillna("").apply(get_sentiment)
df['sentiment_extreme'] = df['sentiment_score'].abs()

# 2. hyperbolic_ratio
def hyperbolic_ratio(text):
    text = str(text)
    words = text.split()
    if not words: return 0.0
    exc = text.count('!')
    caps = sum(1 for w in words if w.isupper() and len(w) > 1)
    return (exc + caps) / len(words)
df['hyperbolic_ratio'] = df['review_text'].fillna("").apply(hyperbolic_ratio)

# 3. repetition_ratio
def repetition_ratio(text):
    words = str(text).split()
    if not words: return 0.0
    return 1 - (len(set(words)) / len(words))
df['repetition_ratio'] = df['clean_review_text'].fillna("").apply(repetition_ratio)

# 4. user_review_frequency
if 'review_date' not in df.columns:
    df['review_date'] = pd.to_datetime(df['reviewTime'])
else:
    df['review_date'] = pd.to_datetime(df['review_date'])
df['user_first_review'] = df.groupby('user_id')['review_date'].transform('min')
df['days_active'] = (df['review_date'] - df['user_first_review']).dt.days + 1
df['user_review_frequency'] = df.groupby('user_id')['user_id'].transform('count') / df['days_active']

# 5. burst_indicator
threshold = df['daily_count'].mean() + df['daily_count'].std()
df['burst_indicator'] = (df['daily_count'] > threshold).astype(int)

# 6. review_density
df['product_first_review'] = df.groupby('product_id')['review_date'].transform('min')
df['days_since_first_review'] = (df['review_date'] - df['product_first_review']).dt.days
df['review_density'] = df.groupby('product_id')['product_id'].transform('count') / (df['days_since_first_review'] + 1)

print("Feature engineering complete.")
print("Shape after feature engineering:", df.shape)"""

new_md_cell = {
    'cell_type': 'markdown',
    'id': 'fe_behavioral',
    'metadata': {},
    'source': ['### 2.0 Feature Engineering (Behavioral Features)']
}

new_code_cell = {
    'cell_type': 'code',
    'execution_count': None,
    'id': 'fe_behavioral_code',
    'metadata': {},
    'outputs': [],
    'source': [line + '\n' for line in fe_code.split('\n')]
}
new_code_cell['source'][-1] = new_code_cell['source'][-1].strip()

# Change data loading cell back to read trust_scored_dataset.csv
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if 'read_csv' in source:
            if 'featured_dataset.csv' in source:
                cell['source'] = [line + '\n' for line in source.replace('featured_dataset.csv', 'trust_scored_dataset.csv').split('\n')]
                cell['source'][-1] = cell['source'][-1].strip()

# Insert the new cell
insert_idx = -1
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown' and len(cell.get('source', [])) > 0 and '2.1 Filter' in cell['source'][0]:
        insert_idx = i
        break

if insert_idx != -1:
    already_there = False
    for cell in nb['cells']:
        if 'Computing behavioral features...' in ''.join(cell.get('source', [])):
            already_there = True
    if not already_there:
        nb['cells'].insert(insert_idx, new_code_cell)
        nb['cells'].insert(insert_idx, new_md_cell)

# Modify X_numeric definition
new_x_numeric = """# Text feature
X_text = df_filtered["review_text"].astype(str)

# Numeric trust signals

num_feature_names = [
    "review_length",
    "rating_deviation",
    "sentiment_extreme",
    "hyperbolic_ratio",
    "repetition_ratio",
    "user_review_frequency",
    "burst_indicator",
    "review_density"
]

X_numeric = df_filtered[num_feature_names]

# Target
y = df_filtered["fake_label"]

print("Text samples:", len(X_text))
print("Numeric features:", X_numeric.shape)"""

# Find the cell that defines X_numeric
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source_str = "".join(cell.get('source', []))
        if 'X_numeric = df_filtered' in source_str:
            cell['source'] = [line + '\n' for line in new_x_numeric.split('\n')]
            cell['source'][-1] = cell['source'][-1].strip()
            break

with open('09_unified_classifier_comparison.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Notebook updated successfully.")
