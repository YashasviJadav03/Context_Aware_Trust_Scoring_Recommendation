"""
Trust-Based Product Recommendation System
Simple, Clean, and Effective
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from textblob import TextBlob

# ============================================================================
# CONFIG
# ============================================================================

st.set_page_config(page_title="Trust-Based Recommendations", page_icon="🛍️", layout="wide")

st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1e3a8a;
        --secondary-color: #3b82f6;
        --success-color: #059669;
        --warning-color: #d97706;
        --danger-color: #dc2626;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
    }
    
    /* Trust score colors */
    .trust-high { 
        color: #059669; 
        font-weight: 700; 
        font-size: 1.2em; 
    }
    .trust-medium { 
        color: #d97706; 
        font-weight: 700; 
        font-size: 1.2em; 
    }
    .trust-low { 
        color: #dc2626; 
        font-weight: 700; 
        font-size: 1.2em; 
    }
    
    /* Metric boxes */
    .metric-box { 
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
    }
    
    .metric-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Product cards */
    .product-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.2s;
    }
    
    .product-card:hover {
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        border-color: #3b82f6;
    }
    
    /* Review cards */
    .review-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.75rem;
        border-left: 3px solid #cbd5e1;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        font-size: 0.85rem;
    }
    
    .review-card.high-trust {
        border-left-color: #059669;
        background: #f0fdf4;
    }
    
    .review-card.medium-trust {
        border-left-color: #d97706;
        background: #fffbeb;
    }
    
    .review-card.low-trust {
        border-left-color: #dc2626;
        background: #fef2f2;
    }
    
    /* Scrollable reviews container */
    .reviews-scroll-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.02);
    }
    
    .reviews-scroll-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .reviews-scroll-container::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    .reviews-scroll-container::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    .reviews-scroll-container::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    /* Info badges */
    .info-badge {
        background: #dbeafe;
        color: #1e40af;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    /* Stats container */
    .stats-container {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    /* Streamlit override */
    .stExpander {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    
    .stButton>button {
        background: #3b82f6;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background: #2563eb;
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
    }
    
    /* Product image container */
    .product-image {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA & MODELS
# ============================================================================

@st.cache_resource
def load_models():
    import os
    try:
        tfidf = joblib.load("models/tfidf_vectorizer.pkl")
        scaler = joblib.load("models/feature_scaler.pkl")
        model = joblib.load("models/trained/best_trust_model.pkl")
        return tfidf, scaler, model
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None, None

@st.cache_resource
def get_db_connection():
    """Get database connection"""
    import sqlite3
    import os
    
    db_path = 'data/processed/reviews.db'
    
    # Check if database exists and has data
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            if tables:
                return conn
        except:
            pass
    
    # If database doesn't exist or is empty, return None
    return None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    """Load products metadata"""
    try:
        conn = get_db_connection()
        
        if conn:
            # Use database if available
            products = pd.read_sql("SELECT * FROM products", conn)
            return products
        else:
            # Fallback to CSV
            products = pd.read_csv("data/processed/product_trust_scores.csv")
            return products
    except Exception as e:
        # Final fallback to CSV
        try:
            products = pd.read_csv("data/processed/product_trust_scores.csv")
            return products
        except:
            st.error(f"Error loading data: {e}")
            st.stop()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_product_reviews(product_id):
    """Load all reviews for a specific product - FAST with indexed database"""
    try:
        conn = get_db_connection()
        
        if conn:
            # Use database if available
            query = "SELECT * FROM reviews WHERE product_id = ?"
            reviews = pd.read_sql(query, conn, params=(product_id,))
            if len(reviews) > 0:
                # DEBUG: Log trust score range
                st.sidebar.write(f"DEBUG: Loaded {len(reviews)} reviews from DB")
                st.sidebar.write(f"Trust range: {reviews['trust_score'].min():.3f} - {reviews['trust_score'].max():.3f}")
                return reviews
        
        # Fallback to sample CSV
        reviews_sample = pd.read_csv("data/processed/reviews_sample.csv")
        filtered = reviews_sample[reviews_sample['product_id'] == product_id]
        # DEBUG: Log trust score range from CSV
        if len(filtered) > 0:
            st.sidebar.write(f"DEBUG: Loaded {len(filtered)} reviews from CSV")
            st.sidebar.write(f"Trust range: {filtered['trust_score'].min():.3f} - {filtered['trust_score'].max():.3f}")
        return filtered
        
    except Exception as e:
        # Fallback to sample CSV
        st.sidebar.error(f"DEBUG ERROR: {str(e)}")
        reviews_sample = pd.read_csv("data/processed/reviews_sample.csv")
        return reviews_sample[reviews_sample['product_id'] == product_id]

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_sample_reviews(limit=10000):
    """Load sample reviews for recommendations display"""
    try:
        conn = get_db_connection()
        
        if conn:
            # Use database if available
            query = "SELECT * FROM reviews ORDER BY RANDOM() LIMIT ?"
            reviews = pd.read_sql(query, conn, params=(limit,))
            if len(reviews) > 0:
                return reviews
        
        # Fallback to sample CSV
        return pd.read_csv("data/processed/reviews_sample.csv")
        
    except Exception as e:
        # Fallback to sample CSV
        return pd.read_csv("data/processed/reviews_sample.csv")

def get_trust_color(score):
    if score >= 0.7: return "trust-high"
    elif score >= 0.4: return "trust-medium"
    else: return "trust-low"

def safe_get(row, column, default=''):
    """Safely get column value, return default if column doesn't exist"""
    try:
        return row[column] if column in row.index and pd.notna(row[column]) and row[column] else default
    except:
        return default

