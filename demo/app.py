"""
Trust-Based Product Recommendation System - Streamlit Demo
Fixed Version with Better Error Handling
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import re
from textblob import TextBlob

# ============================================================================
# PAGE CONFIGURATION - MUST BE FIRST STREAMLIT COMMAND
# ============================================================================

st.set_page_config(
    page_title="Trust-Based Recommendation System",
    page_icon="",
    layout="wide"
)

# ============================================================================
# MODEL LOADING - INFERENCE PIPELINE
# ============================================================================

@st.cache_resource
def load_models():
    """Load trained models for inference"""
    import os
    
    # Try multiple possible paths
    possible_paths = [
        "",  # Running from root
        "../",  # Running from demo folder
        "./",  # Explicit current directory
    ]
    
    base_path = None
    for path in possible_paths:
        if os.path.exists(f"{path}models/tfidf_vectorizer.pkl"):
            base_path = path
            break
    
    if base_path is None:
        # Model files not found - show debug info
        current_dir = os.getcwd()
        st.warning(f"""
         **Model files not found**
        
        Current directory: `{current_dir}`
        
        The app will use a heuristic-based trust scoring system instead of ML models.
        """)
        return None, None, None
    
    try:
        tfidf = joblib.load(f"{base_path}models/tfidf_vectorizer.pkl")
        scaler = joblib.load(f"{base_path}models/feature_scaler.pkl")
        model = joblib.load(f"{base_path}models/trained/best_trust_model.pkl")
        
        # Success message (will only show on first load due to caching)
        st.success(" ML models loaded successfully!")
        
        return tfidf, scaler, model
    except Exception as e:
        # Error loading models
        st.error(f" Error loading models: {str(e)}")
        return None, None, None

# Load models once
tfidf_vectorizer, feature_scaler, trust_model = load_models()

# ============================================================================
# FEATURE ENGINEERING FOR NEW REVIEWS
# ============================================================================

def extract_features_for_review(review_text, rating, verified, helpful_votes=0, 
                                 user_review_count=1, product_review_count=10,
                                 product_rating_variance=0.5, days_since_first=30):
    """
    Extract features from a new review for inference
    
    Parameters:
    - review_text: str - The review text
    - rating: int - Rating (1-5)
    - verified: bool - Verified purchase
    - helpful_votes: int - Number of helpful votes (default 0 for new reviews)
    - user_review_count: int - Total reviews by this user (default 1)
    - product_review_count: int - Total reviews for this product (default 10)
    - product_rating_variance: float - Variance of product ratings (default 0.5)
    - days_since_first: int - Days since product's first review (default 30)
    
    Returns:
    - dict: Feature dictionary
    """
    
    # Text features
    review_length = len(review_text.split())
    exclamation_count = review_text.count('!')
    question_count = review_text.count('?')
    
    # Sentiment analysis using TextBlob (proper NLP-based sentiment)
    try:
        blob = TextBlob(review_text)
        sentiment_score = blob.sentiment.polarity  # Returns -1 to +1
    except:
        # Fallback to simple heuristic if TextBlob fails
        sentiment_score = 0.5 if rating >= 4 else -0.5
    
    sentiment_extreme = abs(sentiment_score)
    
    # Repetition ratio (simplified)
    words = review_text.lower().split()
    unique_words = len(set(words))
    repetition_ratio = 1 - (unique_words / len(words)) if len(words) > 0 else 0
    
    # User features
    user_review_frequency = user_review_count / max(days_since_first, 1)
    
    # Product features
    product_popularity_log = np.log1p(product_review_count)
    
    # Temporal features
    review_density = product_review_count / max(days_since_first, 1)
    review_time_gap = 1  # Default for new reviews
    
    # Rating features
    rating_deviation = abs(rating - 4.0)  # Assume product mean is 4.0
    helpful_ratio = helpful_votes / (helpful_votes + 1)
    
    features = {
        'review_length': review_length,
        'sentiment_score': sentiment_score,
        'sentiment_extreme': sentiment_extreme,
        'repetition_ratio': repetition_ratio,
        'exclamation_count': exclamation_count,
        'question_count': question_count,
        'user_review_count': user_review_count,
        'user_review_frequency': user_review_frequency,
        'product_review_count': product_review_count,
        'product_rating_variance': product_rating_variance,
        'product_popularity_log': product_popularity_log,
        'days_since_first_review': days_since_first,
        'review_density': review_density,
        'review_time_gap': review_time_gap,
        'rating': rating,
        'rating_deviation': rating_deviation,
        'verified': 1 if verified else 0,
        'helpful_ratio': helpful_ratio
    }
    
    return features

def predict_trust_score(review_text, rating, verified=True, helpful_votes=0,
                        user_review_count=1, product_review_count=10):
    """
    Predict trust score for a new review using trained models
    
    Returns:
    - float: Trust score (0-1)
    """
    if tfidf_vectorizer is None or feature_scaler is None or trust_model is None:
        # Models not loaded - use simple heuristic
        # Base score on rating, verified status, and review length
        base_score = rating / 5.0  # 0.2 to 1.0
        
        # Adjust for verified purchase
        if verified:
            base_score += 0.1
        
        # Adjust for helpful votes
        if helpful_votes > 0:
            base_score += min(helpful_votes * 0.02, 0.15)
        
        # Adjust for review length
        word_count = len(review_text.split())
        if word_count < 10:
            base_score -= 0.15  # Very short reviews are suspicious
        elif word_count > 50:
            base_score += 0.1  # Detailed reviews are more trustworthy
        
        # Adjust for excessive punctuation (fake review indicator)
        exclamation_count = review_text.count('!')
        if exclamation_count > 3:
            base_score -= 0.2  # Too many exclamations = suspicious
        
        # Clip to valid range [0, 1]
        return np.clip(base_score, 0, 1)
    
    try:
        # Extract structured features
        features = extract_features_for_review(
            review_text, rating, verified, helpful_votes,
            user_review_count, product_review_count
        )
        
        # Create feature dataframe
        feature_df = pd.DataFrame([features])
        
        # Get TF-IDF features
        tfidf_features = tfidf_vectorizer.transform([review_text]).toarray()
        
        # Combine features
        structured_features = feature_df.values
        combined_features = np.hstack([structured_features, tfidf_features])
        
        # Scale features
        scaled_features = feature_scaler.transform(combined_features)
        
        # Predict trust score
        trust_score = trust_model.predict(scaled_features)[0]
        
        # Clip to valid range [0, 1]
        trust_score = np.clip(trust_score, 0, 1)
        
        return trust_score
    
    except Exception as e:
        st.error(f"Error predicting trust score: {e}")
        # Fallback to heuristic
        base_score = rating / 5.0
        if verified:
            base_score += 0.1
        return np.clip(base_score, 0, 1)

# ============================================================================
# PRODUCT METADATA LOADING
# ============================================================================

@st.cache_data
def load_product_metadata():
    """Load product metadata from Google Drive with caching and fallback
    
    Returns:
        DataFrame: Product metadata with columns: product_id, product_name, image_url, category, brand, price, description
    """
    
    # Google Drive file ID for product_metadata.csv
    # TODO: Upload demo/product_metadata.csv to Google Drive and update this ID
    METADATA_FILE_ID = "YOUR_GOOGLE_DRIVE_FILE_ID_HERE"
    
    # Try Google Drive first
    if METADATA_FILE_ID != "YOUR_GOOGLE_DRIVE_FILE_ID_HERE":
        try:
            metadata_url = f"https://drive.google.com/uc?id={METADATA_FILE_ID}"
            metadata = pd.read_csv(metadata_url)
            return metadata
        except Exception as e:
            st.warning(f" Could not load metadata from Google Drive: {e}")
    
    # Fallback to local file
    try:
        metadata = pd.read_csv("demo/product_metadata.csv")
        return metadata
    except FileNotFoundError:
        st.error(" Product metadata file not found. Please ensure demo/product_metadata.csv exists.")
        # Return empty dataframe with expected columns
        return pd.DataFrame(columns=['product_id', 'product_name', 'image_url', 'category', 'brand', 'price', 'description'])

# Load product metadata
product_metadata = load_product_metadata()

# ============================================================================
# HELPER FUNCTION - DISPLAY PRODUCT INFO
# ============================================================================

def display_product_info(product_id, show_image=True, show_details=True):
    """Display product information with image and details"""
    # Get product metadata
    meta = product_metadata[product_metadata['product_id'] == product_id]
    
    if len(meta) > 0:
        meta_row = meta.iloc[0]
        
        if show_image and show_details:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Display product image - handle missing/empty URLs
                img_url = meta_row.get('image_url', '')
                if img_url and isinstance(img_url, str) and img_url.startswith('http'):
                    try:
                        st.image(img_url, use_container_width=True)
                    except:
                        st.markdown(" **No image available**")
                else:
                    st.markdown(" **No image available**")
            
            with col2:
                # Display product details
                st.markdown(f"### {meta_row['product_name']}")
                st.write(f"**Category:** {meta_row['category']}")
                st.write(f"**Brand:** {meta_row['brand']}")
                st.write(f"**Price:** {meta_row['price']}")
                st.write(f"**Product ID:** {product_id}")
                
                # Display description if available
                if 'description' in meta_row and meta_row['description'] and str(meta_row['description']) != 'nan':
                    desc = str(meta_row['description'])[:150]
                    st.caption(f" {desc}{'...' if len(str(meta_row['description'])) > 150 else ''}")
        
        elif show_image:
            # Display image only - handle missing/empty URLs
            img_url = meta_row.get('image_url', '')
            if img_url and isinstance(img_url, str) and img_url.startswith('http'):
                try:
                    st.image(img_url, width=150)
                except:
                    st.info("")
            else:
                st.info("")
        
        elif show_details:
            st.write(f"**{meta_row['product_name']}**")
            st.caption(f"{meta_row['category']} | {meta_row['brand']} | {meta_row['price']}")
    
    else:
        # No metadata available
        if show_image:
            st.info(" Product Image")
        if show_details:
            st.write(f"**Product ID:** {product_id}")
            st.caption("Fashion Item")

# ============================================================================
# DATA LOADING - GOOGLE DRIVE VERSION WITH FALLBACK
# ============================================================================

@st.cache_data
def load_data():
    """Load review and product data from Google Drive with caching and fallback
    
    Returns:
        tuple: (reviews_df, products_df, status_message) where status_message
               contains loading status information for display in main script
    """
    
    # File IDs for Google Drive
    REVIEWS_FILE_ID = "1brikM4-iQTUmsSZtqkLqFMFHWxdZp9cd"
    PRODUCTS_FILE_ID = "1bnwZBcnnzfGDRYpPg5Vr-wFYfsk6T5PG"
    
    # Option to use local files for testing
    USE_LOCAL_FILES = REVIEWS_FILE_ID == "YOUR_REVIEWS_FILE_ID_HERE"
    
    status_message = ""
    
    if USE_LOCAL_FILES:
        # Try local files
        try:
            reviews = pd.read_csv("../data/processed/reviews_sample.csv")
            products = pd.read_csv("../data/processed/product_trust_scores.csv")
            status_message = f" Local sample data loaded: {len(reviews):,} reviews, {len(products):,} products"
        except FileNotFoundError:
            # Try demo folder sample files
            try:
                reviews = pd.read_csv("reviews_sample.csv")
                products = pd.read_csv("products_sample.csv")
                status_message = f" Demo sample data loaded: {len(reviews):,} reviews, {len(products):,} products"
            except FileNotFoundError:
                raise FileNotFoundError("Sample CSV files not found. Please update File IDs to use Google Drive.")
    else:
        # Load from Google Drive
        try:
            # Try different URL formats for large files
            def load_large_csv_from_gdrive(file_id, file_name):
                urls_to_try = [
                    f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t",
                    f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t",
                    f"https://drive.google.com/uc?id={file_id}&export=download"
                ]
                
                for i, url in enumerate(urls_to_try):
                    try:
                        df = pd.read_csv(url)
                        if len(df) > 0 and len(df.columns) > 3:  # Basic validation
                            return df
                    except Exception as e:
                        continue
                
                raise Exception(f"Failed to load {file_name} from Google Drive")
            
            # Load reviews and products
            reviews = load_large_csv_from_gdrive(REVIEWS_FILE_ID, "reviews")
            products = load_large_csv_from_gdrive(PRODUCTS_FILE_ID, "products")
            
            status_message = f" Data loaded from Google Drive: {len(reviews):,} reviews, {len(products):,} products"
        except Exception as e:
            raise Exception(f"Error loading data from Google Drive: {e}")
    
    # Validate and fix column names (silent processing)
    review_col_mapping = {
        'user_id': ['user_id', 'userId', 'reviewer_id'],
        'product_id': ['product_id', 'productId', 'asin', 'product'],
        'rating': ['rating', 'overall', 'score'],
        'review_text': ['review_text', 'reviewText', 'text', 'summary'],
        'verified': ['verified', 'verified_purchase', 'verifiedPurchase'],
        'helpful_votes': ['helpful_votes', 'helpful', 'helpfulVotes'],
        'trust_score': ['trust_score', 'trustScore', 'predicted_trust_score'],
    }
    
    product_col_mapping = {
        'product_id': ['product_id', 'productId', 'asin', 'product'],
        'avg_rating': ['avg_rating', 'average_rating', 'avgRating'],
        'score_trust_weighted': ['score_trust_weighted', 'trust_weighted_score', 'trustScore'],
        'review_count': ['review_count', 'reviewCount', 'count']
    }
    
    # Standardize column names
    def standardize_columns(df, col_mapping):
        new_df = df.copy()
        for standard_name, possible_names in col_mapping.items():
            for possible_name in possible_names:
                if possible_name in df.columns:
                    if possible_name != standard_name:
                        new_df = new_df.rename(columns={possible_name: standard_name})
                    break
        return new_df
    
    reviews = standardize_columns(reviews, review_col_mapping)
    products = standardize_columns(products, product_col_mapping)
    
    # Check if required columns exist
    required_review_cols = ['product_id', 'rating', 'review_text', 'trust_score']
    required_product_cols = ['product_id', 'avg_rating', 'score_trust_weighted']
    
    missing_review_cols = [col for col in required_review_cols if col not in reviews.columns]
    missing_product_cols = [col for col in required_product_cols if col not in products.columns]
    
    if missing_review_cols:
        raise ValueError(f"Missing review columns: {missing_review_cols}")
        
    if missing_product_cols:
        raise ValueError(f"Missing product columns: {missing_product_cols}")
    
    # Add missing columns with defaults if needed
    if 'verified' not in reviews.columns:
        reviews['verified'] = True
    
    if 'helpful_votes' not in reviews.columns:
        reviews['helpful_votes'] = 0
    
    return reviews, products, status_message

# ============================================================================
# LOAD DATA WITH STATUS DISPLAY
# ============================================================================

try:
    with st.spinner("📥 Loading data..."):
        reviews, products, load_status = load_data()
    
    # Display success message
    st.success(load_status)
except Exception as e:
    st.error(f" Error loading data: {e}")
    st.error("**Possible solutions:**")
    st.error("1. Files are too large (>100MB) - Google Drive blocks direct CSV loading")
    st.error("2. Try using smaller sample files for demo")
    st.error("3. Use a different hosting service (Dropbox, AWS S3, etc.)")
    st.error("4. File IDs are incorrect or files aren't shared properly")
    st.stop()

# ============================================================================
# HEADER
# ============================================================================

st.title("Trust-Based Product Recommendation System")

# Show model loading status
if tfidf_vectorizer is None or feature_scaler is None or trust_model is None:
    st.warning("Running in Demo Mode - ML models not loaded. Using pre-computed trust scores from dataset.")

st.divider()

# ============================================================================
# PRODUCT SEARCH SIMULATION
# ============================================================================

st.header("Product Search")

