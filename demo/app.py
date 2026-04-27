"""
Trust-Based Product Recommendation System - Streamlit Demo
Fixed Version with Better Error Handling
"""

import streamlit as st
import pandas as pd
import numpy as np

# ============================================================================
# PAGE CONFIGURATION - MUST BE FIRST STREAMLIT COMMAND
# ============================================================================

st.set_page_config(
    page_title="Trust-Based Recommendation System",
    page_icon="🧠",
    layout="wide"
)

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

# Load data
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
st.markdown("""
This system ranks reviews and products by **trust score** instead of just rating.
Low-quality reviews are identified and can be filtered out.
""")

st.divider()

# ============================================================================
# PRODUCT SEARCH SIMULATION
# ============================================================================

st.header("🔍 Product Search")

# Search input with advanced options
col1, col2 = st.columns([3, 1])
with col1:
    search_query = st.text_input("Search for products:", placeholder="e.g., 'B014EB2ADA' or 'B01' for partial match", key="search_input")
with col2:
    search_mode = st.selectbox("Search Mode", ["Smart Search", "Exact Match", "High Trust Only"])

# Initialize selected product in session state if not exists
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None

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
            st.session_state.selected_product = None
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
            
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.write(f"**#{idx}** {highlight}")
                if badge:
                    st.caption(badge)
            with col2:
                st.write(f"**Product {product['product_id']}**")
                st.write(f"Trust Score: {product['score_trust_weighted']:.2f}")
                
                # Show additional info for matches
                if hasattr(product, 'review_count') and pd.notna(product.get('review_count')):
                    review_count = product['review_count']
                    avg_rating = product.get('avg_rating', 0)
                    st.write(f"📊 Reviews: {review_count} | Avg Rating: {avg_rating:.2f}")
                    
            with col3:
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
    # Show top products when no search
    st.subheader("🏆 Top 10 Recommended Products (Trust-Based)")
    st.info("💡 Enter a product ID above to search, or browse top products below")
    
    top_products = products.nlargest(10, 'score_trust_weighted')
    
    for idx, (_, product) in enumerate(top_products.iterrows(), 1):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.write(f"**#{idx}**")
        with col2:
            st.write(f"Product {product['product_id']}")
            st.write(f"Trust Score: {product['score_trust_weighted']:.2f}")
        with col3:
            if st.button(f"Analyze", key=f"top_analyze_{idx}"):
                st.session_state.selected_product = product['product_id']
                st.success(f"✅ Selected!")
                st.rerun()

# ============================================================================
# TRUST VS RATING COMPARISON
# ============================================================================

st.header("⚖️ Trust vs Rating Comparison")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔴 Traditional Ranking (Rating Only)")
    rating_ranked = products.nlargest(5, 'avg_rating')[['product_id', 'avg_rating']].copy()
    rating_ranked['avg_rating'] = rating_ranked['avg_rating'].round(2)
    rating_ranked.columns = ['Product ID', 'Avg Rating']
    rating_ranked.insert(0, 'Rank', range(1, 6))
    st.dataframe(rating_ranked, hide_index=True)

with col2:
    st.subheader("🟢 Trust-Based Ranking (Our System)")
    trust_ranked = products.nlargest(5, 'score_trust_weighted')[['product_id', 'score_trust_weighted']].copy()
    trust_ranked['score_trust_weighted'] = trust_ranked['score_trust_weighted'].round(2)
    trust_ranked.columns = ['Product ID', 'Trust Score']
    trust_ranked.insert(0, 'Rank', range(1, 6))
    st.dataframe(trust_ranked, hide_index=True)

# Show the difference
rating_ids = set(products.nlargest(5, 'avg_rating')['product_id'])
trust_ids = set(products.nlargest(5, 'score_trust_weighted')['product_id'])
common_products = rating_ids & trust_ids
st.info(f"Products in both top 5: {len(common_products)}/5 - Shows ranking difference impact!")

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
    st.session_state.selected_product = product_id

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

# Filter reviews for selected product
filtered_reviews = reviews[reviews['product_id'].astype(str) == str(product_id)].copy()

if len(filtered_reviews) == 0:
    st.error(f"❌ No reviews found for product {product_id}")
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
    # Rating vs Trust comparison
    comparison_data = pd.DataFrame({
        'Rating': [filtered_reviews['rating'].mean()],
        'Trust Score': [filtered_reviews['trust_score'].mean()]
    })
    st.bar_chart(comparison_data.T)
    st.caption("Average Rating vs Trust Score")

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
display_df['review_text'] = display_df['review_text'].astype(str).str[:200] + '...'
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

# Get product data
prod = products[products['product_id'].astype(str) == str(product_id)]

if len(prod) > 0:
    avg_rating = prod['avg_rating'].values[0]
    trust_score = prod['score_trust_weighted'].values[0]
    review_count = prod['review_count'].values[0] if 'review_count' in prod.columns else len(filtered_reviews)
    
    # ============================================================================
    # PRODUCT INFORMATION SECTION
    # ============================================================================
    
    st.subheader("📦 Product Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Product ID:** {product_id}")
        st.write(f"**Category:** Fashion Item")
        st.write(f"**Total Reviews:** {len(filtered_reviews)}")
    with col2:
        st.write(f"**Average Rating:** {avg_rating:.2f}/5.0")
        st.write(f"**Trust Score:** {trust_score:.2f}/5.0")
        recommendation = "✅ Recommended" if trust_score > avg_rating else "⚠️ Caution"
        st.write(f"**Recommendation:** {recommendation}")
    
    st.divider()
    
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
# FOOTER
# ============================================================================

