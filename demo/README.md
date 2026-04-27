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

### 🏆 Top Recommended Products
- Top 10 products by trust-weighted score
- Comparison with rating-based rankings
- Shows ranking differences between methods

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
**Last Updated:** April 27, 2026  
**Status:** Production Ready

### Recent Updates
- ✅ Real search functionality with 3 search modes
- ✅ Dynamic product analysis (search → analyze → update all sections)
- ✅ Trust score distribution visualization
- ✅ Google Drive integration for large files
- ✅ Visual indicators for exact matches and high trust products
- ✅ Prominent metrics dashboard
- ✅ Clean UI without debug messages

---

## Support

**Issues?** Check the troubleshooting section above or contact the project maintainer.

**Feature Requests?** Submit via project repository issues.

---

**Built with Streamlit | Powered by XGBoost | Data from Amazon Reviews**
