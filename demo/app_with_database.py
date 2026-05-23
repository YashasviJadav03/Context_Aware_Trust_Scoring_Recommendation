"""
Trust-Based Product Recommendation System - ENHANCED VERSION
Phase 1 Complete: Database + Optional Caching + Performance Monitoring
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from database.config import DatabaseConfig

# Try to import caching (optional)
try:
    from database.db_manager_cached import CachedDatabaseManager
    CACHING_AVAILABLE = True
except:
    CACHING_AVAILABLE = False

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Trust-Based Recommendation System",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SIDEBAR - SETTINGS & INFO
# ============================================================================

with st.sidebar:
    st.title("⚙️ Settings")
    
    # Database selection
    st.subheader("Database")
    db_type = st.radio(
        "Database Type",
        ["SQLite (Local)", "PostgreSQL (Production)"],
        index=0,
        help="SQLite for development, PostgreSQL for production"
    )
    
    # Cache settings
    st.subheader("Performance")
    if CACHING_AVAILABLE:
        use_cache = st.checkbox(
            "Enable Redis Cache",
            value=False,
            help="80-90% faster queries (requires Redis)"
        )
    else:
        use_cache = False
        st.info("📦 Redis not installed\nInstall for 80-90% speed boost")
    
    # Performance monitoring
    show_performance = st.checkbox(
        "Show Query Times",
        value=True,
        help="Display query execution times"
    )
    
    st.divider()
    
    # System info
    st.subheader("📊 System Info")
    
    # Database info will be populated after connection

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

@st.cache_resource
def get_database(use_caching=False):
    """Get database connection (cached)"""
    try:
        # Get configuration
        if db_type == "PostgreSQL (Production)":
            config = DatabaseConfig.get_postgresql_config()
        else:
            config = DatabaseConfig.get_sqlite_config()
        
        # Use cached or regular database manager
        if use_caching and CACHING_AVAILABLE:
            redis_config = DatabaseConfig.get_redis_config()
            db = CachedDatabaseManager(
                cache_enabled=redis_config['enabled'],
                redis_host=redis_config['host'],
                redis_port=redis_config['port'],
                redis_password=redis_config['password'],
                **config
            )
            st.sidebar.success("✓ Cache enabled")
        else:
            db = DatabaseManager(**config)
            if use_caching:
                st.sidebar.warning("⚠ Cache requested but not available")
        
        return db
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# Initialize database
db = get_database(use_cache)

if db is None:
    st.error("Failed to connect to database.")
    st.stop()

# Update sidebar with database info
with st.sidebar:
    st.write(f"**Type:** {db.db_type}")
    if db.db_type == 'sqlite':
        st.write(f"**Path:** {db.db_path}")
        if os.path.exists(db.db_path):
            size_mb = os.path.getsize(db.db_path) / (1024 * 1024)
            st.write(f"**Size:** {size_mb:.2f} MB")
    
    # Cache info
    if use_cache and hasattr(db, 'cache'):
        cache_health = db.cache_health_check()
        if cache_health['redis_available']:
            st.success(f"✓ Redis: {cache_health['response_time_ms']:.2f}ms")
        else:
            st.warning("⚠ Redis unavailable (using fallback)")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def measure_time(func, *args, **kwargs):
    """Measure function execution time"""
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = (time.time() - start) * 1000  # Convert to ms
    return result, elapsed

def show_query_time(elapsed_ms):
    """Display query execution time"""
    if show_performance:
        if elapsed_ms < 10:
            st.caption(f"⚡ Query time: {elapsed_ms:.2f}ms (Excellent)")
        elif elapsed_ms < 50:
            st.caption(f"✓ Query time: {elapsed_ms:.2f}ms (Good)")
        else:
            st.caption(f"⚠ Query time: {elapsed_ms:.2f}ms")

# ============================================================================
# HEADER WITH LIVE STATS
# ============================================================================

st.title("🛍️ Trust-Based Product Recommendation System")
st.caption("Phase 1 Complete | Real-time Database | Optional Caching")

# Get live statistics
stats, stats_time = measure_time(db.get_system_statistics)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Reviews",
        f"{stats['total_reviews']:,}"
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

show_query_time(stats_time)

# Show cache statistics if available
if use_cache and hasattr(db, 'get_cache_stats'):
    with st.expander("📊 Cache Statistics"):
        cache_stats = db.get_cache_stats()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Cache Hits", f"{cache_stats['hits']:,}")
        with col2:
            st.metric("Cache Misses", f"{cache_stats['misses']:,}")
        with col3:
            st.metric("Hit Rate", f"{cache_stats['hit_rate']:.1f}%")
        with col4:
            if cache_stats.get('redis_keys'):
                st.metric("Cached Keys", f"{cache_stats['redis_keys']:,}")

st.divider()

# ============================================================================
# PRODUCT SEARCH
# ============================================================================

st.header("🔍 Product Search")

# Initialize session state
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None

# Search interface
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    search_query = st.text_input(
        "Search products",
        placeholder="Enter product ID, name, category, or brand...",
        key="search_input"
    )

with col2:
    search_mode = st.selectbox(
        "Mode",
        ["Smart Search", "Product ID", "High Trust", "Category"]
    )

with col3:
    search_limit = st.number_input(
        "Results",
        min_value=5,
        max_value=100,
        value=20,
        step=5
    )

# Perform search
if search_query:
    with st.spinner("Searching..."):
        if search_mode == "Product ID":
            product, search_time = measure_time(db.get_product, search_query)
            search_results = [product] if product else []
        elif search_mode == "High Trust":
            all_results, search_time = measure_time(db.search_products, search_query, limit=search_limit)
            search_results = [p for p in all_results if p.get('score_trust_weighted', 0) >= 4.5]
        elif search_mode == "Category":
            search_results, search_time = measure_time(db.get_products_by_category, search_query, limit=search_limit)
        else:
            search_results, search_time = measure_time(db.search_products, search_query, limit=search_limit)
    
    show_query_time(search_time)
    
    if search_results:
        st.success(f"Found {len(search_results)} product(s)")
        
        # Display results in a more compact format
        for idx, product in enumerate(search_results, 1):
            with st.expander(
                f"#{idx} - {product['product_name'][:60]}... | Trust: {product.get('score_trust_weighted', 0):.2f} ⭐",
                expanded=(idx == 1)
            ):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**Product ID:** `{product['product_id']}`")
                    st.write(f"**Category:** {product.get('category', 'N/A')}")
                    st.write(f"**Brand:** {product.get('brand', 'N/A')}")
                
                with col2:
                    st.write(f"**Trust Score:** {product.get('score_trust_weighted', 0):.3f}")
                    st.write(f"**Avg Rating:** {product.get('avg_rating', 0):.2f} ⭐")
                    st.write(f"**Reviews:** {product.get('review_count', 0):,}")
                
                with col3:
                    if st.button("📊 Analyze", key=f"analyze_{idx}", use_container_width=True):
                        st.session_state.selected_product = product['product_id']
                        st.rerun()
    else:
        st.warning("No products found. Try a different search term.")

st.divider()

# ============================================================================
# PRODUCT ANALYSIS
# ============================================================================

if st.session_state.selected_product:
    product_id = st.session_state.selected_product
    
    st.header(f"📊 Product Analysis")
    
    # Get product details
    product, product_time = measure_time(db.get_product, product_id)
    
    if product:
        # Product header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(product['product_name'])
            st.caption(f"Product ID: {product_id}")
        with col2:
            if st.button("🔙 Back to Search"):
                st.session_state.selected_product = None
                st.rerun()
        
        show_query_time(product_time)
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Trust Score", f"{product['score_trust_weighted']:.3f}")
        with col2:
            st.metric("Avg Rating", f"{product['avg_rating']:.2f} ⭐")
        with col3:
            st.metric("Total Reviews", f"{product['review_count']:,}")
        with col4:
            st.metric("Category", product['category'])
        
        # Product statistics
        product_stats, stats_time = measure_time(db.get_product_statistics, product_id)
        
        st.markdown("### 📈 Review Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("High Trust", product_stats.get('high_trust_count', 0))
        with col2:
            st.metric("Low Trust", product_stats.get('low_trust_count', 0))
        with col3:
            st.metric("Verified", product_stats.get('verified_count', 0))
        with col4:
            avg_trust = product_stats.get('avg_trust_score', 0)
            st.metric("Avg Trust", f"{avg_trust:.3f}")
        
        show_query_time(stats_time)
        
        # Reviews section
        st.markdown("### 💬 Reviews")
        
        # Filter controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_trust = st.slider("Min Trust Score", 0.0, 1.0, 0.0, 0.1)
        with col2:
            verified_only = st.checkbox("Verified Only")
        with col3:
            max_reviews = st.number_input("Max Reviews", 5, 100, 10, 5)
        
        # Get reviews
        reviews, reviews_time = measure_time(
            db.get_product_reviews,
            product_id,
            min_trust=min_trust,
            limit=1000
        )
        
        show_query_time(reviews_time)
        
        if reviews:
            # Convert to DataFrame for filtering
            reviews_df = pd.DataFrame(reviews)
            
            # Apply filters
            if verified_only:
                reviews_df = reviews_df[reviews_df['verified'] == True]
            
            st.write(f"Showing {min(len(reviews_df), max_reviews)} of {len(reviews_df)} reviews")
            
            # Display reviews
            for idx, (_, review) in enumerate(reviews_df.head(max_reviews).iterrows(), 1):
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        # Trust score badge
                        trust = review['trust_score']
                        if trust >= 0.7:
                            badge = "🟢 High Trust"
                        elif trust >= 0.4:
                            badge = "🟡 Medium Trust"
                        else:
                            badge = "🔴 Low Trust"
                        
                        st.markdown(f"**Review #{idx}** | {badge} ({trust:.3f})")
                        
                        # Review text
                        text = str(review['review_text'])
                        if len(text) > 300:
                            st.write(text[:300] + "...")
                        else:
                            st.write(text)
                    
                    with col2:
                        st.write(f"**Rating:** {int(review['rating'])} ⭐")
                        st.write(f"**Trust:** {review['trust_score']:.3f}")
                        st.write(f"**Verified:** {'✓' if review['verified'] else '✗'}")
                        if review.get('helpful_votes', 0) > 0:
                            st.write(f"**Helpful:** {review['helpful_votes']}")
                    
                    st.divider()
        else:
            st.info("No reviews found for this product")
    else:
        st.error("Product not found in database")
        if st.button("🔙 Back to Search"):
            st.session_state.selected_product = None
            st.rerun()

else:
    st.info("👆 Search and select a product above to view detailed analysis")

# ============================================================================
# ADD NEW REVIEW
# ============================================================================

if st.session_state.selected_product:
    st.divider()
    st.header("✍️ Add New Review")
    
    with st.form("add_review_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            review_text = st.text_area(
                "Review Text",
                placeholder="Share your experience with this product...",
                height=150
            )
            rating = st.slider("Rating", 1, 5, 5, help="1 = Poor, 5 = Excellent")
        
        with col2:
            verified = st.checkbox("Verified Purchase", value=True)
            helpful_votes = st.number_input("Helpful Votes", min_value=0, value=0)
            
            st.info("""
            **Trust Score Calculation:**
            - Based on rating and verification
            - Verified purchases get bonus
            - Range: 0.0 to 1.0
            """)
        
        submitted = st.form_submit_button("📤 Submit Review", use_container_width=True)
        
        if submitted:
            if not review_text:
                st.error("Please enter review text")
            else:
                # Calculate trust score
                trust_score = rating / 5.0
                if verified:
                    trust_score = min(trust_score + 0.1, 1.0)
                
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
                with st.spinner("Submitting review..."):
                    review_id = db.insert_review(review_data)
                
                if review_id:
                    st.success(f"✅ Review submitted successfully! (ID: {review_id})")
                    st.info("🔄 Refresh the page to see your review")
                    
                    # Clear caches
                    st.cache_data.clear()
                    if use_cache and hasattr(db, 'cache'):
                        db.cache.invalidate_on_new_review(st.session_state.selected_product)
                else:
                    st.error("❌ Failed to submit review. Please try again.")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🛍️ Trust-Based Product Recommendation System")
    st.caption("Phase 1 Complete | Database-Powered")

with col2:
    st.caption(f"📊 Database: {db.db_type.upper()}")
    if use_cache:
        st.caption("⚡ Cache: Enabled")
    else:
        st.caption("💾 Cache: Disabled")

with col3:
    st.caption(f"📦 Products: {stats['total_products']:,}")
    st.caption(f"💬 Reviews: {stats['total_reviews']:,}")

# Performance summary
if show_performance and use_cache and hasattr(db, 'get_cache_stats'):
    with st.expander("🔧 Performance Details"):
        cache_stats = db.get_cache_stats()
        st.write(f"**Cache Hit Rate:** {cache_stats['hit_rate']:.1f}%")
        st.write(f"**Total Requests:** {cache_stats['total_requests']:,}")
        st.write(f"**Cache Hits:** {cache_stats['hits']:,}")
        st.write(f"**Cache Misses:** {cache_stats['misses']:,}")
        
        if cache_stats['hit_rate'] > 50:
            st.success("✓ Cache is working well!")
        elif cache_stats['hit_rate'] > 0:
            st.info("Cache is warming up...")
        else:
            st.warning("Cache not being used yet")
