# Trust-Based Product Recommendation System - Demo

🌐 **[Live Demo on Streamlit Cloud](https://context-aware-trust-scoring-recommendation.streamlit.app)** 🌐

## Overview

This interactive demo showcases a trust-based product recommendation system that ranks reviews and products by trust score instead of just rating. The system identifies low-quality reviews and provides more reliable product rankings.

**Dataset:** 10,000 sample reviews from Amazon Fashion, 7,503 products

---

## Quick Start (Local)

### 1. Navigate to demo folder
```bash
cd demo
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## Features

### 🔍 Product Search
- **Smart Search:** Exact match → Partial match → Contains match
- **Exact Match Mode:** Find specific product IDs
- **High Trust Only:** Search within top-rated products
- **Visual Indicators:** 🎯 Exact matches, ⭐ High trust products
- **Real-time Results:** Search results ranked by trust score

### ⚖️ Trust vs Rating Comparison
- Side-by-side comparison of traditional rating-based ranking vs trust-based ranking
- Shows top 5 products by each method
- Highlights ranking differences and impact

### 📦 Product Analysis (Dynamic)
- **Metrics Dashboard:** Product ID, Trust Score, Avg Rating, Review Count
- **Dynamic Updates:** Searching for a product immediately updates all analysis sections
- **Product Information:** Category, review statistics, recommendation status

### 📊 Reviews Ranked by Trust
- Reviews sorted by trust score (highest first)
- **Trust Score Distribution:** Histogram showing distribution of trust scores
- **Rating vs Trust Comparison:** Visual comparison of average rating vs trust score
- **Interactive Filter:** Slider to filter out low-trust reviews
- **Statistics:** Total reviews, avg trust score, avg rating, verified %
- **Low Trust Warning:** Alerts when suspicious reviews detected

### ⚖️ Product Score Comparison
- Compare average rating vs trust-weighted score
- Visual bar chart comparison
- Explanation of score differences
- Additional product metrics (review count, rating std dev)

### 🎯 Section 5: Dynamic Product Analysis & Review Addition

**NEW in v2.0.0:** Complete workflow for testing review addition with live ML inference

- **Product Selection:** Choose from 100 top products
- **Current Metrics Display:** Reviews, rating, trust score, ranking position
- **Add New Review:** Text input, rating slider, verified checkbox
- **ML Trust Prediction:** Real-time trust score using trained XGBoost model
- **Feature Extraction:** 18 structured features + 5000 TF-IDF features
- **Dynamic Dataset Update:** New review added to dataframe in real-time
- **Product Metrics Recalculation:** Trust-weighted score updated instantly
- **Before/After Comparison:** Visual charts showing impact
- **Ranking Impact:** See how product position changes in top 10
- **Updated Reviews Display:** All reviews sorted by trust, new review highlighted

**Workflow Structure:**
```
1️⃣ Product Information (image, name, category, brand, price)
   ↓
2️⃣ Current Product Scores (reviews, rating, trust, ranking)
   ↓
3️⃣ Add New Review (text input, predict trust score, show results)
   ↓
4️⃣ Updated Reviews (sorted by trust, new review highlighted)
   ↓
5️⃣ Ranking Impact (before/after comparison, visual charts, updated top 10)
```

**Technical Implementation:**
- Models loaded with `@st.cache_resource` (TF-IDF, Scaler, XGBoost)
- Feature extraction function: `extract_features_for_review()`
- Prediction pipeline: `predict_trust_score()`
- Dynamic dataframe updates with `pd.concat()`
- Real-time product score recalculation
- Session-based updates (temporary, resets on refresh)

---

## Data Hosting

**Production:** Data hosted on Google Drive (cloud-hosted)
- Reviews File: 10,000 reviews (1.7MB)
- Products File: 7,503 products (0.7MB)
- Automatic download on app startup
- Cached for fast subsequent loads

**Local Development:** Sample CSV files included in demo folder
- `reviews_sample.csv` - 10K reviews
- `products_sample.csv` - 7.5K products

---

## How It Works

### 1. Search for Products
Enter a product ID (e.g., "B014EB2ADA") or partial ID (e.g., "B01") to search. The system will:
- Find exact matches first
- Fall back to partial matches
- Show top suggestions if no matches found
- Rank all results by trust score

### 2. Analyze Product
Click "Analyze" on any product to:
- View all reviews ranked by trust score
- See trust score distribution histogram
- Compare trust-weighted score vs average rating
- Filter low-quality reviews
- Understand product recommendation status

### 3. Compare Rankings
See how trust-based ranking differs from traditional rating-based ranking:
- Products in both top 5: Shows overlap
- Ranking differences highlight impact of trust scoring

---

## Demo Goals

✅ **Reviews ranked by trust** (not just rating)  
✅ **Product ranking improves** using trust-weighted aggregation  
✅ **Low-quality reviews can be filtered out**  
✅ **Real search functionality** with dynamic analysis  
✅ **Visual trust score distribution** for quality assessment  
✅ **Side-by-side ranking comparison** showing system impact  
✅ **Live ML inference** for trust score prediction  
✅ **Dynamic dataset updates** showing real-time ranking changes  
✅ **Product metadata** with images and detailed information

---

## Section 5: Dynamic Product Analysis & Review Addition

**Complete workflow for testing review addition with live ML inference**

### Key Features
- **Product Selection:** Choose from 100 top products with names displayed
- **Product Metadata:** Real Amazon data (images, names, categories, brands, prices)
- **Current Metrics:** Reviews, rating, trust score, ranking position
- **Demo Presets:** 🟢 Genuine Review and 🔴 Fake Review buttons for quick testing
- **Custom Review Input:** Text area, rating slider (1-5), verified checkbox
- **ML Trust Prediction:** Real-time trust score using trained XGBoost model
- **Feature Extraction:** 18 structured features + 5000 TF-IDF features with TextBlob sentiment
- **Session Persistence:** Reviews persist across reruns (cumulative impact demonstration)
- **Review History Table:** Shows all reviews added in session with trust scores
- **Dynamic Updates:** New reviews added to dataframe in real-time
- **Ranking Impact:** Before/after comparison with visual charts
- **Highlighted Reviews:** New reviews highlighted with timestamp-based unique IDs

### Workflow
```
1️⃣ Product Information (real image, name, category, brand, price)
   ↓
2️⃣ Current Product Scores (reviews, rating, trust, ranking)
   ↓
3️⃣ Demo Presets (🟢 Genuine / 🔴 Fake) OR Custom Review
   ↓
4️⃣ Add Review → ML Prediction → Trust Score
   ↓
5️⃣ Review History Table (all session reviews)
   ↓
6️⃣ Updated Reviews (sorted by trust, new ones highlighted)
   ↓
7️⃣ Ranking Impact (before/after, charts, updated top 10)
```

### Demo Story (30-Second Fake Review Attack)
The most compelling demonstration: Click "🔴 Fake Review" three times and watch the trust-weighted score drop while the raw average stays high. This demonstrates the system detecting low-quality content and protecting the ranking in real-time.

### ML Model Integration
- **Models Loaded:** TF-IDF Vectorizer, StandardScaler, XGBoost Regressor (cached with `@st.cache_resource`)
- **Feature Extraction:** 18 structured features + 5000 TF-IDF features
- **Sentiment Analysis:** TextBlob NLP (not exclamation counting)
- **User IDs:** Timestamp-based `NEW_USER_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}`
- **Persistence:** `st.session_state.added_reviews = []` for cumulative tracking
- **Prediction:** Real-time trust score (0-1 scale)
- **Graceful Fallback:** App works with pre-computed scores if models not found

---

## Technical Details

### Architecture
- **Frontend:** Streamlit (Python web framework)
- **Data Loading:** Google Drive API with caching
- **Processing:** Pandas for data manipulation
- **Visualization:** Streamlit native charts

### Performance
- **First Load:** 2-3 seconds (downloads data from Google Drive)
- **Subsequent Loads:** Instant (cached)
- **Search:** Real-time filtering and ranking
- **Analysis Updates:** Instant (dynamic session state)

### Data Flow
1. User searches for product → Real-time filtering
2. User clicks "Analyze" → Session state updated
3. All sections dynamically update → Show selected product data
4. User adjusts filters → Real-time re-rendering

---

## Troubleshooting

### Data Loading Issues
**Error: "Error loading data from Google Drive"**
- Check internet connection
- Verify Google Drive file IDs are correct
- Ensure files are shared with "Anyone with the link"

**Solution:** App automatically falls back to local sample files if Google Drive fails

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

### Slow Loading
- First load downloads data from Google Drive (2-3 seconds)
- Subsequent loads use cached data (instant)
- Clear cache: Click "Clear cache" in Streamlit menu (⋮)

### Search Not Working
- Ensure product ID is valid (e.g., "B014EB2ADA")
- Try partial search (e.g., "B01")
- Switch search modes (Smart Search, Exact Match, High Trust Only)

### Analysis Not Updating
- Click "Analyze" button after searching
- Use "Select Different Product" to change selection
- Refresh page if session state is stuck

---

## File Structure

```
demo/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── reviews_sample.csv      # Sample reviews (10K, 1.7MB)
├── products_sample.csv     # Sample products (7.5K, 0.7MB)
└── README.md              # This file
```

---

## Deployment

### Streamlit Cloud (Production)
**Live URL:** https://context-aware-trust-scoring-recommendation.streamlit.app

**Configuration:**
- Python version: 3.9+
- Main file: `demo/app.py`
- Requirements: `demo/requirements.txt`
- Data source: Google Drive (cloud-hosted)

### Local Deployment
```bash
cd demo
pip install -r requirements.txt
streamlit run app.py
```

### Docker Deployment
```bash
# Build image
docker build -t trust-demo .

