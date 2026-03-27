"""
Trust Scoring System - Production Demo Application

This app demonstrates the trust scoring system in action:
1. Load trained model and scaler
2. Extract features from new reviews
3. Predict trust scores
4. Aggregate to product level
5. Generate rankings
"""

import pandas as pd
import numpy as np
import joblib
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.preprocess import clean_review_text
from features.feature_engineering import extract_features, FEATURE_NAMES
from models.trust_model import TrustModel


class TrustScoringApp:
    """Production-ready trust scoring application."""
    
    def __init__(self, model_path="../models/trained/best_trust_model.pkl",
                 scaler_path="../models/feature_scaler.pkl",
                 features_path="../models/trained/feature_names.txt"):
        """Initialize the app with trained model and scaler."""
        try:
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            
            with open(features_path, 'r') as f:
                self.feature_names = [line.strip() for line in f.readlines()]
            
            print("✅ Model loaded successfully")
            print(f"   Features: {len(self.feature_names)}")
        except FileNotFoundError as e:
            print(f"❌ Model files not found: {e}")
            print("   Please run notebook 07_trust_regression_models.ipynb first")
            print("   Using dummy model for demonstration...")
            
            # Create dummy model for demo
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.preprocessing import StandardScaler
            
            self.model = RandomForestRegressor(n_estimators=10, random_state=42)
            self.scaler = StandardScaler()
            
            # Use default feature names
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from src.features.feature_engineering import FEATURE_NAMES
            self.feature_names = FEATURE_NAMES
            
            # Fit dummy model on random data
            X_dummy = np.random.randn(100, len(self.feature_names))
            y_dummy = np.random.rand(100)
            
            self.scaler.fit(X_dummy)
            X_scaled = self.scaler.transform(X_dummy)
            self.model.fit(X_scaled, y_dummy)
            
            print("✅ Dummy model created for demonstration")
    
    def predict_trust_score(self, review_data):
        """
        Predict trust score for a single review.
        
        Args:
            review_data: dict with review information
            
        Returns:
            float: trust score (0-1)
        """
        # Extract features
        features = extract_features(review_data)
        
        # Prepare feature vector
        X = pd.DataFrame([features])[self.feature_names].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        trust_score = self.model.predict(X_scaled)[0]
        
        return np.clip(trust_score, 0, 1)
    
    def score_reviews(self, reviews_df):
        """
        Score multiple reviews.
        
        Args:
            reviews_df: DataFrame with review data
            
        Returns:
            DataFrame with trust scores
        """
        scores = []
        for idx, row in reviews_df.iterrows():
            score = self.predict_trust_score(row.to_dict())
            scores.append(score)
        
        reviews_df['trust_score'] = scores
        return reviews_df
    
    def aggregate_product_scores(self, reviews_df):
        """
        Aggregate review trust scores to product level.
        
        Formula: ProductScore = Σ(Trust_i × Rating_i) / Σ(Trust_i)
        
        Args:
            reviews_df: DataFrame with reviews and trust scores
            
        Returns:
            DataFrame with product scores
        """
        if 'trust_score' not in reviews_df.columns:
            raise ValueError("Reviews must have 'trust_score' column")
        
        # Calculate weighted ratings
        reviews_df['weighted_rating'] = reviews_df['trust_score'] * reviews_df['rating']
        
        # Aggregate by product
        product_scores = reviews_df.groupby('product_id').agg({
            'weighted_rating': 'sum',
            'trust_score': 'sum',
            'rating': ['mean', 'count']
        }).reset_index()
        
        product_scores.columns = ['product_id', 'weighted_sum', 'trust_sum', 
                                  'avg_rating', 'review_count']
        
        # Calculate trust-weighted product score
        product_scores['trust_weighted_score'] = (
            product_scores['weighted_sum'] / product_scores['trust_sum']
        )
        
        # Calculate baseline (raw average)
        product_scores['baseline_score'] = product_scores['avg_rating']
        
        # Calculate improvement
        product_scores['improvement'] = (
            product_scores['trust_weighted_score'] - product_scores['baseline_score']
        )
        
        return product_scores.sort_values('trust_weighted_score', ascending=False)
    
    def generate_report(self, reviews_df, product_scores):
        """Generate a summary report."""
        print("\n" + "="*80)
        print("TRUST SCORING SYSTEM - REPORT")
        print("="*80)
        
        print(f"\n📊 REVIEW-LEVEL STATISTICS")
        print(f"   Total reviews: {len(reviews_df)}")
        print(f"   Avg trust score: {reviews_df['trust_score'].mean():.4f}")
        print(f"   Std trust score: {reviews_df['trust_score'].std():.4f}")
        print(f"   Min trust score: {reviews_df['trust_score'].min():.4f}")
        print(f"   Max trust score: {reviews_df['trust_score'].max():.4f}")
        
        # Trust distribution
        high_trust = (reviews_df['trust_score'] >= 0.7).sum()
        medium_trust = ((reviews_df['trust_score'] >= 0.4) & 
                       (reviews_df['trust_score'] < 0.7)).sum()
        low_trust = (reviews_df['trust_score'] < 0.4).sum()
        
        print(f"\n   High trust (≥0.7):   {high_trust:6d} ({100*high_trust/len(reviews_df):.1f}%)")
        print(f"   Medium trust (0.4-0.7): {medium_trust:6d} ({100*medium_trust/len(reviews_df):.1f}%)")
        print(f"   Low trust (<0.4):    {low_trust:6d} ({100*low_trust/len(reviews_df):.1f}%)")
        
        print(f"\n📦 PRODUCT-LEVEL STATISTICS")
        print(f"   Total products: {len(product_scores)}")
        print(f"   Avg trust-weighted score: {product_scores['trust_weighted_score'].mean():.4f}")
        print(f"   Avg baseline score: {product_scores['baseline_score'].mean():.4f}")
        print(f"   Avg improvement: {product_scores['improvement'].mean():.4f}")
        
        print(f"\n🏆 TOP 5 PRODUCTS (by trust-weighted score)")
        for idx, row in product_scores.head(5).iterrows():
            print(f"   {row['product_id']:20s} | Score: {row['trust_weighted_score']:.4f} | "
                  f"Reviews: {int(row['review_count']):4d} | Improvement: {row['improvement']:+.4f}")
        
        print(f"\n⚠️  BOTTOM 5 PRODUCTS (by trust-weighted score)")
        for idx, row in product_scores.tail(5).iterrows():
            print(f"   {row['product_id']:20s} | Score: {row['trust_weighted_score']:.4f} | "
                  f"Reviews: {int(row['review_count']):4d} | Improvement: {row['improvement']:+.4f}")
        
        print("\n" + "="*80)


