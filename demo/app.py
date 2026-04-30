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
    page_icon="🧠",
    layout="wide"
)

# ============================================================================
# MODEL LOADING - INFERENCE PIPELINE
# ============================================================================

@st.cache_resource
def load_models():
    """Load trained models for inference"""
    import os
    
    # Determine the correct base path
    # If running from demo folder, go up one level
    # If running from root, use current directory
    if os.path.exists("models/tfidf_vectorizer.pkl"):
        base_path = ""
    elif os.path.exists("../models/tfidf_vectorizer.pkl"):
        base_path = "../"
    else:
        # Model files not found - return None silently
        return None, None, None
    
    try:
        tfidf = joblib.load(f"{base_path}models/tfidf_vectorizer.pkl")
        scaler = joblib.load(f"{base_path}models/feature_scaler.pkl")
        model = joblib.load(f"{base_path}models/trained/best_trust_model.pkl")
        return tfidf, scaler, model
    except Exception as e:
        # Error loading models - return None silently
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
        return 0.5  # Default score if models not loaded
    
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
        return 0.5  # Default score on error

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
            st.warning(f"⚠️ Could not load metadata from Google Drive: {e}")
    
    # Fallback to local file
    try:
        metadata = pd.read_csv("demo/product_metadata.csv")
        return metadata
    except FileNotFoundError:
        st.error("❌ Product metadata file not found. Please ensure demo/product_metadata.csv exists.")
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
                        st.markdown("📦 **No image available**")
                else:
                    st.markdown("📦 **No image available**")
            
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
                    st.caption(f"📝 {desc}{'...' if len(str(meta_row['description'])) > 150 else ''}")
        
        elif show_image:
            # Display image only - handle missing/empty URLs
            img_url = meta_row.get('image_url', '')
            if img_url and isinstance(img_url, str) and img_url.startswith('http'):
                try:
                    st.image(img_url, width=150)
                except:
                    st.info("📦")
            else:
                st.info("📦")
        
        elif show_details:
            st.write(f"**{meta_row['product_name']}**")
            st.caption(f"{meta_row['category']} | {meta_row['brand']} | {meta_row['price']}")
    
    else:
        # No metadata available
        if show_image:
            st.info("📦 Product Image")
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
            status_message = f"✅ Local sample data loaded: {len(reviews):,} reviews, {len(products):,} products"
        except FileNotFoundError:
            # Try demo folder sample files
            try:
                reviews = pd.read_csv("reviews_sample.csv")
                products = pd.read_csv("products_sample.csv")
                status_message = f"✅ Demo sample data loaded: {len(reviews):,} reviews, {len(products):,} products"
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
            
            status_message = f"✅ Data loaded from Google Drive: {len(reviews):,} reviews, {len(products):,} products"
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
    st.error(f"❌ Error loading data: {e}")
    st.error("**Possible solutions:**")
    st.error("1. Files are too large (>100MB) - Google Drive blocks direct CSV loading")
    st.error("2. Try using smaller sample files for demo")
    st.error("3. Use a different hosting service (Dropbox, AWS S3, etc.)")
    st.error("4. File IDs are incorrect or files aren't shared properly")
    st.stop()

# ============================================================================
# HEADER
# ============================================================================

st.title("🧠 Trust-Based Product Recommendation System")

# Show model loading status
if tfidf_vectorizer is None or feature_scaler is None or trust_model is None:
    st.warning("""
    ⚠️ **Running in Demo Mode** - ML models not loaded. 
    
    The app is using pre-computed trust scores from the dataset. 
    To enable live inference in Section 5, ensure model files are accessible.
    """)

st.markdown("""
This system ranks reviews and products by **trust score** instead of just rating.
Low-quality reviews are identified and can be filtered out.
""")

st.divider()

# ============================================================================
# PRODUCT SEARCH SIMULATION
# ============================================================================

st.header("🔍 Product Search")

# Initialize session state variables BEFORE using them
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None

if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

if 'clear_search_flag' not in st.session_state:
    st.session_state.clear_search_flag = False

if 'added_reviews' not in st.session_state:
    st.session_state.added_reviews = []

# Handle clear search action
if st.session_state.clear_search_flag:
    st.session_state.search_query = ""
    st.session_state.selected_product = None
    st.session_state.clear_search_flag = False
    # Clear the search input widget state directly
    st.session_state.search_input = ""

# Search input with advanced options
col1, col2 = st.columns([3, 1])
with col1:
    search_query = st.text_input(
        "Search for products:", 
        value=st.session_state.search_query,
        placeholder="e.g., 'B014EB2ADA' or 'B01' for partial match", 
        key="search_input"
    )
    # Update session state with current search query
    if search_query != st.session_state.search_query:
        st.session_state.search_query = search_query
with col2:
    search_mode = st.selectbox("Search Mode", ["Smart Search", "Exact Match", "High Trust Only"])

