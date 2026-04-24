# Trust-Based Product Recommendation System - Demo

## Quick Start

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
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

---

## Features

### Section 1: Product Selection
Select a product from the dropdown to analyze its reviews.

### Section 2: Reviews Ranked by Trust
- Reviews sorted by trust score (highest first)
- Interactive trust score filter slider
- Statistics: total reviews, avg trust score, avg rating, verified %

### Section 3: Product Score Comparison
- Compare average rating vs trust-weighted score
- See the difference and what it means

### Section 4: Top Recommended Products
- Top 10 products by trust-weighted score
- Compare trust-based vs rating-based rankings

---

## Demo Goals

✅ Reviews ranked by trust (not just rating)  
✅ Product ranking improves using trust-weighted aggregation  
✅ Low-quality reviews can be filtered out

---

## Troubleshooting

**Data files not found?**  
Make sure you're running from the `demo/` directory.

**Port already in use?**  
Use: `streamlit run streamlit_app.py --server.port 8502`

**Slow loading?**  
First load caches data. Subsequent interactions will be fast.
