"""
Verify that all products in products_sample.csv have metadata
"""

import pandas as pd

print("Loading data...")
products = pd.read_csv('demo/products_sample.csv')
metadata = pd.read_csv('demo/product_metadata.csv')

print(f"\n📊 Data Summary:")
print(f"Total products in dataset: {len(products)}")
print(f"Total products with metadata: {len(metadata)}")

# Check coverage
products_set = set(products['product_id'])
metadata_set = set(metadata['product_id'])

matched = products_set & metadata_set
missing = products_set - metadata_set
extra = metadata_set - products_set

print(f"\n✅ Coverage Analysis:")
print(f"Products with metadata: {len(matched)} ({len(matched)/len(products)*100:.2f}%)")
print(f"Products missing metadata: {len(missing)} ({len(missing)/len(products)*100:.2f}%)")
print(f"Extra metadata entries: {len(extra)}")

if len(missing) > 0:
    print(f"\n⚠️ Missing metadata for products:")
    for pid in list(missing)[:10]:
        print(f"  - {pid}")
    if len(missing) > 10:
        print(f"  ... and {len(missing) - 10} more")
else:
    print(f"\n✅ Perfect! All {len(products)} products have metadata!")

# Check metadata quality
print(f"\n📊 Metadata Quality Check:")
print(f"Products with images: {metadata['image_url'].notna().sum()} ({metadata['image_url'].notna().sum()/len(metadata)*100:.2f}%)")
print(f"Products with names: {metadata['product_name'].notna().sum()} ({metadata['product_name'].notna().sum()/len(metadata)*100:.2f}%)")
print(f"Products with categories: {metadata['category'].notna().sum()} ({metadata['category'].notna().sum()/len(metadata)*100:.2f}%)")
print(f"Products with brands: {metadata['brand'].notna().sum()} ({metadata['brand'].notna().sum()/len(metadata)*100:.2f}%)")
print(f"Products with prices: {metadata['price'].notna().sum()} ({metadata['price'].notna().sum()/len(metadata)*100:.2f}%)")

# Show category distribution
print(f"\n📊 Category Distribution:")
print(metadata['category'].value_counts())

# Show sample products
print(f"\n📦 Sample Products with Metadata:")
sample = metadata.sample(5)
for _, row in sample.iterrows():
    print(f"\n  Product ID: {row['product_id']}")
    print(f"  Name: {row['product_name']}")
    print(f"  Category: {row['category']}")
    print(f"  Brand: {row['brand']}")
    print(f"  Price: {row['price']}")
    print(f"  Image: {row['image_url'][:60]}...")

print(f"\n✅ Verification complete!")
