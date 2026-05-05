"""
Migrate CSV data to database
Converts existing CSV files to SQLite/PostgreSQL database
"""

import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager

def migrate_data():
    """Migrate CSV data to database"""
    
    print("=" * 80)
    print("MIGRATING CSV DATA TO DATABASE")
    print("=" * 80)
    
    # Initialize database
    print("\n1. Initializing database...")
    db = DatabaseManager(db_type='sqlite', db_path='database/reviews.db')
    
    # Initialize schema
    print("\n2. Creating database schema...")
    if not db.initialize_schema('database/schema.sql'):
        print("Failed to initialize schema")
        return
    
    # Load product metadata
    print("\n3. Loading product metadata...")
    try:
        products_meta = pd.read_csv('demo/product_metadata.csv')
        print(f"   Loaded {len(products_meta)} products from metadata")
    except Exception as e:
        print(f"   Error loading metadata: {e}")
        products_meta = pd.DataFrame()
    
    # Load product trust scores
    print("\n4. Loading product trust scores...")
    try:
        products_scores = pd.read_csv('data/processed/product_trust_scores.csv')
        print(f"   Loaded {len(products_scores)} products from trust scores")
    except Exception as e:
        print(f"   Error loading trust scores: {e}")
        products_scores = pd.DataFrame()
    
    # Merge product data
    print("\n5. Merging product data...")
    if len(products_meta) > 0 and len(products_scores) > 0:
        products = products_scores.merge(
            products_meta,
            on='product_id',
            how='left'
        )
        
        # Fill missing values
        products['product_name'] = products['product_name'].fillna('Unknown Product')
        products['category'] = products['category'].fillna('Fashion')
        products['brand'] = products['brand'].fillna('Unknown Brand')
        products['price'] = products['price'].fillna('N/A')
        products['image_url'] = products['image_url'].fillna('')
        products['description'] = products['description'].fillna('')
        
        print(f"   Merged data for {len(products)} products")
    else:
        products = products_scores if len(products_scores) > 0 else products_meta
    
    # Insert products
    print("\n6. Inserting products into database...")
    try:
        count = db.bulk_insert_products(products)
        print(f"   Inserted {count} products")
    except Exception as e:
        print(f"   Error inserting products: {e}")
    
    # Load reviews
    print("\n7. Loading reviews...")
    try:
        reviews = pd.read_csv('data/processed/reviews_sample.csv')
        print(f"   Loaded {len(reviews)} reviews")
        
        # Ensure required columns
        if 'predicted_trust_score' not in reviews.columns:
            reviews['predicted_trust_score'] = reviews['trust_score']
        
        # Insert reviews
        print("\n8. Inserting reviews into database...")
        count = db.bulk_insert_reviews(reviews)
        print(f"   Inserted {count} reviews")
        
    except Exception as e:
        print(f"   Error with reviews: {e}")
    
    # Verify migration
    print("\n9. Verifying migration...")
    stats = db.get_system_statistics()
    print(f"   Total products in DB: {stats['total_products']}")
    print(f"   Total reviews in DB: {stats['total_reviews']}")
    print(f"   Average trust score: {stats['avg_trust_score']:.3f}")
    print(f"   Verified reviews: {stats['verified_reviews']}")
    print(f"   High trust reviews: {stats['high_trust_reviews']}")
    
    # Close connection
    db.close()
    
    print("\n" + "=" * 80)
    print("MIGRATION COMPLETE!")
    print("=" * 80)
    print(f"\nDatabase location: database/reviews.db")
    print(f"Database size: {os.path.getsize('database/reviews.db') / (1024*1024):.2f} MB")
    print("\nYou can now use the database in your application!")

if __name__ == "__main__":
    migrate_data()