if search_query:
    # Real search functionality
    search_query_upper = search_query.upper().strip()
    
    # Search methods based on mode
    search_results = pd.DataFrame()
    
    if search_mode == "Exact Match":
        search_results = products[products['product_id'].str.upper() == search_query_upper]
        search_type = "Exact Match"
        
    elif search_mode == "High Trust Only":
        high_trust_threshold = products['score_trust_weighted'].quantile(0.75)
        high_trust_products = products[products['score_trust_weighted'] >= high_trust_threshold]
        
        if search_query_upper in high_trust_products['product_id'].str.upper().values:
            search_results = high_trust_products[high_trust_products['product_id'].str.upper() == search_query_upper]
            search_type = "High Trust Exact Match"
        else:
            search_results = high_trust_products[high_trust_products['product_id'].str.upper().str.contains(search_query_upper, na=False)].head(10)
            search_type = "High Trust Products"
            
    else:  # Smart Search (default)
        exact_match = products[products['product_id'].str.upper() == search_query_upper]
        partial_match = products[products['product_id'].str.upper().str.startswith(search_query_upper)]
        contains_match = products[products['product_id'].str.upper().str.contains(search_query_upper, na=False)]
        
        if len(exact_match) > 0:
            search_results = exact_match
            search_type = "Exact Match"
            # Auto-select exact match
            st.session_state.selected_product = exact_match.iloc[0]['product_id']
        elif len(partial_match) > 0:
            search_results = partial_match.head(10)
            search_type = "Partial Match"
        elif len(contains_match) > 0:
            search_results = contains_match.head(10)
            search_type = "Contains Match"
        else:
            search_results = products.nlargest(5, 'score_trust_weighted')
            search_type = "No matches - Top Suggestions"
    
    # Sort search results by trust score (descending)
    if len(search_results) > 0:
        search_results = search_results.sort_values('score_trust_weighted', ascending=False)
    
    # Display search info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader(f"🔍 Search Results: '{search_query}'")
        if len(search_results) > 0:
            st.info(f"**{search_type}** - Found {len(search_results)} product(s)")
        else:
            st.warning(f"**No Results** - No products found for '{search_query}'")
    with col2:
        if st.button("🔄 Clear Search", key="clear_search"):
            st.session_state.clear_search_flag = True
            st.rerun()
    with col3:
        if len(search_results) > 0:
            avg_trust = search_results['score_trust_weighted'].mean()
            st.metric("Avg Trust", f"{avg_trust:.2f}")
    
    # Display results
    if len(search_results) > 0:
        for idx, (_, product) in enumerate(search_results.iterrows(), 1):
            # Highlight exact matches and high trust products
            if product['product_id'].upper() == search_query_upper:
                highlight = "🎯"
                badge = "EXACT MATCH"
            elif product['score_trust_weighted'] >= 4.5:
                highlight = "⭐"
                badge = "HIGH TRUST"
            else:
                highlight = "📦"
                badge = ""
            
            col1, col2, col3, col4 = st.columns([1, 1, 3, 1])
            with col1:
                st.write(f"**#{idx}** {highlight}")
                if badge:
                    st.caption(badge)
            with col2:
                # Display product image (small)
                display_product_info(product['product_id'], show_image=True, show_details=False)
            with col3:
                # Display product name and details
                meta = product_metadata[product_metadata['product_id'] == product['product_id']]
                if len(meta) > 0:
                    st.write(f"**{meta.iloc[0]['product_name']}**")
                    st.caption(f"{meta.iloc[0]['category']} | {meta.iloc[0]['brand']}")
                else:
                    st.write(f"**Product {product['product_id']}**")
                st.write(f"Trust Score: {product['score_trust_weighted']:.2f}")
                
                # Show additional info for matches
                if hasattr(product, 'review_count') and pd.notna(product.get('review_count')):
                    review_count = product['review_count']
                    avg_rating = product.get('avg_rating', 0)
                    st.write(f"📊 Reviews: {review_count} | Avg Rating: {avg_rating:.2f}")
                    
            with col4:
                if st.button(f"Analyze", key=f"search_analyze_{idx}"):
                    st.session_state.selected_product = product['product_id']
                    st.success(f"✅ Selected!")
                    st.rerun()
    
    # Search suggestions
    if len(search_results) == 0:
        st.subheader("💡 Search Suggestions")
        st.write("Try these search patterns:")
        st.write("- **Exact ID:** B014EB2ADA")
        st.write("- **Partial ID:** B01 (shows all products starting with B01)")
        st.write("- **Switch to 'High Trust Only'** to search within top-rated products")
    
    st.divider()

else:
    # Show helpful message when no search
    st.info("💡 **Get Started:** Enter a product ID above to search and analyze reviews")
    st.markdown("""
    **Tips:**
    - Search for a specific product ID (e.g., B014EB2ADA)
    - Use partial ID to find multiple products (e.g., B01)
    - Switch to 'High Trust Only' mode to search within top-rated products
    - Scroll down to Section 4 to see the top 10 recommended products
    """)

st.divider()

# ============================================================================
# SECTION 1 — PRODUCT SELECTION (DYNAMIC)
# ============================================================================

st.header("📦 Product Analysis")

# Use selected product from search if available, otherwise show dropdown
if st.session_state.selected_product:
    # Product selected from search - show it prominently
    product_id = str(st.session_state.selected_product)
    
    st.success(f"🎯 Analyzing Product: **{product_id}** (from search)")
    
    # Option to change product
    if st.button("🔄 Select Different Product", key="change_product"):
        st.session_state.selected_product = None
        st.rerun()
    
