"""
Final diagnosis: Check if CSV data actually has the trust score problem
"""
import pandas as pd

# Load CSV
csv = pd.read_csv('data/processed/reviews_sample.csv')

print("=" * 60)
print("CSV TRUST SCORE ANALYSIS")
print("=" * 60)

# Overall stats
print(f"\nTotal reviews: {len(csv)}")
print(f"Unique products: {csv['product_id'].nunique()}")
print(f"\nTrust Score Statistics:")
print(csv['trust_score'].describe())

# Check how many are exactly 0.5
exactly_05 = (csv['trust_score'] == 0.5).sum()
close_to_05 = ((csv['trust_score'] >= 0.495) & (csv['trust_score'] <= 0.505)).sum()

print(f"\nReviews with trust_score exactly 0.500: {exactly_05} ({exactly_05/len(csv)*100:.1f}%)")
print(f"Reviews with trust_score 0.495-0.505: {close_to_05} ({close_to_05/len(csv)*100:.1f}%)")

# Check a sample product
sample_products = csv['product_id'].value_counts().head(10)
print(f"\n{'-'*60}")
print("TOP 10 PRODUCTS BY REVIEW COUNT:")
print(f"{'-'*60}")

for product_id, count in sample_products.items():
    product_reviews = csv[csv['product_id'] == product_id]
    min_trust = product_reviews['trust_score'].min()
    max_trust = product_reviews['trust_score'].max()
    avg_trust = product_reviews['trust_score'].mean()
    
    print(f"\n{product_id}: {count} reviews")
    print(f"  Trust range: {min_trust:.4f} - {max_trust:.4f} (avg: {avg_trust:.4f})")
    
    # Show first 5 trust scores
    scores = product_reviews['trust_score'].head(5).tolist()
    print(f"  First 5 scores: {[f'{s:.4f}' for s in scores]}")

print(f"\n{'='*60}")
print("CONCLUSION:")
print(f"{'='*60}")

if exactly_05 > len(csv) * 0.5:
    print("⚠️ PROBLEM FOUND: More than 50% of reviews have exactly 0.500 trust score!")
    print("   This indicates a data generation or model prediction issue.")
else:
    print("✅ DATA IS GOOD: Trust scores are properly varied.")
    print("   If you're seeing all 0.5 on the site, it's a display/caching issue.")
