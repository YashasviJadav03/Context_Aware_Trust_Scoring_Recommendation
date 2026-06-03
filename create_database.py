"""
Create SQLite database from reviews and products data
This will be MUCH faster than reading CSVs or JSON
"""

import pandas as pd
import sqlite3
import json
import gzip
from tqdm import tqdm

def create_database():
    print("Creating SQLite database...")
    
    # Connect to database
    conn = sqlite3.connect('data/processed/reviews.db')
    cursor = conn.cursor()
    
    # Create tables with indexes
    print("Creating tables...")
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            review_count INTEGER,
            avg_rating REAL,
            rating_std REAL,
            score_raw_avg REAL,
            score_count_weighted REAL,
            score_trust_weighted REAL
        )
    ''')
    
    # Reviews table with index on product_id for fast lookups
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            review_text TEXT,
            rating REAL,
            verified INTEGER,
            trust_score REAL,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')
    
    # Create index for fast product_id lookups
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_id ON reviews(product_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_trust_score ON reviews(trust_score)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_rating ON reviews(rating)')
    
    conn.commit()
    
    # Load products
    print("Loading products...")
    products_df = pd.read_csv('data/processed/product_trust_scores.csv')
    products_df.to_sql('products', conn, if_exists='replace', index=False)
    
    # Load reviews from full dataset
    print("Loading reviews from full dataset (this may take a few minutes)...")
    
    # First, try to load from reviews_sample to get trust scores
    reviews_sample = pd.read_csv('data/processed/reviews_sample.csv')
    
    # Create a lookup for trust scores
    trust_lookup = {}
    for _, row in reviews_sample.iterrows():
        key = (row['product_id'], row['review_text'][:100])  # Use first 100 chars as key
        trust_lookup[key] = row['trust_score']
    
    # Now load full reviews
    reviews_data = []
    count = 0
    
    with open('data/raw/AMAZON_FASHION.json', 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="Processing reviews"):
            try:
                review = json.loads(line.strip())
                product_id = review.get('asin')
                review_text = review.get('reviewText', '')
                
                # Try to get trust score from sample
                key = (product_id, review_text[:100])
                trust_score = trust_lookup.get(key, 0.5)  # Default 0.5 if not in sample
                
                reviews_data.append({
                    'product_id': product_id,
                    'review_text': review_text,
                    'rating': review.get('overall', 0),
                    'verified': 1 if review.get('verified', False) else 0,
                    'trust_score': trust_score
                })
                
                count += 1
                
                # Batch insert every 10000 rows for performance
                if count % 10000 == 0:
                    df_batch = pd.DataFrame(reviews_data)
                    df_batch.to_sql('reviews', conn, if_exists='append', index=False)
                    reviews_data = []
                    print(f"Inserted {count} reviews...")
                    
            except Exception as e:
                continue
    
    # Insert remaining reviews
    if reviews_data:
        df_batch = pd.DataFrame(reviews_data)
        df_batch.to_sql('reviews', conn, if_exists='append', index=False)
    
    print(f"Total reviews inserted: {count}")
    
    # Optimize database
    print("Optimizing database...")
    cursor.execute('VACUUM')
    cursor.execute('ANALYZE')
    
    conn.commit()
    conn.close()
    
    print("✅ Database created successfully!")
    print(f"Location: data/processed/reviews.db")
    
    # Show stats
    conn = sqlite3.connect('data/processed/reviews.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM reviews')
    review_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM products')
    product_count = cursor.fetchone()[0]
    
    print(f"\n📊 Database Statistics:")
    print(f"  Products: {product_count:,}")
    print(f"  Reviews: {review_count:,}")
    
    conn.close()

if __name__ == "__main__":
    create_database()