else:
    # No search selection - show dropdown
    st.info("💡 Search for a product above, or select from popular products below")
    
    # Get products with multiple reviews for better demo
    try:
        product_review_counts = reviews.groupby('product_id').size().reset_index(name='count')
        products_with_reviews = product_review_counts[product_review_counts['count'] >= 5].sort_values('count', ascending=False)
    except KeyError as e:
        st.error(f"❌ Column error: {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error processing product counts: {e}")
        st.stop()

    # Create product options with review counts
    product_options = []
    for _, row in products_with_reviews.head(100).iterrows():
        pid = row['product_id']
        count = row['count']
        product_options.append(f"{pid} ({count} reviews)")

    if not product_options:
        st.error("❌ No products found with sufficient reviews")
        st.stop()

    selected_option = st.selectbox(
        "Select a product to analyze:",
        product_options,
        key="product_selector_dropdown",
        help="Products with at least 5 reviews are shown"
    )

    # Extract product_id from selection
    product_id = selected_option.split(' (')[0]
    
    # Add explicit Analyze button - only set session state on button click
    if st.button("🔍 Analyze this product", key="analyze_dropdown_product"):
        st.session_state.selected_product = product_id
        st.rerun()

# Show prominent indicator of what's being analyzed
st.markdown("---")
if st.session_state.selected_product:
    product_id = str(st.session_state.selected_product)
    current_product = products[products['product_id'].astype(str) == product_id]
    current_reviews = reviews[reviews['product_id'].astype(str) == product_id]
    
    if len(current_product) > 0 and len(current_reviews) > 0:
        trust_score = current_product['score_trust_weighted'].iloc[0]
        avg_rating = current_product['avg_rating'].iloc[0]
        review_count = len(current_reviews)
        
        # Display product image and info prominently
        st.subheader("📦 Product Being Analyzed")
        display_product_info(product_id, show_image=True, show_details=True)
        
        st.markdown("---")
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 Product ID", product_id)
        with col2:
            st.metric("🧠 Trust Score", f"{trust_score:.2f}")
        with col3:
            st.metric("⭐ Avg Rating", f"{avg_rating:.2f}")
        with col4:
            st.metric("📊 Reviews", review_count)
    else:
        st.error(f"❌ Product {product_id} not found or has no reviews in dataset")
        st.stop()

st.divider()

# ============================================================================
# SECTION 2 — REVIEWS RANKED BY TRUST
# ============================================================================

st.header("📊 Section 2: Reviews Ranked by Trust")

# Guard: Ensure a product has been selected and analyzed
if 'selected_product' not in st.session_state or st.session_state.selected_product is None:
    st.info("👆 Search for a product above and click **Analyze** to see reviews.")
    st.stop()

# Get product_id from session state
product_id = str(st.session_state.selected_product)

# Filter reviews for selected product
filtered_reviews = reviews[reviews['product_id'].astype(str) == str(product_id)].copy()

if len(filtered_reviews) == 0:
    st.error(f"❌ No reviews found for product {product_id}")
    st.stop()

# Safety check: ensure trust_score column exists
if 'trust_score' not in filtered_reviews.columns:
    if 'predicted_trust_score' in filtered_reviews.columns:
        filtered_reviews['trust_score'] = filtered_reviews['predicted_trust_score']
    else:
        st.error("❌ Trust score column not found in reviews data")
        st.stop()

# Sort by trust score (descending)
filtered_reviews = filtered_reviews.sort_values(by="trust_score", ascending=False)

# Flag low trust reviews
filtered_reviews['low_trust_flag'] = filtered_reviews['trust_score'] < 0.3

# Display statistics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Reviews", len(filtered_reviews))
with col2:
    st.metric("Avg Trust Score", f"{filtered_reviews['trust_score'].mean():.3f}")
with col3:
    st.metric("Avg Rating", f"{filtered_reviews['rating'].mean():.2f}")
with col4:
    if 'verified' in filtered_reviews.columns:
        verified_pct = (filtered_reviews['verified'].sum() / len(filtered_reviews) * 100)
        st.metric("Verified %", f"{verified_pct:.1f}%")
    else:
        st.metric("Verified %", "N/A")

# Add visualization
st.subheader("Trust Score Distribution")
col1, col2 = st.columns(2)

with col1:
    # Trust score histogram
    trust_hist = filtered_reviews['trust_score'].value_counts(bins=10, sort=False).sort_index()
    st.bar_chart(trust_hist)
    st.caption("Distribution of trust scores")

with col2:
    # Rating vs Trust comparison (normalized to same scale)
    # Trust score is 0-1, so multiply by 5 to compare with rating (1-5)
    avg_rating = filtered_reviews['rating'].mean()
    avg_trust_normalized = filtered_reviews['trust_score'].mean() * 5  # Normalize 0-1 to 0-5
    
    comparison_data = pd.DataFrame({
        'Rating': [avg_rating],
        'Trust Score (×5)': [avg_trust_normalized]
    })
    st.bar_chart(comparison_data.T)
    st.caption("Average Rating vs Trust Score (normalized to 1-5 scale)")
    st.caption(f"Raw trust score: {filtered_reviews['trust_score'].mean():.3f} (0-1 scale)")

# Trust score filter
st.subheader("Filter by Trust Score")
min_trust = st.slider(
    "Minimum trust score:",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.1,
    help="Filter out low-trust reviews"
)

filtered_reviews_display = filtered_reviews[filtered_reviews['trust_score'] >= min_trust]

# Show low trust warning
low_trust_count = (filtered_reviews['trust_score'] < 0.3).sum()
if low_trust_count > 0:
    st.warning(f"⚠️ {low_trust_count} low-trust reviews detected (trust score < 0.3)")

st.write(f"Showing **{len(filtered_reviews_display)}** reviews (filtered from {len(filtered_reviews)})")

# Display reviews table with highlighting
display_df = filtered_reviews_display[['review_text', 'rating', 'trust_score', 'verified', 'low_trust_flag']].copy()
# Smart truncation - only add '...' if text is actually longer than 200 chars
display_df['review_text'] = display_df['review_text'].astype(str).apply(lambda x: x[:200] + '...' if len(x) > 200 else x)
display_df['trust_score'] = display_df['trust_score'].round(4)

