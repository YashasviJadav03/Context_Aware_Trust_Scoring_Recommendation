"""
Inspect the structure of Amazon metadata to understand the data format
"""

import gzip
import json

print("📦 Inspecting first 5 records from Amazon Fashion metadata...\n")

with gzip.open('data/raw/meta_AMAZON_FASHION.json.gz', 'rt', encoding='utf-8') as f:
    for i in range(5):
        line = f.readline()
        record = json.loads(line)
        
        print(f"{'='*80}")
        print(f"Record {i+1}:")
        print(f"{'='*80}")
        
        # Show all keys
        print(f"\nKeys: {list(record.keys())}\n")
        
        # Show important fields
        if 'asin' in record:
            print(f"ASIN: {record['asin']}")
        
        if 'title' in record:
            print(f"Title: {record['title'][:100]}...")
        
        if 'brand' in record:
            print(f"Brand: {record['brand']}")
        
        if 'price' in record:
            print(f"Price: {record['price']}")
        
        if 'imageURL' in record:
            print(f"imageURL type: {type(record['imageURL'])}")
            print(f"imageURL: {record['imageURL']}")
        
        if 'imageURLHighRes' in record:
            print(f"imageURLHighRes type: {type(record['imageURLHighRes'])}")
            if isinstance(record['imageURLHighRes'], list):
                print(f"imageURLHighRes length: {len(record['imageURLHighRes'])}")
                if len(record['imageURLHighRes']) > 0:
                    print(f"imageURLHighRes[0]: {record['imageURLHighRes'][0]}")
            else:
                print(f"imageURLHighRes: {record['imageURLHighRes']}")
        
        if 'categories' in record:
            print(f"categories type: {type(record['categories'])}")
            print(f"categories: {record['categories']}")
        
        print()
