"""
Clean up the extracted metadata:
1. Replace 'nan' image URLs with category-appropriate placeholders
2. Replace 'Unknown Brand' with better fallbacks
3. Ensure all fields are properly formatted
"""

import pandas as pd

print("📦 Loading extracted metadata...")
meta = pd.read_csv('demo/product_metadata.csv')

print(f"Total products: {len(meta)}")

# Count issues
nan_images = (meta['image_url'] == 'nan') | (meta['image_url'].isna())
unknown_brands = (meta['brand'] == 'Unknown Brand') | (meta['brand'].isna())
na_prices = (meta['price'] == 'N/A') | (meta['price'].isna())

print(f"\n📊 Issues to fix:")
print(f"Products with 'nan' images: {nan_images.sum()} ({nan_images.sum()/len(meta)*100:.2f}%)")
print(f"Products with 'Unknown Brand': {unknown_brands.sum()} ({unknown_brands.sum()/len(meta)*100:.2f}%)")
print(f"Products with 'N/A' prices: {na_prices.sum()} ({na_prices.sum()/len(meta)*100:.2f}%)")

# Fix 'nan' image URLs with a generic fashion placeholder
print("\n🔧 Fixing image URLs...")
meta.loc[nan_images, 'image_url'] = 'https://images.unsplash.com/photo-1492707892479-7bc8d5a4ee93?w=400'

# Fix 'Unknown Brand' - keep as is, it's honest
# But ensure it's not NaN
meta['brand'] = meta['brand'].fillna('Unknown Brand')

# Fix 'N/A' prices - keep as is, it's honest
meta['price'] = meta['price'].fillna('N/A')

# Ensure category is not empty
meta['category'] = meta['category'].fillna('Fashion')

# Ensure product_name is not empty
meta['product_name'] = meta['product_name'].fillna('Fashion Item')

# Save cleaned metadata
output_file = 'demo/product_metadata.csv'
meta.to_csv(output_file, index=False)

print(f"\n✅ Cleaned metadata saved to {output_file}")

# Show final statistics
print(f"\n📊 Final Statistics:")
print(f"Total products: {len(meta)}")
print(f"Products with real Amazon images: {(~meta['image_url'].str.contains('unsplash', na=False)).sum()} ({(~meta['image_url'].str.contains('unsplash', na=False)).sum()/len(meta)*100:.2f}%)")
print(f"Products with placeholder images: {(meta['image_url'].str.contains('unsplash', na=False)).sum()} ({(meta['image_url'].str.contains('unsplash', na=False)).sum()/len(meta)*100:.2f}%)")
print(f"Products with known brands: {(meta['brand'] != 'Unknown Brand').sum()} ({(meta['brand'] != 'Unknown Brand').sum()/len(meta)*100:.2f}%)")
print(f"Products with prices: {(meta['price'] != 'N/A').sum()} ({(meta['price'] != 'N/A').sum()/len(meta)*100:.2f}%)")

# Show sample of real products
print(f"\n📦 Sample Real Amazon Products:")
real_products = meta[(~meta['image_url'].str.contains('unsplash', na=False)) & (meta['brand'] != 'Unknown Brand')].head(10)

for _, row in real_products.iterrows():
    print(f"\n  {row['product_name'][:60]}...")
    print(f"  Brand: {row['brand']} | Price: {row['price']}")
    print(f"  Image: {row['image_url'][:70]}...")

print(f"\n✅ Done! Metadata is now clean and ready for use.")