# Add flag column for highlighting
display_df['Status'] = display_df['low_trust_flag'].apply(lambda x: '🔴 Low Trust' if x else '🟢 Trusted')
display_df = display_df.drop('low_trust_flag', axis=1)
display_df.columns = ['Review Text', 'Rating', 'Trust Score', 'Verified', 'Status']

st.dataframe(
    display_df,
    use_container_width=True,
    height=400
)

st.divider()

# ============================================================================
# SECTION 3 — PRODUCT SCORE COMPARISON
# ============================================================================

st.header("⚖️ Section 3: Product Score Comparison")

# Guard: Ensure a product has been selected
if 'selected_product' not in st.session_state or st.session_state.selected_product is None:
    st.info("👆 Search for a product above and click **Analyze** to see comparison.")
    st.stop()

# Get product_id from session state
product_id = str(st.session_state.selected_product)

# Get product data
prod = products[products['product_id'].astype(str) == str(product_id)]

if len(prod) > 0:
    avg_rating = prod['avg_rating'].values[0]
    trust_score = prod['score_trust_weighted'].values[0]
    review_count = prod['review_count'].values[0] if 'review_count' in prod.columns else len(filtered_reviews)
    
    # Calculate and show difference prominently
    difference = trust_score - avg_rating
    
    st.subheader("Score Comparison")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "⭐ Average Rating",
            f"{avg_rating:.2f}",
            help="Simple average of all ratings"
        )
    
    with col2:
        st.metric(
            "🧠 Trust-Weighted Score",
            f"{trust_score:.2f}",
            delta=f"{difference:+.2f}",
            help="Rating weighted by review trust scores"
        )
    
    with col3:
        st.metric(
            "📊 Difference",
            f"{difference:+.2f}",
            delta=f"{abs(difference):.2f}",
            delta_color="normal" if difference > 0 else "inverse",
            help="Trust score - Average rating"
        )
    
    # Visual comparison chart
    st.subheader("Visual Comparison")
    comparison_chart = pd.DataFrame({
        'Average Rating': [avg_rating],
        'Trust-Weighted Score': [trust_score]
    })
    st.bar_chart(comparison_chart.T)
    
    # Explanation
    if difference > 0:
        st.success(f"✅ Trust-weighted score is **higher** by {abs(difference):.2f} points. High-quality reviews boost this product.")
    elif difference < 0:
        st.warning(f"⚠️ Trust-weighted score is **lower** by {abs(difference):.2f} points. Low-quality reviews may be inflating the average.")
    else:
        st.info("ℹ️ Trust-weighted score matches the average rating.")
    
    # Additional metrics
    st.subheader("Additional Product Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**Review Count:** {review_count}")
    with col2:
        if 'rating_std' in prod.columns:
            st.write(f"**Rating Std Dev:** {prod['rating_std'].values[0]:.3f}")
    with col3:
        if 'score_raw_avg' in prod.columns:
            st.write(f"**Raw Avg Score:** {prod['score_raw_avg'].values[0]:.3f}")
else:
    st.error("Product data not found!")

st.divider()

# ============================================================================
# SECTION 4 — TOP RECOMMENDED PRODUCTS
# ============================================================================

st.header("🏆 Section 4: Top Recommended Products")

st.subheader("Top 10 Products by Trust-Weighted Score")

# Get top products
top_products = products.sort_values(by="score_trust_weighted", ascending=False).head(10)

# Prepare display
top_display = top_products[['product_id', 'review_count', 'avg_rating', 'score_trust_weighted']].copy()
top_display['score_trust_weighted'] = top_display['score_trust_weighted'].round(3)
top_display['avg_rating'] = top_display['avg_rating'].round(2)
top_display.columns = ['Product ID', 'Review Count', 'Avg Rating', 'Trust Score']

# Add rank
top_display.insert(0, 'Rank', range(1, len(top_display) + 1))

st.dataframe(
    top_display,
    use_container_width=True,
    hide_index=True
)

# Comparison with rating-based ranking
st.subheader("Comparison: Trust-Based vs Rating-Based Ranking")

col1, col2 = st.columns(2)

with col1:
    st.write("**Top 10 by Trust Score**")
    trust_top = products.sort_values(by="score_trust_weighted", ascending=False).head(10)
    trust_display = trust_top[['product_id', 'score_trust_weighted']].copy()
    trust_display['score_trust_weighted'] = trust_display['score_trust_weighted'].round(3)
    trust_display.columns = ['Product ID', 'Trust Score']
    trust_display.insert(0, 'Rank', range(1, 11))
    st.dataframe(trust_display, hide_index=True, use_container_width=True)

with col2:
    st.write("**Top 10 by Average Rating**")
    rating_top = products.sort_values(by="avg_rating", ascending=False).head(10)
    rating_display = rating_top[['product_id', 'avg_rating']].copy()
    rating_display['avg_rating'] = rating_display['avg_rating'].round(2)
    rating_display.columns = ['Product ID', 'Avg Rating']
    rating_display.insert(0, 'Rank', range(1, 11))
    st.dataframe(rating_display, hide_index=True, use_container_width=True)

# Show ranking differences
trust_ids = set(trust_top['product_id'].values)
rating_ids = set(rating_top['product_id'].values)
common = trust_ids & rating_ids
only_trust = trust_ids - rating_ids
only_rating = rating_ids - trust_ids

