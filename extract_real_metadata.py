"""
Extract real product metadata from Amazon Fashion metadata file
This replaces generated metadata with actual Amazon product information
"""

import pandas as pd
import gzip
import json




print("📦 Loading Amazon Fashion metadata...")
print("This may take a few minutes for large files...")

# Load metadata from compressed JSON
records = []
with gzip.open('data/raw/meta_AMAZON_FASHION.json.gz', 'rt', encoding='utf-8') as f:
    for i, line in enumerate(f):
        try:
            records.append(json.loads(line))
            if (i + 1) % 10000 == 0:
                print(f"Processed {i + 1} records...")
        except json.JSONDecodeError as e:
            print(f"Warning: Skipping malformed JSON at line {i + 1}")
            continue

print(f"\n✅ Loaded {len(records)} product metadata records")

# Convert to DataFrame
meta = pd.DataFrame(records)

print(f"\n📊 Available columns: {list(meta.columns)}")

# Select and rename relevant columns
# Check which columns exist
available_cols = []
col_mapping = {}

if 'asin' in meta.columns:
    available_cols.append('asin')
    col_mapping['asin'] = 'product_id'

if 'title' in meta.columns:
    available_cols.append('title')
    col_mapping['title'] = 'product_name'

# Handle image URLs - try multiple possible column names
image_col = None
for col in ['imageURLHighRes', 'imUrl', 'imageURL']:
    if col in meta.columns:
        available_cols.append(col)
        image_col = col
        break

if 'categories' in meta.columns:
    available_cols.append('categories')

if 'brand' in meta.columns:
    available_cols.append('brand')

if 'price' in meta.columns:
    available_cols.append('price')

# Add description/feature field if available
if 'feature' in meta.columns:
    available_cols.append('feature')
elif 'description' in meta.columns:
    available_cols.append('description')

print(f"\n📋 Using columns: {available_cols}")

# Select available columns
meta_clean = meta[available_cols].copy()

# Rename columns
meta_clean = meta_clean.rename(columns=col_mapping)

# Process image URLs
if image_col:
    def extract_image_url(x):
        """Extract first valid image URL from list or string"""
        try:
            # Check if it's None or NaN
            if x is None:
                return ''
            # Check if it's a numpy array or list
            if hasattr(x, '__iter__') and not isinstance(x, str):
                x_list = list(x)
                if len(x_list) > 0 and x_list[0]:
                    return str(x_list[0])
                return ''
            # It's a string or other scalar
            return str(x) if x else ''
        except:
            return ''
    
    meta_clean['image_url'] = meta_clean[image_col].apply(extract_image_url)
    meta_clean = meta_clean.drop(columns=[image_col])
else:
    # Fallback to placeholder if no image column
    meta_clean['image_url'] = 'https://images.unsplash.com/photo-1492707892479-7bc8d5a4ee93?w=400'

# Process categories
if 'categories' in meta_clean.columns:
    def extract_category(x):
        """Extract main category from nested list"""
        try:
            if x is None:
                return 'Fashion'
            if hasattr(x, '__iter__') and not isinstance(x, str):
                x_list = list(x)
                if len(x_list) > 0:
                    if hasattr(x_list[0], '__iter__') and not isinstance(x_list[0], str):
                        inner_list = list(x_list[0])
                        if len(inner_list) > 0:
                            return str(inner_list[0])
                    else:
                        return str(x_list[0])
            return 'Fashion'
        except:
            return 'Fashion'
    
    meta_clean['category'] = meta_clean['categories'].apply(extract_category)
    meta_clean = meta_clean.drop(columns=['categories'])
else:
    meta_clean['category'] = 'Fashion'

# Clean brand names
if 'brand' in meta_clean.columns:
    meta_clean['brand'] = meta_clean['brand'].fillna('Unknown Brand')
    meta_clean['brand'] = meta_clean['brand'].astype(str)
else:
    meta_clean['brand'] = 'Unknown Brand'

# Format prices
if 'price' in meta_clean.columns:
    def format_price(x):
        """Format price as currency"""
        if pd.isna(x):
            return 'N/A'
        try:
            # Try to extract numeric value
            if isinstance(x, str):
                # Remove currency symbols and extract number
                import re
                numbers = re.findall(r'\d+\.?\d*', x)
                if numbers:
                    price_val = float(numbers[0])
                    return f'${price_val:.2f}'
            elif isinstance(x, (int, float)):
                return f'${float(x):.2f}'
        except:
            pass
        return str(x)
    
    meta_clean['price'] = meta_clean['price'].apply(format_price)
else:
    meta_clean['price'] = 'N/A'

# Process descriptions/features
if 'feature' in meta_clean.columns:
    def extract_description(x):
        """Extract description from feature list"""
        try:
            if x is None or pd.isna(x):
                return ''
            # If it's a list, join the features
            if hasattr(x, '__iter__') and not isinstance(x, str):
                features = [str(f) for f in x if f]
                if features:
                    return ' | '.join(features[:3])  # Take first 3 features
                return ''
            # If it's a string, return as is
            return str(x) if x else ''
        except:
            return ''
    
    meta_clean['description'] = meta_clean['feature'].apply(extract_description)
    meta_clean = meta_clean.drop(columns=['feature'])