def extract_features(text, rating, verified):
    """Extract features for prediction"""
    if pd.isna(text) or text == "":
        return None
    
    blob = TextBlob(str(text))
    words = text.split()
    
    return {
        'rating': rating,
        'verified': 1 if verified else 0,
        'review_length': len(text),
        'word_count': len(words),
        'avg_word_length': np.mean([len(w) for w in words]) if words else 0,
        'sentiment_polarity': blob.sentiment.polarity,
        'sentiment_subjectivity': blob.sentiment.subjectivity,
        'exclamation_count': text.count('!'),
        'question_count': text.count('?'),
        'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if len(text) > 0 else 0
    }

# Load everything
tfidf_vec, scaler, model = load_models()
products_df = load_data()
reviews_df = load_sample_reviews(10000)  # Sample for recommendations

# Check if using database or fallback
conn = get_db_connection()
if conn:
    st.sidebar.success("✅ Using full database (883K reviews)")
else:
    st.sidebar.info("ℹ️ Using sample data (10K reviews)")

# Add cache clear button
if st.sidebar.button("🔄 Clear Cache & Refresh Data"):
    st.cache_data.clear()
    st.rerun()

if products_df is None or len(products_df) == 0:
    st.error("Failed to load data. Please check database exists.")
    st.stop()

# ============================================================================
# HEADER
# ============================================================================

# Main header with gradient background
st.markdown("""
<div class="main-header">
    <h1>🛍️ Trust-Based Product Recommendation System</h1>
    <p>Advanced AI-Powered Review Analysis & Trust Scoring Platform</p>
</div>
""", unsafe_allow_html=True)

# Model Performance Metrics
st.markdown('<div class="stats-container">', unsafe_allow_html=True)
st.markdown("### 📊 System Overview")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Products", f"{len(products_df):,}", help="Unique products analyzed")
with col2:
    st.metric("Total Reviews", f"{len(reviews_df):,}", help="Reviews processed")
with col3:
    avg_reviews = reviews_df.groupby('product_id').size().mean()
    st.metric("Avg Reviews/Product", f"{avg_reviews:.0f}", help="Average reviews per product")
with col4:
    st.metric("Model R² Score", "0.847", help="84.7% variance explained", delta="High Accuracy")
with col5:
    st.metric("Model MAE", "0.082", help="Mean Absolute Error", delta="-0.082", delta_color="inverse")

st.info("ℹ️ **Model Performance**: Our XGBoost model achieves R² = 0.847, explaining 84.7% of trust score variance with MAE = 0.082 (±8.2% prediction accuracy).")
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ============================================================================
# PRODUCT SEARCH & ANALYSIS
# ============================================================================