st.info(f"""
**Ranking Comparison:**
- Products in both top 10: **{len(common)}**
- Only in trust-based top 10: **{len(only_trust)}**
- Only in rating-based top 10: **{len(only_rating)}**

This shows how trust-based ranking differs from simple rating averages.
""")

st.divider()

# ============================================================================
# SECTION 5 — IMPROVED UI FLOW: DYNAMIC PRODUCT ANALYSIS
# ============================================================================

st.header("🎯 Section 5: Dynamic Product Analysis & Review Addition")
st.markdown("""
**Complete workflow:** Select a product → View current metrics → Add a new review → See instant impact on rankings!
""")

# Show added reviews count and reset button
col_info1, col_info2 = st.columns([3, 1])
with col_info1:
    if len(st.session_state.added_reviews) > 0:
        st.info(f"📝 **{len(st.session_state.added_reviews)} review(s) added** in this session (cumulative impact shown)")
with col_info2:
    if len(st.session_state.added_reviews) > 0:
        if st.button("🗑️ Clear All Added Reviews", key="clear_added_reviews", help="Reset to original dataset"):
            st.session_state.added_reviews = []
            st.success("✅ All added reviews cleared!")
            st.rerun()

# Show Review History table if reviews have been added
if len(st.session_state.added_reviews) > 0:
    st.markdown("### 📋 Review History (This Session)")
    
    # Create DataFrame from added reviews
    history_data = []
    for i, review in enumerate(st.session_state.added_reviews, 1):
        history_data.append({
            '#': i,
            'Review Text': review['review_text'][:50] + '...' if len(review['review_text']) > 50 else review['review_text'],
            'Rating': '⭐' * int(review['rating']),
            'Trust Score': f"{review['trust_score']:.3f}",
            'Verified': '✓' if review['verified'] else '✗',
            'Product': review['product_id'][:10] + '...'
        })
    
    history_df = pd.DataFrame(history_data)
    
    # Display table
    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            '#': st.column_config.NumberColumn('#', width='small'),
            'Review Text': st.column_config.TextColumn('Review Text', width='large'),
            'Rating': st.column_config.TextColumn('Rating', width='small'),
            'Trust Score': st.column_config.TextColumn('Trust Score', width='small'),
            'Verified': st.column_config.TextColumn('Verified', width='small'),
            'Product': st.column_config.TextColumn('Product', width='medium')
        }
    )
    
    st.caption(f"💡 Showing all {len(st.session_state.added_reviews)} review(s) added in this session. Use the table above to track your demo scenario.")

st.divider()

# ============================================================================
# 1️⃣ PRODUCT INFO
# ============================================================================

st.subheader("1️⃣ Product Information")

# Use the product already selected in the search section
if 'selected_product' in st.session_state and st.session_state.selected_product:
    selected_product_dynamic = str(st.session_state.selected_product)
    
    # Get product name for display
    meta_row = product_metadata[product_metadata['product_id'] == selected_product_dynamic]
    product_name = meta_row.iloc[0]['product_name'] if len(meta_row) > 0 else selected_product_dynamic
    
    st.info(f"📦 **Analyzing:** {product_name} (ID: {selected_product_dynamic})")
    st.caption("💡 To analyze a different product, use the search section above")
else:
    # Fallback to first product if nothing selected
    selected_product_dynamic = str(products['product_id'].iloc[0])
    st.warning("⚠️ No product selected. Using first product as default. Please use the search section above to select a specific product.")

# Display full product information
st.markdown("---")
display_product_info(selected_product_dynamic, show_image=True, show_details=True)

st.divider()

# ============================================================================
# 2️⃣ PRODUCT SCORES (CURRENT STATE)
# ============================================================================

st.subheader("2️⃣ Current Product Scores")