elif 'description' in meta_clean.columns:
    meta_clean['description'] = meta_clean['description'].fillna('')
    meta_clean['description'] = meta_clean['description'].astype(str)
else:
    meta_clean['description'] = ''

# Remove duplicates (keep first occurrence)
meta_clean = meta_clean.drop_duplicates(subset=['product_id'], keep='first')

# Remove rows with missing product_id
meta_clean = meta_clean[meta_clean['product_id'].notna()]

print(f"\n✅ Cleaned metadata: {len(meta_clean)} unique products")

# Load products from demo to see which ones we need
print("\n📦 Loading products from demo dataset...")
products = pd.read_csv('demo/products_sample.csv')
print(f"Products in demo: {len(products)}")

# Match metadata to demo products
matched = meta_clean[meta_clean['product_id'].isin(products['product_id'])]
print(f"\n✅ Matched products: {len(matched)} ({len(matched)/len(products)*100:.2f}%)")

# For unmatched products, create fallback entries
unmatched_ids = set(products['product_id']) - set(matched['product_id'])
print(f"⚠️ Unmatched products: {len(unmatched_ids)} ({len(unmatched_ids)/len(products)*100:.2f}%)")

if len(unmatched_ids) > 0:
    print("\n📝 Creating fallback entries for unmatched products...")
    fallback_records = []
    for pid in unmatched_ids:
        fallback_records.append({
            'product_id': pid,
            'product_name': f'Fashion Item {pid}',
            'image_url': 'https://images.unsplash.com/photo-1492707892479-7bc8d5a4ee93?w=400',
            'category': 'Fashion',
            'brand': 'Unknown Brand',
            'price': 'N/A',
            'description': ''
        })
    
    fallback_df = pd.DataFrame(fallback_records)
    final_metadata = pd.concat([matched, fallback_df], ignore_index=True)
else:
    final_metadata = matched

# Ensure all required columns exist
required_cols = ['product_id', 'product_name', 'image_url', 'category', 'brand', 'price', 'description']
for col in required_cols:
    if col not in final_metadata.columns:
        if col == 'product_name':
            final_metadata[col] = 'Fashion Item'
        elif col == 'image_url':
            final_metadata[col] = 'https://images.unsplash.com/photo-1492707892479-7bc8d5a4ee93?w=400'
        elif col == 'category':
            final_metadata[col] = 'Fashion'
        elif col == 'brand':
            final_metadata[col] = 'Unknown Brand'
        elif col == 'price':
            final_metadata[col] = 'N/A'
        elif col == 'description':
            final_metadata[col] = ''

# Reorder columns
final_metadata = final_metadata[required_cols]

# Save to CSV
output_file = 'demo/product_metadata.csv'
final_metadata.to_csv(output_file, index=False)

print(f"\n✅ Saved metadata to {output_file}")
print(f"✅ Total products: {len(final_metadata)}")

# Show statistics
print(f"\n📊 Metadata Quality:")
print(f"Products with real names: {(final_metadata['product_name'] != 'Fashion Item').sum()} ({(final_metadata['product_name'] != 'Fashion Item').sum()/len(final_metadata)*100:.2f}%)")
print(f"Products with real images: {(~final_metadata['image_url'].str.contains('unsplash')).sum()} ({(~final_metadata['image_url'].str.contains('unsplash')).sum()/len(final_metadata)*100:.2f}%)")
print(f"Products with brands: {(final_metadata['brand'] != 'Unknown Brand').sum()} ({(final_metadata['brand'] != 'Unknown Brand').sum()/len(final_metadata)*100:.2f}%)")
print(f"Products with prices: {(final_metadata['price'] != 'N/A').sum()} ({(final_metadata['price'] != 'N/A').sum()/len(final_metadata)*100:.2f}%)")
print(f"Products with descriptions: {(final_metadata['description'] != '').sum()} ({(final_metadata['description'] != '').sum()/len(final_metadata)*100:.2f}%)")

# Show category distribution
print(f"\n📊 Category Distribution:")
print(final_metadata['category'].value_counts().head(10))

# Show sample products
print(f"\n📦 Sample Real Products:")
real_products = final_metadata[final_metadata['product_name'] != 'Fashion Item'].head(5)
for _, row in real_products.iterrows():
    print(f"\n  Product ID: {row['product_id']}")
    print(f"  Name: {row['product_name'][:80]}...")
    print(f"  Category: {row['category']}")
    print(f"  Brand: {row['brand']}")
    print(f"  Price: {row['price']}")
    print(f"  Image: {row['image_url'][:60]}...")
    if row['description']:
        print(f"  Description: {row['description'][:100]}...")

print(f"\n✅ Done! Real Amazon product metadata extracted.")
