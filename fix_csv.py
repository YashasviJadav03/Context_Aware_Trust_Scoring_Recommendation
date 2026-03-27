"""
Fix CSV loading issues for trust_scored_dataset.csv
"""

import pandas as pd
import numpy as np

def test_csv_loading():
    """Test different methods to load the CSV file."""
    
    file_path = "data/processed/trust_scored_dataset.csv"
    
    print("🔍 Testing CSV loading methods...")
    
    # Method 1: Standard pandas
    try:
        print("\n1. Trying standard pandas read_csv...")
        df = pd.read_csv(file_path)
        print(f"✅ Success! Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Method 2: Python engine
    try:
        print("\n2. Trying python engine...")
        df = pd.read_csv(file_path, engine='python')
        print(f"✅ Success! Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Method 3: C engine with error handling
    try:
        print("\n3. Trying c engine with error handling...")
        df = pd.read_csv(file_path, 
                        engine='c', 
                        on_bad_lines='skip',
                        low_memory=False)
        print(f"✅ Success! Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Method 4: Chunked loading
    try:
        print("\n4. Trying chunked loading...")
        chunk_list = []
        chunk_size = 10000
        max_rows = 100000  # Limit for testing
        
        for i, chunk in enumerate(pd.read_csv(file_path, 
                                            chunksize=chunk_size, 
                                            engine='python')):
            chunk_list.append(chunk)
            print(f"   Loaded chunk {i+1}: {chunk.shape}")
            
            if len(chunk_list) * chunk_size >= max_rows:
                print(f"   Stopping at {max_rows} rows for testing")
                break
        
        df = pd.concat(chunk_list, ignore_index=True)
        print(f"✅ Success! Final shape: {df.shape}")
        return df
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Method 5: Check if file exists and is readable
    try:
        print("\n5. Checking file status...")
        import os
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   File exists, size: {size:,} bytes ({size/1024**2:.1f} MB)")
            
            # Try reading first few lines
            with open(file_path, 'r', encoding='utf-8') as f:
                first_lines = [f.readline() for _ in range(5)]
                print("   First 5 lines:")
                for i, line in enumerate(first_lines):
                    print(f"   {i+1}: {line.strip()[:100]}...")
        else:
            print("   ❌ File does not exist!")
    except Exception as e:
        print(f"   ❌ Error checking file: {e}")
    
    return None

def create_sample_dataset():
    """Create a sample dataset if the original is corrupted."""
    
    print("\n🔧 Creating sample dataset for testing...")
    
    # Create synthetic data matching expected structure
    np.random.seed(42)
    n_samples = 10000
    
    data = {
        # Text features
        'review_length': np.random.randint(10, 500, n_samples),
        'sentiment_score': np.random.uniform(-1, 1, n_samples),
        'sentiment_extreme': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'repetition_ratio': np.random.uniform(0, 0.5, n_samples),
        'unique_word_ratio': np.random.uniform(0.3, 1.0, n_samples),
        'exclamation_count': np.random.poisson(1, n_samples),
        'question_count': np.random.poisson(0.5, n_samples),
        
        # Behavioral features
        'user_review_count': np.random.randint(1, 100, n_samples),
        'user_rating_variance': np.random.uniform(0, 2, n_samples),
        'user_avg_rating_deviation': np.random.uniform(0, 2, n_samples),
        'user_review_frequency': np.random.uniform(0.1, 10, n_samples),
        'user_extreme_ratio': np.random.uniform(0, 1, n_samples),
        'user_burst_flag': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
        'user_product_diversity': np.random.uniform(0, 1, n_samples),
        
        # Product features
        'product_review_count': np.random.randint(10, 1000, n_samples),
        'product_rating_variance': np.random.uniform(0, 2, n_samples),
        'product_rating_std': np.random.uniform(0, 1.5, n_samples),
        'product_popularity_log': np.random.uniform(2, 8, n_samples),
        'product_user_diversity': np.random.uniform(0, 1, n_samples),
        
        # Temporal features
        'days_since_first_review': np.random.randint(1, 365, n_samples),
        'review_density': np.random.uniform(0.01, 1, n_samples),
        'review_time_gap': np.random.randint(1, 30, n_samples),
        'burst_indicator': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
        
        # Rating features
        'rating': np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.1, 0.2, 0.3, 0.3]),
        'rating_deviation': np.random.uniform(0, 2, n_samples),
        'verified': np.random.choice([0, 1], n_samples, p=[0.3, 0.7]),
        'helpful_ratio': np.random.uniform(0, 1, n_samples),
        
        # Target variable
        'trust_score': np.random.beta(2, 2, n_samples)  # Beta distribution for 0-1 range
    }
    
    df = pd.DataFrame(data)
    
    # Save sample dataset
    sample_path = "data/processed/trust_scored_dataset_sample.csv"
    df.to_csv(sample_path, index=False)
    
    print(f"✅ Sample dataset created: {sample_path}")
    print(f"   Shape: {df.shape}")
    print(f"   Columns: {list(df.columns)}")
    
    return df

if __name__ == "__main__":
    # Test loading
    df = test_csv_loading()
    
    if df is None:
        print("\n❌ All loading methods failed. Creating sample dataset...")
        df = create_sample_dataset()
    else:
        print(f"\n✅ Successfully loaded dataset with shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Check for trust_score column
        if 'trust_score' in df.columns:
            print(f"Trust score range: {df['trust_score'].min():.3f} - {df['trust_score'].max():.3f}")
        else:
            print("❌ No 'trust_score' column found!")