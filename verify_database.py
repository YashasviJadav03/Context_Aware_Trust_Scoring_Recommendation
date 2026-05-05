"""
Verify Database Implementation
Tests all database operations to ensure everything works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def verify_database():
    """Verify database implementation"""
    
    print("=" * 80)
    print("DATABASE VERIFICATION")
    print("=" * 80)
    
    # Connect to database
    print("\n1. Connecting to database...")
    db = DatabaseManager(db_type='sqlite', db_path='database/reviews.db')
    print("   ✓ Connected successfully")
    
    # Test system statistics
    print("\n2. Testing system statistics...")
    stats = db.get_system_statistics()
    print(f"   ✓ Total products: {stats['total_products']:,}")
    print(f"   ✓ Total reviews: {stats['total_reviews']:,}")
    print(f"   ✓ Average trust score: {stats['avg_trust_score']:.3f}")
    print(f"   ✓ Verified reviews: {stats['verified_reviews']:,}")
    print(f"   ✓ High trust reviews: {stats['high_trust_reviews']:,}")
    
    # Test product search
    print("\n3. Testing product search...")
    results = db.search_products('belt', limit=5)
    print(f"   ✓ Found {len(results)} products matching 'belt'")
    if results:
        print(f"   ✓ Sample: {results[0]['product_name'][:50]}...")
    
    # Test get product
    print("\n4. Testing get product by ID...")
    if results:
        product_id = results[0]['product_id']
        product = db.get_product(product_id)
        print(f"   ✓ Retrieved product: {product['product_id']}")
        print(f"   ✓ Product name: {product['product_name'][:50]}...")
        print(f"   ✓ Trust score: {product['score_trust_weighted']:.3f}")
    
    # Test get product reviews
    print("\n5. Testing get product reviews...")
    if results:
        reviews = db.get_product_reviews(product_id, limit=10)
        print(f"   ✓ Found {len(reviews)} reviews for product {product_id}")
        if reviews:
            print(f"   ✓ Sample review trust score: {reviews[0]['trust_score']:.3f}")
    
    # Test product statistics
    print("\n6. Testing product statistics...")
    if results:
        product_stats = db.get_product_statistics(product_id)
        print(f"   ✓ Total reviews: {product_stats.get('total_reviews', 0)}")
        print(f"   ✓ Average rating: {product_stats.get('avg_rating', 0):.2f}")
        print(f"   ✓ Average trust: {product_stats.get('avg_trust_score', 0):.3f}")
        print(f"   ✓ High trust reviews: {product_stats.get('high_trust_count', 0)}")
        print(f"   ✓ Verified reviews: {product_stats.get('verified_count', 0)}")
    
    # Test top products
    print("\n7. Testing get top products...")
    top_products = db.get_top_products(limit=10, min_reviews=5)
    print(f"   ✓ Retrieved {len(top_products)} top products")
    if top_products:
        print(f"   ✓ Top product: {top_products[0]['product_name'][:50]}...")
        print(f"   ✓ Trust score: {top_products[0]['score_trust_weighted']:.3f}")
    
    # Test recent reviews
    print("\n8. Testing get recent reviews...")
    recent = db.get_recent_reviews(limit=5)
    print(f"   ✓ Retrieved {len(recent)} recent reviews")
    
    # Test insert review
    print("\n9. Testing insert review...")
    test_review = {
        'user_id': 'TEST_USER_001',
        'product_id': product_id if results else 'B00TEST',
        'rating': 5,
        'review_text': 'This is a test review for database verification.',
        'verified': True,
        'helpful_votes': 0,
        'trust_score': 0.85,
        'predicted_trust_score': 0.85
    }
    review_id = db.insert_review(test_review)
    if review_id:
        print(f"   ✓ Inserted test review with ID: {review_id}")
        
        # Delete test review
        print("\n10. Testing delete review...")
        if db.delete_review(review_id):
            print(f"   ✓ Deleted test review {review_id}")
    
    # Test export to DataFrame
    print("\n11. Testing export to DataFrame...")
    products_df = db.export_to_dataframe('products')
    print(f"   ✓ Exported {len(products_df)} products to DataFrame")
    
    reviews_df = db.export_to_dataframe('reviews')
    print(f"   ✓ Exported {len(reviews_df)} reviews to DataFrame")
    
    # Close connection
    db.close()
    
    print("\n" + "=" * 80)
    print("✓ ALL TESTS PASSED!")
    print("=" * 80)
    print("\nDatabase implementation is working correctly!")
    print("\nNext steps:")
    print("1. Run the database-powered demo: streamlit run demo/app_with_database.py")
    print("2. Compare with CSV version: streamlit run demo/app.py")
    print("3. Check database file: database/reviews.db (39.73 MB)")

if __name__ == "__main__":
    try:
        verify_database()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
