"""
Generate comprehensive product metadata for all products in the dataset
This script creates product names, images, categories, brands, and prices for 7,503 products
"""

import pandas as pd
import random
import hashlib

# Load products
print("Loading products...")
products = pd.read_csv('demo/products_sample.csv')
print(f"Total products: {len(products)}")

# Define categories and their attributes
CATEGORIES = {
    'Women\'s Clothing': {
        'items': ['Dress', 'Blouse', 'Skirt', 'Sweater', 'Cardigan', 'Top', 'Pants', 'Jeans', 'Jacket', 'Coat'],
        'brands': ['ChicWear', 'FashionNova', 'StyleHub', 'TrendyLook', 'ElegantWear', 'ModernStyle'],
        'price_range': (25, 120),
        'image': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400'
    },
    'Men\'s Clothing': {
        'items': ['Shirt', 'T-Shirt', 'Polo', 'Jeans', 'Pants', 'Jacket', 'Sweater', 'Hoodie', 'Shorts', 'Suit'],
        'brands': ['ManStyle', 'UrbanGent', 'ClassicMen', 'ModernMan', 'GentWear', 'StyleKing'],
        'price_range': (20, 150),
        'image': 'https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=400'
    },
    'Footwear': {
        'items': ['Sneakers', 'Boots', 'Sandals', 'Heels', 'Flats', 'Loafers', 'Running Shoes', 'Formal Shoes'],
        'brands': ['FootComfort', 'StepStyle', 'WalkEasy', 'ShoeHub', 'ComfortFit', 'StridePro'],
        'price_range': (35, 180),
        'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'
    },
    'Accessories': {
        'items': ['Belt', 'Wallet', 'Bag', 'Hat', 'Scarf', 'Gloves', 'Sunglasses', 'Watch', 'Jewelry', 'Tie'],
        'brands': ['AccessPro', 'StyleAdd', 'FashionPlus', 'TrendyBits', 'ChicAccess', 'ModernTouch'],
        'price_range': (15, 200),
        'image': 'https://images.unsplash.com/photo-1492707892479-7bc8d5a4ee93?w=400'
    },
    'Jewelry': {
        'items': ['Necklace', 'Bracelet', 'Earrings', 'Ring', 'Pendant', 'Anklet', 'Brooch', 'Chain'],
        'brands': ['SparkleGem', 'JewelCraft', 'GemStone', 'ShineStyle', 'LuxeJewel', 'GlitterGold'],
        'price_range': (30, 500),
        'image': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=400'
    },
    'Bags & Luggage': {
        'items': ['Backpack', 'Handbag', 'Tote', 'Crossbody', 'Clutch', 'Suitcase', 'Duffel', 'Messenger Bag'],
        'brands': ['BagStyle', 'CarryAll', 'PackPro', 'TravelEase', 'LuggagePlus', 'BagMaster'],
        'price_range': (40, 250),
        'image': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400'
    }
}

def generate_product_name(product_id, category_data):
    """Generate a product name based on product ID and category"""
    # Use product_id hash to consistently generate same name for same ID
    hash_val = int(hashlib.md5(product_id.encode()).hexdigest(), 16)
    
    # Select item type
    item = category_data['items'][hash_val % len(category_data['items'])]
    
    # Add descriptive adjectives
    adjectives = ['Classic', 'Modern', 'Stylish', 'Premium', 'Elegant', 'Casual', 
                  'Comfortable', 'Trendy', 'Vintage', 'Designer', 'Luxury', 'Essential']
    adjective = adjectives[hash_val % len(adjectives)]
    
    # Add material/style descriptors
    descriptors = ['Cotton', 'Leather', 'Denim', 'Silk', 'Wool', 'Synthetic', 
                   'Canvas', 'Suede', 'Knit', 'Woven', 'Printed', 'Solid']
    descriptor = descriptors[(hash_val // 100) % len(descriptors)]
    
    return f"{adjective} {descriptor} {item}"

def generate_brand(product_id, category_data):
    """Generate a brand name based on product ID"""
    hash_val = int(hashlib.md5(product_id.encode()).hexdigest(), 16)
    return category_data['brands'][hash_val % len(category_data['brands'])]

def generate_price(product_id, category_data):
    """Generate a price based on product ID and category"""
    hash_val = int(hashlib.md5(product_id.encode()).hexdigest(), 16)
    min_price, max_price = category_data['price_range']
    
    # Generate price with some randomness but consistent for same ID
    price_range = max_price - min_price
    price = min_price + (hash_val % price_range)
    
    # Round to .99
    price = int(price) + 0.99
    
    return f"${price:.2f}"

def assign_category(product_id):
    """Assign a category based on product ID hash"""
    hash_val = int(hashlib.md5(product_id.encode()).hexdigest(), 16)
    categories = list(CATEGORIES.keys())
    return categories[hash_val % len(categories)]

# Generate metadata for all products
print("Generating metadata...")
metadata_list = []

for idx, row in products.iterrows():
    product_id = row['product_id']
    
    # Assign category
    category = assign_category(product_id)
    category_data = CATEGORIES[category]
    
    # Generate metadata
    metadata = {
        'product_id': product_id,
        'product_name': generate_product_name(product_id, category_data),
        'image_url': category_data['image'],
        'category': category,
        'brand': generate_brand(product_id, category_data),
        'price': generate_price(product_id, category_data)
    }
    
    metadata_list.append(metadata)
    
    if (idx + 1) % 1000 == 0:
        print(f"Processed {idx + 1}/{len(products)} products...")

# Create DataFrame
metadata_df = pd.DataFrame(metadata_list)

# Save to CSV
output_file = 'demo/product_metadata.csv'
metadata_df.to_csv(output_file, index=False)

print(f"\n✅ Generated metadata for {len(metadata_df)} products")
print(f"✅ Saved to {output_file}")

# Show statistics
print("\n📊 Category Distribution:")
print(metadata_df['category'].value_counts())

print("\n📊 Sample Products:")
print(metadata_df.head(10).to_string(index=False))

print("\n✅ Done! All 7,503 products now have metadata.")
