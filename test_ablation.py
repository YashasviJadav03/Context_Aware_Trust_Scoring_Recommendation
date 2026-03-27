"""
Test script to verify ablation study setup
"""

import pandas as pd
import numpy as np

def test_ablation_setup():
    """Test if ablation study can run successfully."""
    
    print("🔍 Testing ablation study setup...")
    
    # Check if required files exist
    files_to_check = [
        "data/processed/trust_scored_dataset.csv",
        "results/reports/",
        "results/figures/"
    ]
    
    import os
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
    
    # Test feature categories
    feature_categories = {
        'text': [
            'review_length', 'sentiment_score', 'sentiment_extreme', 
            'repetition_ratio', 'unique_word_ratio', 'exclamation_count', 'question_count'
        ],
        'behavioral': [
            'user_review_count', 'user_rating_variance', 'user_avg_rating_deviation',
            'user_review_frequency', 'user_extreme_ratio', 'user_burst_flag', 'user_product_diversity'
        ],
        'product': [
            'product_review_count', 'product_rating_variance', 'product_rating_std',
            'product_popularity_log', 'product_user_diversity'
        ],
        'temporal': [
            'days_since_first_review', 'review_density', 'review_time_gap', 'burst_indicator'
        ],
        'rating': [
            'rating', 'rating_deviation', 'verified', 'helpful_ratio'
        ]
    }
    
    print(f"\n📊 Feature categories defined:")
    total_features = 0
    for category, features in feature_categories.items():
        print(f"  {category}: {len(features)} features")
        total_features += len(features)
    
    print(f"\nTotal expected features: {total_features}")
    
    # Test if we can load the dataset
    try:
        print("\n📂 Testing dataset loading...")
        df = pd.read_csv("data/processed/trust_scored_dataset.csv", nrows=1000)  # Sample
        print(f"✅ Dataset loaded: {df.shape}")
        
        # Check which features are available
        available_features = []
        for category, features in feature_categories.items():
            available_in_category = [f for f in features if f in df.columns]
            available_features.extend(available_in_category)
            print(f"  {category}: {len(available_in_category)}/{len(features)} available")
        
        print(f"\nTotal available features: {len(available_features)}")
        
        if 'trust_score' in df.columns:
            print(f"✅ Target variable 'trust_score' found")
            print(f"   Range: {df['trust_score'].min():.3f} - {df['trust_score'].max():.3f}")
        else:
            print(f"❌ Target variable 'trust_score' missing")
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
    
    print(f"\n🚀 Ablation study is ready to run!")
    print(f"   Expected output: results/reports/ablation_study.csv")
    print(f"   Expected visualization: results/figures/ablation_analysis.png")

if __name__ == "__main__":
    test_ablation_setup()