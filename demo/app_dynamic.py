"""
Trust-Based Product Recommendation System - DYNAMIC VERSION
Enhanced with interactive features, real-time visualizations, and better UX
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import re
from textblob import TextBlob
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Trust-Based Recommendation System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .trust-high {
        color: #2ecc71;
        font-weight: bold;
    }
    .trust-medium {
        color: #f39c12;
        font-weight: bold;
    }
    .trust-low {
        color: #e74c3c;
        font-weight: bold;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - DYNAMIC CONTROLS
# ============================================================================

with st.sidebar:
    st.markdown("### Control Panel")
    
    # Dataset info
    st.markdown("#### Dataset Statistics")
    
    # Filters
    st.markdown("#### Filters")
    min_trust_filter = st.slider(
        "Minimum Trust Score",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1,
        help="Filter products by minimum trust score"
    )
    
    min_reviews_filter = st.slider(
        "Minimum Reviews",
        min_value=1,
        max_value=100,
        value=1,
        help="Filter products by minimum number of reviews"
    )
    
    # Visualization options
    st.markdown("#### Visualization Options")
    show_charts = st.checkbox("Show Interactive Charts", value=True)
    show_distributions = st.checkbox("Show Distributions", value=True)
    show_comparisons = st.checkbox("Show Comparisons", value=True)
    
    # Export options
    st.markdown("#### Export Options")
    if st.button("Export Current View"):
        st.info("Export functionality coming soon!")

# ============================================================================
# LOAD MODELS AND DATA (same as before)
# ============================================================================

@st.cache_resource
def load_models():
    """Load trained models for inference"""
    import os
    
    possible_paths = ["", "../", "./"]
    base_path = None
    
    for path in possible_paths:
        if os.path.exists(f"{path}models/tfidf_vectorizer.pkl"):
            base_path = path
            break
    
    if base_path is None:
        return None, None, None
    
    try:
        tfidf = joblib.load(f"{base_path}models/tfidf_vectorizer.pkl")
        scaler = joblib.load(f"{base_path}models/feature_scaler.pkl")
        model = joblib.load(f"{base_path}models/trained/best_trust_model.pkl")
        return tfidf, scaler, model
    except:
        return None, None, None

@st.cache_data
def load_data():
    """Load review and product data"""
    try:
        reviews = pd.read_csv("data/processed/reviews_sample.csv")
        products = pd.read_csv("data/processed/product_trust_scores.csv")
        return reviews, products
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

# Load everything
tfidf_vectorizer, feature_scaler, trust_model = load_models()
reviews, products = load_data()

# ============================================================================
# DYNAMIC HEADER WITH LIVE STATS
# ============================================================================

st.markdown('<div class="main-header">Trust-Based Product Recommendation System</div>', unsafe_allow_html=True)

# Live statistics in columns
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Reviews",
        f"{len(reviews):,}",
        delta=f"+{len(st.session_state.get('added_reviews', []))} new" if st.session_state.get('added_reviews') else None
    )

with col2:
    st.metric(
        "Total Products",
        f"{products['product_id'].nunique():,}"
    )

with col3:
    avg_trust = reviews['trust_score'].mean()
    st.metric(
        "Avg Trust Score",
        f"{avg_trust:.3f}",
        delta=f"{(avg_trust - 0.5):.3f}" if avg_trust > 0.5 else f"{(avg_trust - 0.5):.3f}"
    )

with col4:
    high_trust_pct = (reviews['trust_score'] >= 0.7).sum() / len(reviews) * 100
    st.metric(
        "High Trust %",
        f"{high_trust_pct:.1f}%"
    )

with col5:
    verified_pct = reviews['verified'].sum() / len(reviews) * 100
    st.metric(
        "Verified %",
        f"{verified_pct:.1f}%"
    )

st.divider()

# ============================================================================
# DYNAMIC VISUALIZATIONS
# ============================================================================

if show_charts:
    st.subheader("System Overview - Interactive Visualizations")
    
    tab1, tab2, tab3 = st.tabs(["Trust Distribution", "Rating vs Trust", "Product Analysis"])
    
    with tab1:
        # Trust score distribution
        fig = px.histogram(
            reviews,
            x='trust_score',
            nbins=50,
            title="Trust Score Distribution",
            labels={'trust_score': 'Trust Score', 'count': 'Number of Reviews'},
            color_discrete_sequence=['#1f77b4']
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Rating vs Trust scatter
        sample_reviews = reviews.sample(min(5000, len(reviews)))
        fig = px.scatter(
            sample_reviews,
            x='rating',
            y='trust_score',
            color='verified',
            title="Rating vs Trust Score",
            labels={'rating': 'Rating (1-5)', 'trust_score': 'Trust Score', 'verified': 'Verified'},
            opacity=0.6
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Top products by trust
        top_products = products.nlargest(20, 'score_trust_weighted')
        fig = px.bar(
            top_products,
            x='product_id',
            y='score_trust_weighted',
            title="Top 20 Products by Trust Score",
            labels={'product_id': 'Product ID', 'score_trust_weighted': 'Trust Score'},
            color='score_trust_weighted',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()

# ============================================================================
# DYNAMIC PRODUCT SEARCH WITH AUTOCOMPLETE
# ============================================================================

st.subheader("Product Search & Analysis")

# Initialize session state
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'added_reviews' not in st.session_state:
    st.session_state.added_reviews = []
if 'comparison_products' not in st.session_state:
    st.session_state.comparison_products = []

# Search with real-time suggestions
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input(
        "Search products",
        placeholder="Enter product ID or search term...",
        help="Search by product ID, name, category, or brand"
    )

with col2:
    search_mode = st.selectbox(
        "Mode",
        ["Smart Search", "Product ID", "High Trust"]
    )

# Real-time search results
if search_query:
    # Filter products based on search
    if search_mode == "Product ID":
        results = products[products['product_id'].str.contains(search_query, case=False, na=False)]
    else:
        results = products[products['product_id'].str.contains(search_query, case=False, na=False)]
    
    if len(results) > 0:
        st.success(f"Found {len(results)} product(s)")
        
        # Display results in expandable cards
        for idx, (_, product) in enumerate(results.head(10).iterrows(), 1):
            with st.expander(f"#{idx} - {product['product_id']} (Trust: {product['score_trust_weighted']:.2f})"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**Trust Score:** {product['score_trust_weighted']:.3f}")
                    st.write(f"**Avg Rating:** {product['avg_rating']:.2f}")
                
                with col2:
                    review_count = len(reviews[reviews['product_id'] == product['product_id']])
                    st.write(f"**Reviews:** {review_count}")
                    st.write(f"**Rating Std:** {product.get('rating_std', 0):.3f}")
                
                with col3:
                    if st.button("Analyze", key=f"analyze_{idx}"):
                        st.session_state.selected_product = product['product_id']
                        st.rerun()
    else:
        st.warning("No products found")

st.divider()

# ============================================================================
# DYNAMIC PRODUCT ANALYSIS
# ============================================================================

if st.session_state.selected_product:
    product_id = st.session_state.selected_product
    
    st.subheader(f"Product Analysis: {product_id}")
    
    # Get product data
    product_data = products[products['product_id'] == product_id].iloc[0]
    product_reviews = reviews[reviews['product_id'] == product_id]
    
    # Dynamic metrics with progress bars
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        trust_score = product_data['score_trust_weighted']
        st.metric("Trust Score", f"{trust_score:.3f}")
        st.progress(trust_score / 5.0)
    
    with col2:
        avg_rating = product_data['avg_rating']
        st.metric("Avg Rating", f"{avg_rating:.2f}")
        st.progress(avg_rating / 5.0)
    
    with col3:
        review_count = len(product_reviews)
        st.metric("Reviews", review_count)
    
    with col4:
        verified_pct = product_reviews['verified'].sum() / len(product_reviews) * 100
        st.metric("Verified %", f"{verified_pct:.1f}%")
    
    # Interactive review analysis
    st.markdown("### Review Analysis")
    
    # Trust score distribution for this product
    if show_distributions:
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=product_reviews['trust_score'],
            name='Trust Score',
            nbinsx=20,
            marker_color='#1f77b4'
        ))
        
        fig.update_layout(
            title=f"Trust Score Distribution for {product_id}",
            xaxis_title="Trust Score",
            yaxis_title="Count",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Review table with filtering
    st.markdown("### Reviews")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_trust = st.slider("Min Trust", 0.0, 1.0, 0.0, 0.1, key="review_trust_filter")
    
    with col2:
        min_rating = st.slider("Min Rating", 1, 5, 1, key="review_rating_filter")
    
    with col3:
        verified_only = st.checkbox("Verified Only", key="verified_filter")
    
    # Apply filters
    filtered_reviews = product_reviews[
        (product_reviews['trust_score'] >= min_trust) &
        (product_reviews['rating'] >= min_rating)
    ]
    
    if verified_only:
        filtered_reviews = filtered_reviews[filtered_reviews['verified'] == True]
    
    st.write(f"Showing {len(filtered_reviews)} of {len(product_reviews)} reviews")
    
    # Display reviews
    for idx, (_, review) in enumerate(filtered_reviews.head(10).iterrows(), 1):
        trust_class = "trust-high" if review['trust_score'] >= 0.7 else "trust-medium" if review['trust_score'] >= 0.4 else "trust-low"
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**Review #{idx}**")
                st.write(review['review_text'][:200] + "..." if len(review['review_text']) > 200 else review['review_text'])
            
            with col2:
                st.markdown(f"<span class='{trust_class}'>Trust: {review['trust_score']:.3f}</span>", unsafe_allow_html=True)
                st.write(f"Rating: {'⭐' * int(review['rating'])}")
                st.write(f"Verified: {'✓' if review['verified'] else '✗'}")
            
            st.divider()

else:
    st.info("Search and select a product above to begin analysis")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.caption("Trust-Based Product Recommendation System | Enhanced Dynamic Version")
