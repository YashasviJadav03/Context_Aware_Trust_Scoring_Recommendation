"""
Script to easily switch between balanced sample and full dataset
"""
import shutil
import os
import sys

def switch_to_full():
    """Switch to full dataset (883K reviews)"""
    print("Switching to FULL dataset (883,636 reviews)...")
    
    # Backup current
    if os.path.exists('data/processed/reviews_sample.csv'):
        shutil.copy('data/processed/reviews_sample.csv', 'data/processed/reviews_sample_backup.csv')
        print("  ✓ Backed up current sample")
    
    # Copy full dataset
    shutil.copy('data/processed/reviews_full.csv', 'data/processed/reviews_sample.csv')
    shutil.copy('data/processed/product_trust_scores_full.csv', 'data/processed/product_trust_scores.csv')
    
    print("  ✓ Switched to full dataset")
    print("\n[SUCCESS] Now using full dataset with 883K reviews!")
    print("This is best for local demos and impressive presentations.")

def switch_to_balanced():
    """Switch to balanced sample (9K reviews)"""
    print("Switching to BALANCED sample (9,025 reviews)...")
    
    # Check if balanced backup exists
    if not os.path.exists('data/processed/reviews_sample_old.csv'):
        print("[ERROR] Balanced sample backup not found!")
        print("Please run create_balanced_sample.py first.")
        return
    
    # Backup current
    if os.path.exists('data/processed/reviews_sample.csv'):
        shutil.copy('data/processed/reviews_sample.csv', 'data/processed/reviews_sample_backup.csv')
        print("  ✓ Backed up current sample")
    
    # Copy balanced sample
    shutil.copy('data/processed/reviews_sample_old.csv', 'data/processed/reviews_sample.csv')
    shutil.copy('data/processed/product_trust_scores_old.csv', 'data/processed/product_trust_scores.csv')
    
    print("  ✓ Switched to balanced sample")
    print("\n[SUCCESS] Now using balanced sample with 9K reviews!")
    print("This is best for Streamlit Cloud deployment (faster, less memory).")

def show_current():
    """Show current dataset info"""
    import pandas as pd
    
    print("\nCurrent Dataset Info:")
    print("=" * 60)
    
    try:
        reviews = pd.read_csv('data/processed/reviews_sample.csv')
        products = reviews['product_id'].nunique()
        avg_reviews = len(reviews) / products
        
        print(f"Total reviews: {len(reviews):,}")
        print(f"Total products: {products:,}")
        print(f"Average reviews per product: {avg_reviews:.1f}")
        
        # Determine which dataset
        if len(reviews) > 100000:
            print("\n[INFO] Currently using: FULL DATASET")
        elif len(reviews) > 8000 and len(reviews) < 10000:
            print("\n[INFO] Currently using: BALANCED SAMPLE")
        else:
            print("\n[INFO] Currently using: CUSTOM SAMPLE")
            
    except Exception as e:
        print(f"[ERROR] Could not read dataset: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("DATASET SWITCHER")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "full":
            switch_to_full()
        elif command == "balanced":
            switch_to_balanced()
        elif command == "info":
            show_current()
        else:
            print(f"[ERROR] Unknown command: {command}")
            print("\nUsage:")
            print("  python switch_dataset.py full      - Switch to full dataset (883K reviews)")
            print("  python switch_dataset.py balanced  - Switch to balanced sample (9K reviews)")
            print("  python switch_dataset.py info      - Show current dataset info")
    else:
        print("\nUsage:")
        print("  python switch_dataset.py full      - Switch to full dataset (883K reviews)")
        print("  python switch_dataset.py balanced  - Switch to balanced sample (9K reviews)")
        print("  python switch_dataset.py info      - Show current dataset info")
        print("\n")
        show_current()