st.markdown('<p class="section-header">🔎 Product Search & Analysis</p>', unsafe_allow_html=True)

# Check if product_name column exists
has_product_names = 'product_name' in products_df.columns

# Search input with toggle for search type
col1, col2 = st.columns([3, 1])
with col1:
    if has_product_names:
        search_input = st.text_input(
            "Search Products",
            placeholder="e.g., 'tungsten ring' or 'B00008JPRZ'",
            help="Search by product name or ID"
        )
    else:
        search_input = st.text_input(
            "Search Products by ID",
            placeholder="e.g., B00008JPRZ",
            help="Enter a product ID to see detailed analysis"
        )
with col2:
    if has_product_names:
        search_type = st.radio(
            "Search by",
            ["Name", "ID"],
            horizontal=True
        )
    else:
        st.info("🔍 ID Search Only")
        search_type = "ID"

if search_input:
    # Search for products matching the input
    if search_type == "Name":
        search_results = products_df[products_df['product_name'].str.contains(search_input, case=False, na=False)]
    else:
        search_results = products_df[products_df['product_id'].str.contains(search_input, case=False, na=False)]
    
    if len(search_results) > 0:
        st.success(f"✅ Found {len(search_results)} product(s) matching '{search_input}'")
        
        # If multiple results, show selection with product names
        if len(search_results) > 1:
            # Create display options with both name and ID
            display_options = []
            for _, row in search_results.iterrows():
                name = safe_get(row, 'product_name', 'Unknown Product')
                if name and name != 'Unknown Product':
                    display_options.append(f"{name[:60]}... ({row['product_id']})")
                else:
                    display_options.append(f"{row['product_id']}")
            
            selected_display = st.selectbox(
                "Select a product to analyze:",
                display_options
            )
            # Extract product_id from the selected display option
            if '(' in selected_display:
                selected_product_id = selected_display.split('(')[-1].strip(')')
            else:
                selected_product_id = selected_display
        else:
            selected_product_id = search_results['product_id'].iloc[0]
        
        # Get selected product data
        product = products_df[products_df['product_id'] == selected_product_id].iloc[0]
        
        # Load ALL reviews for this specific product
        with st.spinner(f"Loading all reviews for {selected_product_id}..."):
            product_reviews = load_product_reviews(selected_product_id)
        
        # Update review count to actual loaded reviews
        actual_review_count = len(product_reviews)
        
        # Display product header with image
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        col_img, col_info = st.columns([1, 3])
        
        with col_img:
            image_url = safe_get(product, 'image_url', None)
            if image_url:
                try:
                    st.markdown('<div class="product-image">', unsafe_allow_html=True)
                    st.image(image_url, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                except:
                    st.image("https://via.placeholder.com/300x300?text=No+Image", use_container_width=True)
            else:
                st.image("https://via.placeholder.com/300x300?text=No+Image", use_container_width=True)
        
        with col_info:
            product_name = safe_get(product, 'product_name', f'Product {selected_product_id}')
            st.markdown(f"## {product_name}")
            st.caption(f"**Product ID:** `{selected_product_id}`")
            brand = safe_get(product, 'brand', None)
            if brand:
                st.markdown(f'<span class="info-badge">🏷️ Brand: {brand}</span>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Product overview metrics
        st.markdown('<p class="section-header">📊 Product Performance Metrics</p>', unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            trust_class = get_trust_color(product['score_trust_weighted'])
            st.markdown(f"**Trust Score**")
            st.markdown(f"<span class='{trust_class}' style='font-size: 2em;'>{product['score_trust_weighted']:.3f}</span>", unsafe_allow_html=True)
        
        with col2:
            st.metric("Avg Rating", f"{product['avg_rating']:.2f}/5.0")
            st.progress(product['avg_rating'] / 5.0)
        
        with col3:
            st.metric("Total Reviews", actual_review_count)
        
        with col4:
            verified_pct = (product_reviews['verified'].sum() / len(product_reviews)) * 100
            st.metric("Verified", f"{verified_pct:.0f}%")
        
        with col5:
            rating_consistency = 5 - product['rating_std']
            st.metric("Consistency", f"{rating_consistency:.1f}/5.0")
        
        st.divider()
        
        # Review statistics
        st.markdown('<p class="section-header">📊 Review Distribution Statistics</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Trust score distribution
            st.markdown("**Trust Score Distribution**")
            trust_bins = pd.cut(product_reviews['trust_score'], bins=[0, 0.4, 0.7, 1.0], labels=['Low', 'Medium', 'High'])
            trust_counts = trust_bins.value_counts()
            
            for level in ['High', 'Medium', 'Low']:
                if level in trust_counts.index:
                    count = trust_counts[level]
                    pct = (count / len(product_reviews)) * 100
                    st.write(f"🟢 {level}: {count} ({pct:.0f}%)" if level == 'High' else 
                            f"🟡 {level}: {count} ({pct:.0f}%)" if level == 'Medium' else 
                            f"🔴 {level}: {count} ({pct:.0f}%)")
        
        with col2:
            # Rating distribution
            st.markdown("**Rating Distribution**")
            rating_counts = product_reviews['rating'].value_counts().sort_index(ascending=False)
            for rating in [5, 4, 3, 2, 1]:
                count = rating_counts.get(rating, 0)
                pct = (count / len(product_reviews)) * 100
                st.write(f"{'⭐' * rating}: {count} ({pct:.0f}%)")
        
        st.divider()
        
        # All reviews section
        st.markdown('<p class="section-header">📝 Customer Reviews</p>', unsafe_allow_html=True)
        
        # Review controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            sort_by = st.selectbox(
                "Sort by",
                ["Most Helpful (Trust)", "Highest Rating", "Lowest Rating", "Most Recent"],
                key="sort_select"
            )
        
        with col2:
            filter_verified = st.checkbox("✅ Verified Only", value=False, key="verified_check")
        
        with col3:
            filter_rating = st.selectbox(
                "Filter by Rating",
                ["All Ratings", "5 Stars", "4 Stars", "3 Stars", "2 Stars", "1 Star"],
                key="rating_filter"
            )
        
        with col4:
            reviews_per_page = st.selectbox(
                "Show",
                [10, 25, 50, 100],
                index=1,
                key="per_page"
            )
        
        # Reset page to 1 when filters/sort change
        filter_key = f"{sort_by}_{filter_verified}_{filter_rating}_{reviews_per_page}"
        if 'last_filter_key' not in st.session_state or st.session_state['last_filter_key'] != filter_key:
            st.session_state.page_number = 1
            st.session_state['last_filter_key'] = filter_key
        
        # Apply filters
        filtered_reviews = product_reviews.copy()
        
        if filter_verified:
            filtered_reviews = filtered_reviews[filtered_reviews['verified'] == True]
        
        if filter_rating != "All Ratings":
            rating_map = {"5 Stars": 5, "4 Stars": 4, "3 Stars": 3, "2 Stars": 2, "1 Star": 1}
            filtered_reviews = filtered_reviews[filtered_reviews['rating'] == rating_map[filter_rating]]
        
        # Sort
        if sort_by == "Most Helpful (Trust)":
            filtered_reviews = filtered_reviews.sort_values('trust_score', ascending=False)
        elif sort_by == "Highest Rating":
            filtered_reviews = filtered_reviews.sort_values(['rating', 'trust_score'], ascending=[False, False])
        elif sort_by == "Lowest Rating":
            filtered_reviews = filtered_reviews.sort_values(['rating', 'trust_score'], ascending=[True, False])
        elif sort_by == "Most Recent":
            # If timestamp column exists, sort by it, otherwise keep current order
            if 'timestamp' in filtered_reviews.columns:
                filtered_reviews = filtered_reviews.sort_values('timestamp', ascending=False)
            elif 'created_at' in filtered_reviews.columns:
                filtered_reviews = filtered_reviews.sort_values('created_at', ascending=False)
        
        # Pagination
        total_reviews = len(filtered_reviews)
        total_pages = (total_reviews + reviews_per_page - 1) // reviews_per_page
        
        if total_pages > 0:
            # Initialize page number in session state
            if 'page_number' not in st.session_state:
                st.session_state.page_number = 1
            
            # Pagination controls at top
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("⬅️ Previous", disabled=st.session_state.page_number <= 1, key="prev_top"):
                    st.session_state.page_number -= 1
                    st.rerun()
            
            with col2:
                st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.page_number} of {total_pages} ({total_reviews} reviews)</div>", unsafe_allow_html=True)
            
            with col3:
                if st.button("Next ➡️", disabled=st.session_state.page_number >= total_pages, key="next_top"):
                    st.session_state.page_number += 1
                    st.rerun()
            
            # Get current page reviews
            start_idx = (st.session_state.page_number - 1) * reviews_per_page
            end_idx = start_idx + reviews_per_page
            page_reviews = filtered_reviews.iloc[start_idx:end_idx]
            
            st.divider()
            
            # Display reviews in scrollable container using st.components
            import streamlit.components.v1 as components
            
            reviews_html = """
            <style>
                .reviews-scroll-container {
                    max-height: 600px;
                    overflow-y: auto;
                    padding: 1rem;
                    background: white;
                    border-radius: 10px;
                    border: 1px solid #e2e8f0;
                    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.02);
                }
                
                .reviews-scroll-container::-webkit-scrollbar {
                    width: 8px;
                }
                
                .reviews-scroll-container::-webkit-scrollbar-track {
                    background: #f1f5f9;
                    border-radius: 4px;
                }
                
                .reviews-scroll-container::-webkit-scrollbar-thumb {
                    background: #cbd5e1;
                    border-radius: 4px;
                }
                
                .reviews-scroll-container::-webkit-scrollbar-thumb:hover {
                    background: #94a3b8;
                }
                
                .review-card {
                    background: #f8fafc;
                    padding: 1rem;
                    border-radius: 8px;
                    margin-bottom: 0.75rem;
                    border-left: 3px solid #cbd5e1;
                    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
                    font-size: 0.85rem;
                }
                
                .review-card.high-trust {
                    border-left-color: #059669;
                    background: #f0fdf4;
                }
                
                .review-card.medium-trust {
                    border-left-color: #d97706;
                    background: #fffbeb;
                }
                
                .review-card.low-trust {
                    border-left-color: #dc2626;
                    background: #fef2f2;
                }
                
                .trust-high { color: #059669; font-weight: 700; }
                .trust-medium { color: #d97706; font-weight: 700; }
                .trust-low { color: #dc2626; font-weight: 700; }
            </style>
            <div class="reviews-scroll-container">
            """
            
            for idx, (_, review) in enumerate(page_reviews.iterrows(), start=start_idx + 1):
                review_trust_class = get_trust_color(review['trust_score'])
                trust_level = 'high-trust' if review['trust_score'] >= 0.7 else 'medium-trust' if review['trust_score'] >= 0.4 else 'low-trust'
                
                # Escape any HTML in review text
                review_text = str(review['review_text']).replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                
                # Review card
                reviews_html += f"""
                <div class='review-card {trust_level}'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
                        <div>
                            <span style='font-size: 0.9em; color: #f59e0b;'>{'⭐' * int(review['rating'])}</span>
                            <span style='color: #64748b; margin-left: 0.5rem; font-size: 0.75rem; font-weight: 600;'>{'✅ Verified' if review['verified'] else '❌ Unverified'}</span>
                        </div>
                        <div>
                            <span class='{review_trust_class}' style='font-size: 0.8em;'>Trust: {review['trust_score']:.4f}</span>
                        </div>
                    </div>
                    <div style='color: #334155; line-height: 1.5; font-size: 0.85rem;'>
                        {review_text}
                    </div>
                </div>
                """
            
            reviews_html += '</div>'
            components.html(reviews_html, height=620, scrolling=False)
            
            st.divider()
            
            # Pagination controls at bottom
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("⬅️ Previous", disabled=st.session_state.page_number <= 1, key="prev_bottom"):
                    st.session_state.page_number -= 1
                    st.rerun()
            
            with col2:
                # Page selector
                page_options = list(range(1, total_pages + 1))
                new_page = st.selectbox(
                    "Go to page:",
                    page_options,
                    index=st.session_state.page_number - 1,
                    key="page_select"
                )
                if new_page != st.session_state.page_number:
                    st.session_state.page_number = new_page
                    st.rerun()
            
            with col3:
                if st.button("Next ➡️", disabled=st.session_state.page_number >= total_pages, key="next_bottom"):
                    st.session_state.page_number += 1
                    st.rerun()
        
        else:
            st.warning("No reviews match your filters. Try adjusting the filters above.")
    
    else:
        st.warning(f"⚠️ No products found matching '{search_input}'. Try a different Product ID.")

st.divider()

# ============================================================================
# RECOMMENDATIONS
# ============================================================================

st.markdown('<p class="section-header">🎯 Discover Trustworthy Products</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    min_trust = st.slider("Minimum Trust Score", 0.0, 1.0, 0.65, 0.05)
with col2:
    min_reviews = st.slider("Minimum Reviews", 5, 30, 12)

# Filter products
filtered = products_df[
    (products_df['score_trust_weighted'] >= min_trust) &
    (products_df['review_count'] >= min_reviews)
].sort_values('score_trust_weighted', ascending=False)

st.success(f"✅ Found **{len(filtered)}** products with trust ≥ {min_trust:.2f} and ≥ {min_reviews} reviews")

# Show top products
if len(filtered) > 0:
    for idx, (_, prod) in enumerate(filtered.head(15).iterrows(), 1):
        trust_class = get_trust_color(prod['score_trust_weighted'])
        
        # Get product name safely
        prod_name = safe_get(prod, 'product_name', f'Product {prod["product_id"]}')
        
        with st.expander(f"**#{idx}. {prod_name[:60]}{'...' if len(prod_name) > 60 else ''}** - Trust: {prod['score_trust_weighted']:.3f} | Rating: {prod['avg_rating']:.1f}⭐"):
            
            # Product image and info
            col_img, col_details = st.columns([1, 3])
            
            with col_img:
                image_url = safe_get(prod, 'image_url', None)
                if image_url:
                    try:
                        st.image(image_url, use_container_width=True)
                    except:
                        st.write("📦 No Image")
                else:
                    st.write("📦 No Image")
            
            with col_details:
                st.markdown(f"**{prod_name}**")
                st.caption(f"Product ID: {prod['product_id']}")
                brand = safe_get(prod, 'brand', None)
                if brand:
                    st.caption(f"Brand: {brand}")
            
            st.markdown("---")
            
            # Product metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"<div class='metric-box'><span class='{trust_class}'>{prod['score_trust_weighted']:.3f}</span><br>Trust Score</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='metric-box'><strong>{prod['avg_rating']:.2f}/5.0</strong><br>Avg Rating</div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='metric-box'><strong>{prod['review_count']}</strong><br>Total Reviews</div>", unsafe_allow_html=True)
            with col4:
                prod_reviews = reviews_df[reviews_df['product_id'] == prod['product_id']]
                verified_pct = (prod_reviews['verified'].sum() / len(prod_reviews)) * 100
                st.markdown(f"<div class='metric-box'><strong>{verified_pct:.0f}%</strong><br>Verified</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("**📝 Top Trustworthy Reviews:**")
            
            # Show top 3 reviews in compact format - full text using components
            import streamlit.components.v1 as components
            
            reviews_html = """
            <style>
                .rec-reviews-container {
                    max-height: 350px;
                    overflow-y: auto;
                    padding: 0.5rem;
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                }
                .rec-reviews-container::-webkit-scrollbar {
                    width: 6px;
                }
                .rec-reviews-container::-webkit-scrollbar-track {
                    background: #f1f5f9;
                    border-radius: 3px;
                }
                .rec-reviews-container::-webkit-scrollbar-thumb {
                    background: #cbd5e1;
                    border-radius: 3px;
                }
                .rec-review-card {
                    background: #f8fafc;
                    padding: 0.75rem;
                    border-radius: 6px;
                    margin-bottom: 0.5rem;
                    font-size: 0.85rem;
                }
                .trust-high { color: #059669; font-weight: 700; }
                .trust-medium { color: #d97706; font-weight: 700; }
                .trust-low { color: #dc2626; font-weight: 700; }
            </style>
            <div class="rec-reviews-container">
            """
            
            top_reviews = prod_reviews.nlargest(3, 'trust_score')
            for ridx, (_, rev) in enumerate(top_reviews.iterrows(), 1):
                rev_class = get_trust_color(rev['trust_score'])
                review_text = str(rev['review_text']).replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                
                reviews_html += f"""
                <div class='rec-review-card'>
                    <div style='margin-bottom: 0.5rem;'>
                        <span style='font-size: 0.9em; color: #f59e0b;'>{'⭐' * int(rev['rating'])}</span>
                        <span class='{rev_class}' style='font-size: 0.8em; margin-left: 0.5rem;'>Trust: {rev['trust_score']:.4f}</span>
                        <span style='color: #64748b; margin-left: 0.5rem; font-size: 0.75rem;'>{'✅ Verified' if rev['verified'] else '❌'}</span>
                    </div>
                    <div style='color: #475569; line-height: 1.5;'>
                        {review_text}
                    </div>
                </div>
                """
            
            reviews_html += '</div>'
            components.html(reviews_html, height=370, scrolling=False)
else:
    st.warning("⚠️ No products match your criteria. Try lowering the filters.")

st.divider()

# ============================================================================
# REVIEW ANALYZER
# ============================================================================

st.markdown('<p class="section-header">🔍 AI Review Trust Analyzer</p>', unsafe_allow_html=True)
st.markdown("Test any review text to see how our AI model evaluates its trustworthiness")

col1, col2 = st.columns([3, 1])

with col1:
    review_text = st.text_area("Review Text", placeholder="Enter a product review...", height=120)

with col2:
    rating = st.selectbox("Rating", [5, 4, 3, 2, 1])
    verified = st.checkbox("Verified Purchase", value=True)

if st.button("🔍 Analyze Trust Score", type="primary"):
    if review_text and tfidf_vec and scaler and model:
        try:
            # Extract features
            features = extract_features(review_text, rating, verified)
            if features:
                # TF-IDF
                tfidf_features = tfidf_vec.transform([review_text]).toarray()
                
                # Numerical features
                num_features = np.array([[
                    features['rating'],
                    features['verified'],
                    features['review_length'],
                    features['word_count'],
                    features['avg_word_length'],
                    features['sentiment_polarity'],
                    features['sentiment_subjectivity'],
                    features['exclamation_count'],
                    features['question_count'],
                    features['uppercase_ratio']
                ]])
                
                # Combine and predict
                combined = np.hstack([num_features, tfidf_features])
                scaled = scaler.transform(combined)
                trust_score = model.predict(scaled)[0]
                
                # Display results
                st.success("✅ Analysis Complete!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    trust_class = get_trust_color(trust_score)
                    st.markdown(f"<div style='text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 8px;'>"
                               f"<div class='{trust_class}'>{trust_score:.3f}</div>"
                               f"<div style='color: #7f8c8d; margin-top: 0.5rem;'>Trust Score</div></div>", 
                               unsafe_allow_html=True)
                
                with col2:
                    st.metric("Sentiment", f"{features['sentiment_polarity']:.2f}", help="Range: -1 (negative) to +1 (positive)")
                
                with col3:
                    st.metric("Word Count", features['word_count'])
                
                # Interpretation
                st.markdown("---")
                if trust_score >= 0.7:
                    st.success("✅ **High Trust** - This review appears authentic, detailed, and helpful.")
                elif trust_score >= 0.4:
                    st.warning("⚠️ **Medium Trust** - This review is acceptable but may lack detail or show some unusual patterns.")
                else:
                    st.error("❌ **Low Trust** - This review shows suspicious patterns and may be spam or fake.")
                
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter review text and ensure models are loaded.")

st.divider()

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div style='text-align: center; padding: 2rem; background: #f8fafc; border-radius: 10px; margin-top: 2rem;'>
    <p style='color: #64748b; font-size: 0.9rem; margin-bottom: 0.5rem;'>
        <strong>🤖 Powered by Advanced Machine Learning</strong>
    </p>
    <p style='color: #94a3b8; font-size: 0.85rem;'>
        XGBoost Model | 10+ Features | Text Analysis | Sentiment Detection | Behavioral Patterns
    </p>
</div>
""", unsafe_allow_html=True)
