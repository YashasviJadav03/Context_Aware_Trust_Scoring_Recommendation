"""
Feature Engineering for Trust Scoring System

Extracts 27 features from review data for trust prediction.
"""

import pandas as pd
import numpy as np
from textblob import TextBlob
import re
from datetime import datetime


def extract_features(review_data):
    """
    Extract 27 features from review data.
    
    Args:
        review_data (dict): Review information
        
    Returns:
        dict: Feature values
    """
    features = {}
    
    # Get review text (handle missing text)
    text = str(review_data.get('text', ''))
    if pd.isna(text) or text == 'nan':
        text = ''
    
    # Basic info
    rating = float(review_data.get('rating', 3))
    verified = bool(review_data.get('verified', False))
    helpful_votes = int(review_data.get('helpful_votes', 0))
    total_votes = int(review_data.get('total_votes', 0))
    
    # === TEXT FEATURES (7) ===
    
    # 1. Review length
    features['review_length'] = len(text.split()) if text else 0
    
    # 2. Sentiment score
    try:
        blob = TextBlob(text)
        features['sentiment_score'] = blob.sentiment.polarity
    except:
        features['sentiment_score'] = 0.0
    
    # 3. Sentiment extreme (very positive or negative)
    features['sentiment_extreme'] = 1 if abs(features['sentiment_score']) > 0.7 else 0
    
    # 4. Repetition ratio
    if text:
        words = text.lower().split()
        unique_words = set(words)
        features['repetition_ratio'] = 1 - (len(unique_words) / len(words)) if words else 0
    else:
        features['repetition_ratio'] = 0
    
    # 5. Unique word ratio
    if text:
        words = text.lower().split()
        features['unique_word_ratio'] = len(set(words)) / len(words) if words else 0
    else:
        features['unique_word_ratio'] = 0
    
    # 6. Exclamation count
    features['exclamation_count'] = text.count('!') if text else 0
    
    # 7. Question count
    features['question_count'] = text.count('?') if text else 0
    
    # === BEHAVIORAL FEATURES (7) ===
    # Note: These would normally come from user history analysis
    # For demo, we'll use reasonable defaults
    
    # 8. User review count (estimated)
    features['user_review_count'] = 10  # Default assumption
    
    # 9. User rating variance (estimated)
    features['user_rating_variance'] = 1.0  # Default assumption
    
    # 10. User average rating deviation
    features['user_avg_rating_deviation'] = abs(rating - 4.0)  # Deviation from typical 4.0
    
    # 11. User review frequency (reviews per month)
    features['user_review_frequency'] = 2.0  # Default assumption
    
    # 12. User extreme ratio (% of 1 or 5 star ratings)
    features['user_extreme_ratio'] = 1.0 if rating in [1, 5] else 0.3
    
    # 13. User burst flag (many reviews in short time)
    features['user_burst_flag'] = 0  # Default: no burst
    
    # 14. User product diversity
    features['user_product_diversity'] = 0.7  # Default assumption
    
    # === PRODUCT FEATURES (5) ===
    # Note: These would normally come from product analysis
    
    # 15. Product review count (estimated)
    features['product_review_count'] = 100  # Default assumption
    
    # 16. Product rating variance
    features['product_rating_variance'] = 1.5  # Default assumption
    
    # 17. Product rating standard deviation
    features['product_rating_std'] = 1.2  # Default assumption
    
    # 18. Product popularity (log scale)
    features['product_popularity_log'] = np.log(100)  # Default assumption
    
    # 19. Product user diversity
    features['product_user_diversity'] = 0.8  # Default assumption
    
    # === TEMPORAL FEATURES (4) ===
    
    # 20. Days since first review (estimated)
    features['days_since_first_review'] = 30  # Default assumption
    
    # 21. Review density (reviews per day)
    features['review_density'] = 0.1  # Default assumption
    
    # 22. Review time gap (days since last review)
    features['review_time_gap'] = 7  # Default assumption
    
    # 23. Burst indicator
    features['burst_indicator'] = 0  # Default: no burst
    
    # === RATING FEATURES (4) ===
    
    # 24. Rating
    features['rating'] = rating
    
    # 25. Rating deviation (from product average, estimated as 4.0)
    features['rating_deviation'] = abs(rating - 4.0)
    
    # 26. Verified purchase
    features['verified'] = 1 if verified else 0
    
    # 27. Helpful ratio
    if total_votes > 0:
        features['helpful_ratio'] = helpful_votes / total_votes
    else:
        features['helpful_ratio'] = 0.5  # Default neutral
    
    return features


def extract_features_batch(reviews_df):
    """
    Extract features for multiple reviews efficiently.
    
    Args:
        reviews_df (pd.DataFrame): DataFrame with review data
        
    Returns:
        pd.DataFrame: DataFrame with extracted features
    """
    feature_list = []
    
    for idx, row in reviews_df.iterrows():
        features = extract_features(row.to_dict())
        feature_list.append(features)
    
    return pd.DataFrame(feature_list)


# Feature names in order (for consistency with trained model)
FEATURE_NAMES = [
    'review_length', 'sentiment_score', 'sentiment_extreme', 'repetition_ratio',
    'unique_word_ratio', 'exclamation_count', 'question_count',
    'user_review_count', 'user_rating_variance', 'user_avg_rating_deviation',
    'user_review_frequency', 'user_extreme_ratio', 'user_burst_flag',
    'user_product_diversity', 'product_review_count', 'product_rating_variance',
    'product_rating_std', 'product_popularity_log', 'product_user_diversity',
    'days_since_first_review', 'review_density', 'review_time_gap', 'burst_indicator',
    'rating', 'rating_deviation', 'verified', 'helpful_ratio'
]