if selected_product_dynamic:
    # Build current reviews including any added reviews from session state
    if st.session_state.added_reviews:
        added_df = pd.DataFrame(st.session_state.added_reviews)
        current_revs_with_added = pd.concat([reviews, added_df], ignore_index=True)
        current_revs = current_revs_with_added[current_revs_with_added['product_id'] == selected_product_dynamic]
    else:
        current_revs = reviews[reviews['product_id'] == selected_product_dynamic]
    
    # Get original product data for comparison
    current_prod = products[products['product_id'] == selected_product_dynamic]
    
    # Initialize current_rank with default value (prevents NameError if product not found)
    current_rank = len(products)  # Default to last position
    
    if len(current_prod) > 0:
        # Calculate current metrics (with added reviews if any)
        added_count_for_product = len([r for r in st.session_state.added_reviews if r['product_id'] == selected_product_dynamic])
        
        if len(current_revs) > 0:
            current_avg_rating = current_revs['rating'].mean()
            current_review_count = len(current_revs)
            
            # Use CSV value for baseline, only recalculate if reviews have been added
            if added_count_for_product > 0:
                # Recalculate trust score with added reviews
                current_trust_score = (current_revs['rating'] * current_revs['trust_score']).sum() / current_revs['trust_score'].sum()
            else:
                # Use pre-computed CSV value (includes Bayesian smoothing from notebook)
                current_trust_score = current_prod['score_trust_weighted'].iloc[0]
        else:
            current_avg_rating = current_prod['avg_rating'].iloc[0]
            current_trust_score = current_prod['score_trust_weighted'].iloc[0]
            current_review_count = 0
        
        # Get original metrics for delta calculation
        original_avg_rating = current_prod['avg_rating'].iloc[0]
        original_trust_score = current_prod['score_trust_weighted'].iloc[0]
        original_review_count = len(reviews[reviews['product_id'] == selected_product_dynamic])
        
        # Calculate deltas
        rating_delta = current_avg_rating - original_avg_rating if added_count_for_product > 0 else 0
        trust_delta = current_trust_score - original_trust_score if added_count_for_product > 0 else 0
        
        # Display current metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📊 Total Reviews",
                current_review_count,
                delta=f"+{added_count_for_product}" if added_count_for_product > 0 else None,
                help="Number of reviews for this product (including added reviews)"
            )
        
        with col2:
            st.metric(
                "⭐ Average Rating",
                f"{current_avg_rating:.2f}",
                delta=f"{rating_delta:+.2f}" if added_count_for_product > 0 else None,
                delta_color="normal" if rating_delta >= 0 else "inverse",
                help="Simple average of all ratings (including added reviews)"
            )
        
        with col3:
            st.metric(
                "🧠 Trust Score",
                f"{current_trust_score:.2f}",
                delta=f"{trust_delta:+.2f}" if added_count_for_product > 0 else None,
                delta_color="normal" if trust_delta >= 0 else "inverse",
                help="Trust-weighted score (our system, including added reviews)"
            )
        
        with col4:
            score_diff = current_trust_score - current_avg_rating
            st.metric(
                "📈 Difference",
                f"{score_diff:+.2f}",
                help="Trust score - Average rating"
            )
        
        # Show current ranking position
        st.markdown("**Current Ranking Position:**")
        products_sorted = products.sort_values('score_trust_weighted', ascending=False).reset_index(drop=True)
        current_rank = products_sorted[products_sorted['product_id'] == selected_product_dynamic].index[0] + 1
        total_products = len(products_sorted)
        
        st.info(f"🏆 This product is ranked **#{current_rank}** out of {total_products} products (by trust score)")

st.divider()

# ============================================================================
# 3️⃣ ADD NEW REVIEW
# ============================================================================

st.subheader("3️⃣ Add New Review")

