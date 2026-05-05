"""
Trust-Based Product Recommendation System - DATABASE VERSION
Uses SQLite/PostgreSQL instead of CSV files
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Trust-Based Recommendation System",
    page_icon="",
    layout="wide"
)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

@st.cache_resource
def get_database():
    """Get database connection (cached)"""
    try:
        db = DatabaseManager(db_type='sqlite', db_path='database/reviews.db')
        return db
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# Initialize database
db = get_database()

if db is None:
    st.error("Failed to connect to database. Please run migrate_csv_to_db.py first.")
    st.stop()

# ============================================================================
# DATA LOADING FROM DATABASE
# ============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_products_from_db():
    """Load products from database"""
    try:
        products_df = db.export_to_dataframe('products')
        return products_df
    except Exception as e:
        st.error(f"Error loading products: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_reviews_from_db():
    """Load reviews from database"""
    try:
        reviews_df = db.export_to_dataframe('reviews')
        return reviews_df
    except Exception as e:
        st.error(f"Error loading reviews: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_product_reviews_from_db(product_id: str):
    """Get reviews for a specific product"""
    try:
        reviews = db.get_product_reviews(product_id, limit=1000)
        return pd.DataFrame(reviews)
    except Exception as e:
        st.error(f"Error loading product reviews: {e}")
        return pd.DataFrame()

# Load data
products = load_products_from_db()
reviews = load_reviews_from_db()

# ============================================================================
# HEADER WITH LIVE STATS FROM DATABASE
# ============================================================================

st.title("Trust-Based Product Recommendation System")
st.caption("Powered by Database | Real-time Data")

# Get live statistics from database
stats = db.get_system_statistics()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Reviews",
        f"{stats['total_reviews']:,}",
        delta=f"+{len(st.session_state.get('added_reviews', []))} new" if st.session_state.get('added_reviews') else None
    )

with col2:
    st.metric(
        "Total Products",
        f"{stats['total_products']:,}"
    )

with col3:
    st.metric(
        "Avg Trust Score",
        f"{stats['avg_trust_score']:.3f}"
    )

with col4:
    verified_pct = (stats['verified_reviews'] / stats['total_reviews'] * 100) if stats['total_reviews'] > 0 else 0
    st.metric(
        "Verified %",
        f"{verified_pct:.1f}%"
    )

with col5:
    high_trust_pct = (stats['high_trust_reviews'] / stats['total_reviews'] * 100) if stats['total_reviews'] > 0 else 0
    st.metric(
        "High Trust %",
        f"{high_trust_pct:.1f}%"
    )

st.divider()

# ============================================================================
# PRODUCT SEARCH (Using Database)
# ============================================================================

st.header("Product Search")

# Initialize session state
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'added_reviews' not in st.session_state:
    st.session_state.added_reviews = []

# Search
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input(
        "Search products",
        placeholder="Enter product ID, name, category, or brand...",
        key="search_input"
    )

with col2:
    search_mode = st.selectbox(
        "Mode",
        ["Smart Search", "Product ID", "High Trust"]
    )

# Perform search using database
if search_query:
    with st.spinner("Searching database..."):
        if search_mode == "Product ID":
            # Exact product ID search
            product = db.get_product(search_query)
            search_results = [product] if product else []
        elif search_mode == "High Trust":
            # Search high trust products
            all_results = db.search_products(search_query, limit=50)
            search_results = [p for p in all_results if p['score_trust_weighted'] >= 4.5]
        else:
            # Smart search
            search_results = db.search_products(search_query, limit=20)
    
    if search_results:
        st.success(f"Found {len(search_results)} product(s)")
        
        # Display results
        for idx, product in enumerate(search_results, 1):
            with st.expander(f"#{idx} - {product['product_name'][:60]}... (Trust: {product['score_trust_weighted']:.2f})"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**Product ID:** {product['product_id']}")
                    st.write(f"**Category:** {product['category']}")
                    st.write(f"**Brand:** {product['brand']}")
                
                with col2:
                    st.write(f"**Trust Score:** {product['score_trust_weighted']:.3f}")
                    st.write(f"**Avg Rating:** {product['avg_rating']:.2f}")
                    st.write(f"**Reviews:** {product['review_count']}")
                
                with col3:
                    if st.button("Analyze", key=f"analyze_{idx}"):
                        st.session_state.selected_product = product['product_id']
                        st.rerun()
    else:
        st.warning("No products found")

st.divider()

# ============================================================================
# PRODUCT ANALYSIS (Using Database)
# ============================================================================

if st.session_state.selected_product:
    product_id = st.session_state.selected_product
    
    st.subheader(f"Product Analysis: {product_id}")
    
    # Get product from database
    product = db.get_product(product_id)
    
    if product:
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Trust Score", f"{product['score_trust_weighted']:.3f}")
        
        with col2:
            st.metric("Avg Rating", f"{product['avg_rating']:.2f}")
        
        with col3:
            st.metric("Reviews", product['review_count'])
        
        with col4:
            st.metric("Category", product['category'])
        
        # Get product statistics from database
        product_stats = db.get_product_statistics(product_id)
        
        st.markdown("### Review Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("High Trust Reviews", product_stats.get('high_trust_count', 0))
        
        with col2:
            st.metric("Low Trust Reviews", product_stats.get('low_trust_count', 0))
        
        with col3:
            st.metric("Verified Reviews", product_stats.get('verified_count', 0))
        
        # Get reviews from database
        st.markdown("### Reviews")
        
        product_reviews = get_product_reviews_from_db(product_id)
        
        if len(product_reviews) > 0:
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                min_trust = st.slider("Min Trust Score", 0.0, 1.0, 0.0, 0.1)
            
            with col2:
                verified_only = st.checkbox("Verified Only")
            
            # Apply filters
            filtered_reviews = product_reviews[product_reviews['trust_score'] >= min_trust]
            if verified_only:
                filtered_reviews = filtered_reviews[filtered_reviews['verified'] == True]
            
            st.write(f"Showing {len(filtered_reviews)} of {len(product_reviews)} reviews")
            
            # Display reviews
            for idx, (_, review) in enumerate(filtered_reviews.head(10).iterrows(), 1):
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"**Review #{idx}**")
                        st.write(review['review_text'][:200] + "..." if len(str(review['review_text'])) > 200 else review['review_text'])
                    
                    with col2:
                        trust_class = "high" if review['trust_score'] >= 0.7 else "medium" if review['trust_score'] >= 0.4 else "low"
                        st.write(f"Trust: {review['trust_score']:.3f}")
                        st.write(f"Rating: {int(review['rating'])} stars")
                        st.write(f"Verified: {'Yes' if review['verified'] else 'No'}")
                    
                    st.divider()
        else:
            st.info("No reviews found for this product")
    else:
        st.error("Product not found in database")
else:
    st.info("Search and select a product above to begin analysis")

# ============================================================================
# ADD NEW REVIEW (Save to Database)
# ============================================================================

if st.session_state.selected_product:
    st.divider()
    st.subheader("Add New Review")
    
    with st.form("add_review_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            review_text = st.text_area("Review Text", placeholder="Enter your review...")
            rating = st.slider("Rating", 1, 5, 5)
        
        with col2:
            verified = st.checkbox("Verified Purchase", value=True)
            helpful_votes = st.number_input("Helpful Votes", min_value=0, value=0)
        
        submitted = st.form_submit_button("Submit Review")
        
        if submitted and review_text:
            # Calculate trust score (simplified)
            trust_score = rating / 5.0
            if verified:
                trust_score += 0.1
            trust_score = min(trust_score, 1.0)
            
            # Prepare review data
            review_data = {
                'user_id': f'USER_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'product_id': st.session_state.selected_product,
                'rating': rating,
                'review_text': review_text,
                'verified': verified,
                'helpful_votes': helpful_votes,
                'trust_score': trust_score,
                'predicted_trust_score': trust_score
            }
            
            # Insert into database
            review_id = db.insert_review(review_data)
            
            if review_id:
                st.success(f"Review added successfully! (ID: {review_id})")
                st.info("Database updated. Refresh to see changes.")
                
                # Clear cache to show new data
                st.cache_data.clear()
            else:
                st.error("Failed to add review to database")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.caption("Trust-Based Product Recommendation System | Database-Powered Version")
st.caption(f"Database: SQLite | Location: database/reviews.db")