# Run container
docker run -p 8501:8501 trust-demo
```

---

## Updates & Maintenance

**Version:** 2.0.0  
**Last Updated:** April 29, 2026  
**Status:** Production Ready

### Recent Updates (v2.0.0 - April 29, 2026)

**Phase 0: Core Fixes**
- ✅ **Fixed duplicate Section 5** - Removed 497 lines of duplicate code
- ✅ **Verified dynamic connectivity** - All sections properly connected via session state
- ✅ **Real search functionality** - 3 search modes with visual indicators
- ✅ **Dynamic product analysis** - Search → Analyze → Instant updates
- ✅ **Fixed all crashes** - Resolved set_page_config, column name, security issues

**Phase 1: Real Data Integration**
- ✅ **Real Amazon metadata** - Extracted from official dataset (186,637 records)
- ✅ **100% authentic data** - Real product names, 78% real images, 76% real brands
- ✅ **Fixed column bug** - Corrected col3/col4 duplicate in search results
- ✅ **Session persistence** - Reviews survive Streamlit reruns (cumulative tracking)
- ✅ **TextBlob sentiment** - Replaced exclamation counting with NLP analysis
- ✅ **Timestamp user IDs** - Fixed highlighting with unique timestamp-based IDs

**Phase 2: UX Enhancements**
- ✅ **Image validation** - Robust URL checking with graceful fallbacks
- ✅ **Product descriptions** - Added from Amazon metadata
- ✅ **Dropdown improvements** - Show "B01... — Product Name" format
- ✅ **Dynamic categories** - Real category lookup from metadata (not hardcoded)

**Phase 3: Demo Features**
- ✅ **Demo presets** - 🟢 Genuine Review and 🔴 Fake Review buttons
- ✅ **Review History table** - Shows all session reviews with trust scores
- ✅ **Live ML inference** - Real-time trust score prediction
- ✅ **Dynamic updates** - Real-time ranking changes after review addition
- ✅ **Cumulative metrics** - Live counters with deltas showing session impact

**Deployment & Performance**
- ✅ **Streamlit Cloud** - Production deployment with auto-updates
- ✅ **Google Drive integration** - Cloud-hosted data files for scalability
- ✅ **Model loading** - Fixed XGBoost dependency and caching
- ✅ **Performance** - 2-3s first load, instant subsequent loads

### Architecture Changes
- **Session State Management:** Unified product selection across sections
- **Independent Section 5:** Separate workflow for testing review addition
- **Model Loading:** Cached with `@st.cache_resource` for performance
- **Data Loading:** Cached with `@st.cache_data` for fast subsequent loads
- **Error Handling:** Graceful fallbacks for missing models or data

### Performance Improvements
- **First Load:** 2-3 seconds (downloads from Google Drive)
- **Subsequent Loads:** Instant (cached)
- **Search:** Real-time filtering (<100ms)
- **ML Inference:** ~50ms per review
- **Dataset Updates:** Real-time recalculation

---

## Support

**Issues?** Check the troubleshooting section above or contact the project maintainer.

**Feature Requests?** Submit via project repository issues.

---

**Built with Streamlit | Powered by XGBoost | Data from Amazon Reviews**