if selected_product_dynamic:
    st.markdown("Enter a new review for this product and see how it affects the trust score and ranking!")
    
    # Demo instructions
    st.info("💡 **Demo Tip:** Click '🔴 Fake Review' 3 times and watch the trust score drop while the average rating stays high. This demonstrates the system's ability to detect and downweight suspicious reviews!")
    
    # Review input
    col_input1, col_input2 = st.columns([2, 1])
    
    with col_input1:
        # Preset buttons for demo (placed before text area)
        st.markdown("**Quick Demo Presets:**")
        col_preset1, col_preset2 = st.columns(2)
        
        with col_preset1:
            if st.button("🟢 Genuine Review", use_container_width=True, help="Load a realistic, trustworthy review"):
                st.session_state.preset_review_text = "Great product, fits well, fast delivery. Exactly as described. Would buy again."
                st.session_state.preset_rating = 5
                st.session_state.preset_verified = True
                st.rerun()
        
        with col_preset2:
            if st.button("🔴 Fake Review", use_container_width=True, help="Load a suspicious, low-quality review"):
                st.session_state.preset_review_text = "AMAZING!!! BEST PRODUCT EVER!!!! 5 STARS!!!! BUY NOW!!!!"
                st.session_state.preset_rating = 5
                st.session_state.preset_verified = False
                st.rerun()
        
        # Review text with preset value
        default_text = st.session_state.get('preset_review_text', '')
        new_review_text = st.text_area(
            "Review Text:",
            value=default_text,
            placeholder="e.g., 'This product exceeded my expectations! Great quality and fast shipping.'",
            height=120,
            help="Enter your review text (minimum 3 characters)"
        )
        
        # Rating with preset value
        default_rating = st.session_state.get('preset_rating', 5)
        new_rating = st.slider(
            "Rating (1-5 stars):",
            min_value=1,
            max_value=5,
            value=default_rating,
            help="Select your rating"
        )
        
        # Verified purchase with preset value
        default_verified = st.session_state.get('preset_verified', True)
        new_verified = st.checkbox(
            "✓ Verified Purchase",
            value=default_verified,
            help="Is this a verified purchase?"
        )
    
    with col_input2:
        st.markdown("**Advanced Options**")
        
        with st.expander("⚙️ Optional Settings"):
            new_helpful_votes = st.number_input(
                "Helpful Votes:",
                min_value=0,
                value=0,
                key="helpful_votes_dynamic"
            )
            
            new_user_review_count = st.number_input(
                "User's Total Reviews:",
                min_value=1,
                value=1,
                key="user_reviews_dynamic"
            )
    
    # Predict and add button
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        predict_button = st.button(
            "🔮 Predict Trust Score",
            type="primary",
            use_container_width=True,
            key="predict_dynamic"
        )
    
    with col_btn2:
        add_to_dataset = st.checkbox(
            "📊 Add to dataset",
            value=True,
            key="add_dataset_dynamic",
            help="Update product ranking with this review"
        )
    
    # Process prediction
    if predict_button:
        # Clear preset values after use
        if 'preset_review_text' in st.session_state:
            st.session_state.preset_review_text = ''
        if 'preset_rating' in st.session_state:
            st.session_state.preset_rating = 5
        if 'preset_verified' in st.session_state:
            st.session_state.preset_verified = True
        
        if not new_review_text or len(new_review_text.strip()) < 3:
            st.error("❌ Please enter a review with at least 3 characters")
        else:
            with st.spinner("🧠 Analyzing review..."):
                # Predict trust score
                predicted_trust = predict_trust_score(
                    review_text=new_review_text,
                    rating=new_rating,
                    verified=new_verified,
                    helpful_votes=new_helpful_votes,
                    user_review_count=new_user_review_count,
                    product_review_count=current_review_count
                )
                
                # Display prediction result
                st.success("✅ Trust score predicted successfully!")
                
                # Show predicted trust score
                col_result1, col_result2, col_result3 = st.columns(3)
                
                with col_result1:
                    st.metric(
                        "🧠 Predicted Trust Score",
                        f"{predicted_trust:.4f}",
                        help="Trust score for this review (0-1 scale)"
                    )
                
                with col_result2:
                    trust_percentage = predicted_trust * 100
                    st.metric(
                        "📊 Trust Percentage",
                        f"{trust_percentage:.1f}%",
                        help="Trust score as percentage"
                    )
                
                with col_result3:
                    # Classify trust level
                    if predicted_trust >= 0.7:
                        trust_level = "🟢 High Trust"
                    elif predicted_trust >= 0.4:
                        trust_level = "🟡 Medium Trust"
                    else:
                        trust_level = "🔴 Low Trust"
                    
                    st.metric(
                        "🎯 Trust Level",
                        trust_level,
                        help="Classification based on trust score"
                    )
                
                # Interpretation
                if predicted_trust >= 0.7:
                    st.success("**High Trust Review** - This review appears genuine and trustworthy.")
                elif predicted_trust >= 0.4:
                    st.info("**Medium Trust Review** - This review has some trustworthy characteristics.")
                else:
                    st.warning("**Low Trust Review** - This review shows suspicious patterns.")
                
                st.divider()
                
                # ============================================================================
                # 4️⃣ UPDATED REVIEWS (IF ADDED TO DATASET)
                # ============================================================================
                
                if add_to_dataset:
                    st.subheader("4️⃣ Updated Reviews (Sorted by Trust)")
                    
                    # Generate unique user_id for this review (timestamp-based for uniqueness)
                    new_user_id = f'NEW_USER_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}'
                    
                    # Create new review row
                    new_review_row = {
                        'user_id': new_user_id,
                        'product_id': selected_product_dynamic,
                        'rating': new_rating,
                        'review_text': new_review_text,
                        'verified': new_verified,
                        'helpful_votes': new_helpful_votes,
                        'trust_score': predicted_trust,
                        'predicted_trust_score': predicted_trust
                    }
                    
                    # Add to session state for persistence
                    st.session_state.added_reviews.append(new_review_row)
                    
                    # Build updated reviews dataframe with all added reviews
                    if st.session_state.added_reviews:
                        added_df = pd.DataFrame(st.session_state.added_reviews)
                        reviews_updated = pd.concat([reviews, added_df], ignore_index=True)
                    else:
                        reviews_updated = reviews.copy()
                    
                    # Get updated product reviews
                    product_reviews_updated = reviews_updated[reviews_updated['product_id'] == selected_product_dynamic]
                    product_reviews_updated = product_reviews_updated.sort_values('trust_score', ascending=False)
                    
                    # Show updated review count with cumulative count
                    added_count = len([r for r in st.session_state.added_reviews if r['product_id'] == selected_product_dynamic])
                    st.info(f"📊 Total reviews for this product: **{len(product_reviews_updated)}** (including {added_count} new review{'s' if added_count > 1 else ''})")
                    
                    # Display top reviews
                    st.markdown("**Top 5 Reviews by Trust Score:**")
                    
                    top_reviews = product_reviews_updated.head(5)
                    
                    # Get list of new user IDs for highlighting
                    new_user_ids = [r['user_id'] for r in st.session_state.added_reviews]
                    
                    for idx, (_, review) in enumerate(top_reviews.iterrows(), 1):
                        # Highlight the new reviews
                        if review['user_id'] in new_user_ids:
                            st.markdown(f"**🆕 #{idx} - Your New Review** (Trust: {review['trust_score']:.3f})")
                            with st.container():
                                st.markdown(f"**Rating:** {'⭐' * int(review['rating'])}")
                                st.markdown(f"**Review:** {review['review_text'][:200]}...")
                                st.markdown(f"**Verified:** {'✓' if review['verified'] else '✗'}")
                        else:
                            st.markdown(f"**#{idx}** (Trust: {review['trust_score']:.3f})")
                            with st.expander(f"View Review #{idx}"):
                                st.markdown(f"**Rating:** {'⭐' * int(review['rating'])}")
                                st.markdown(f"**Review:** {review['review_text'][:200]}...")
                                st.markdown(f"**Verified:** {'✓' if review['verified'] else '✗'}")
                    
                    st.divider()
                    
                    # ============================================================================
                    # 5️⃣ RANKING IMPACT (BEFORE VS AFTER)
                    # ============================================================================
                    
                    st.subheader("5️⃣ Ranking Impact: Before vs After")
                    
                    # Calculate new product metrics using all added reviews
                    new_avg_rating = product_reviews_updated['rating'].mean()
                    new_trust_weighted_score = (product_reviews_updated['rating'] * product_reviews_updated['trust_score']).sum() / product_reviews_updated['trust_score'].sum()
                    new_review_count = len(product_reviews_updated)
                    
                    # Calculate changes (cumulative)
                    rating_change = new_avg_rating - current_avg_rating
                    trust_change = new_trust_weighted_score - current_trust_score
                    review_count_change = added_count
                    
                    # Display before/after comparison
                    st.markdown("**📊 Score Changes:**")
                    
                    col_comp1, col_comp2, col_comp3 = st.columns(3)
                    
                    with col_comp1:
                        st.metric(
                            "📊 Total Reviews",
                            new_review_count,
                            delta=f"+{review_count_change}",
                            help=f"Review count increased by {review_count_change}"
                        )
                    
                    with col_comp2:
                        st.metric(
                            "⭐ Average Rating",
                            f"{new_avg_rating:.2f}",
                            delta=f"{rating_change:+.2f}",
                            delta_color="normal" if rating_change >= 0 else "inverse",
                            help="Change in average rating"
                        )
                    
                    with col_comp3:
                        st.metric(
                            "🧠 Trust Score",
                            f"{new_trust_weighted_score:.2f}",
                            delta=f"{trust_change:+.2f}",
                            delta_color="normal" if trust_change >= 0 else "inverse",
                            help="Change in trust-weighted score"
                        )
                    
                    # Visual comparison
                    st.markdown("**📈 Visual Comparison:**")
                    
                    comparison_df = pd.DataFrame({
                        'Before': [current_avg_rating, current_trust_score],
                        'After': [new_avg_rating, new_trust_weighted_score]
                    }, index=['Avg Rating', 'Trust Score'])
                    
                    st.bar_chart(comparison_df)
                    
                    # Impact interpretation
                    st.markdown("**💡 Impact Analysis:**")
                    
                    if trust_change > 0:
                        st.success(f"""
                        **Positive Impact!** 🎉
                        - Your review improved the product's trust score by **{trust_change:.3f}** points
                        - The review has high trust ({predicted_trust:.3f})
                        - Product ranking will improve in trust-based recommendations
                        """)
                    elif trust_change < 0:
                        st.warning(f"""
                        **Negative Impact** ⚠️
                        - Your review decreased the product's trust score by **{abs(trust_change):.3f}** points
                        - The review has lower trust ({predicted_trust:.3f})
                        - Product ranking will decrease in trust-based recommendations
                        """)
                    else:
                        st.info(f"""
                        **Neutral Impact** ℹ️
                        - Your review maintained the product's trust score
                        - The review's trust ({predicted_trust:.3f}) matches the product average
                        """)
                    
                    # Updated ranking position
                    st.markdown("**🏆 Updated Ranking Position:**")
                    
                    # Update products dataframe
                    products_updated = products.copy()
                    mask = products_updated['product_id'] == selected_product_dynamic
                    if mask.any():
                        products_updated.loc[mask, 'avg_rating'] = new_avg_rating
                        products_updated.loc[mask, 'score_trust_weighted'] = new_trust_weighted_score
                    
                    # Calculate new ranking
                    products_sorted_new = products_updated.sort_values('score_trust_weighted', ascending=False).reset_index(drop=True)
                    new_rank = products_sorted_new[products_sorted_new['product_id'] == selected_product_dynamic].index[0] + 1
                    rank_change = current_rank - new_rank
                    
                    col_rank1, col_rank2 = st.columns(2)
                    
                    with col_rank1:
                        st.metric(
                            "Previous Rank",
                            f"#{current_rank}",
                            help="Ranking before adding review"
                        )
                    
                    with col_rank2:
                        st.metric(
                            "New Rank",
                            f"#{new_rank}",
                            delta=f"{rank_change:+d} positions" if rank_change != 0 else "No change",
                            delta_color="normal" if rank_change > 0 else "inverse" if rank_change < 0 else "off",
                            help="Ranking after adding review"
                        )
                    
                    if rank_change > 0:
                        st.success(f"🎉 Product moved up {rank_change} position(s) in the ranking!")
                    elif rank_change < 0:
                        st.warning(f"⚠️ Product moved down {abs(rank_change)} position(s) in the ranking.")
                    else:
                        st.info("ℹ️ Product ranking position unchanged.")
                    
                    # Show top 10 with highlighting
                    st.markdown("**📋 Updated Top 10 Products:**")
                    
                    top_10_updated = products_sorted_new.head(10)[['product_id', 'score_trust_weighted', 'avg_rating']].copy()
                    top_10_updated['score_trust_weighted'] = top_10_updated['score_trust_weighted'].round(3)
                    top_10_updated['avg_rating'] = top_10_updated['avg_rating'].round(2)
                    top_10_updated.columns = ['Product ID', 'Trust Score', 'Avg Rating']
                    top_10_updated.insert(0, 'Rank', range(1, len(top_10_updated) + 1))
                    
                    # Highlight the updated product
                    def highlight_updated_product(row):
                        if row['Product ID'] == selected_product_dynamic:
                            return ['background-color: #90EE90'] * len(row)
                        return [''] * len(row)
                    
                    st.dataframe(
                        top_10_updated.style.apply(highlight_updated_product, axis=1),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    st.info(f"💡 **Product {selected_product_dynamic}** is highlighted in green")
                    
                    # Note about persistence
                    st.warning("""
                    ⚠️ **Note:** This update is temporary and only affects the current session.
                    In a production system, changes would be persisted to a database.
                    Refresh the page to reset to original data.
                    """)
                
                else:
                    st.info("💡 Check 'Add to dataset' to see the impact on product ranking!")

else:
    st.info("👆 Please select a product above to begin")

st.divider()

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("🧠 Trust-Based Product Recommendation System | Built with Streamlit")
st.caption("💡 This demo uses machine learning to identify trustworthy reviews and rank products accordingly.")