def main():
    """Demo: Load sample data and generate trust scores."""
    print("\n🚀 TRUST SCORING SYSTEM - PRODUCTION DEMO\n")
    
    # Initialize app
    app = TrustScoringApp()
    
    # Load sample data
    print("\n📂 Loading sample reviews...")
    try:
        reviews_df = pd.read_csv("../data/processed/reviews_with_predicted_trust.csv")
        reviews_df = reviews_df.head(1000)  # Use first 1000 for demo
        print(f"✅ Loaded {len(reviews_df)} reviews")
    except FileNotFoundError:
        print("❌ Sample data not found. Creating synthetic example...")
        reviews_df = pd.DataFrame({
            'product_id': ['PROD_001', 'PROD_001', 'PROD_002', 'PROD_002', 'PROD_003'],
            'rating': [5, 1, 4, 5, 3],
            'review_length': [150, 50, 200, 180, 100],
            'sentiment_score': [0.9, -0.8, 0.7, 0.85, 0.5],
            'verified': [1, 0, 1, 1, 0],
            'helpful_ratio': [0.8, 0.1, 0.7, 0.9, 0.3]
        })
    
    # Score reviews
    print("\n🔍 Scoring reviews...")
    reviews_df = app.score_reviews(reviews_df)
    print(f"✅ Scored {len(reviews_df)} reviews")
    
    # Aggregate to product level
    print("\n📊 Aggregating to product level...")
    product_scores = app.aggregate_product_scores(reviews_df)
    print(f"✅ Generated scores for {len(product_scores)} products")
    
    # Generate report
    app.generate_report(reviews_df, product_scores)
    
    # Save results
    print("\n💾 Saving results...")
    reviews_df.to_csv("demo_reviews_scored.csv", index=False)
    product_scores.to_csv("demo_product_scores.csv", index=False)
    print("✅ Results saved to demo_reviews_scored.csv and demo_product_scores.csv")


if __name__ == "__main__":
    main()
