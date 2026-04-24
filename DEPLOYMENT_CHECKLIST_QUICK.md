# ✅ Quick Deployment Checklist

## Before Clicking "Deploy" on Streamlit Cloud:

### 1. Upload CSV Files to Google Drive
- [ ] Upload `data/processed/reviews_with_predicted_trust.csv`
- [ ] Upload `data/processed/product_trust_scores.csv`
- [ ] Set sharing to "Anyone with the link"
- [ ] Copy File IDs from URLs

### 2. Update demo/app.py
- [ ] Replace `YOUR_REVIEWS_FILE_ID_HERE` with actual File ID
- [ ] Replace `YOUR_PRODUCTS_FILE_ID_HERE` with actual File ID
- [ ] Save the file

### 3. Push to GitHub
```bash
git add .
git commit -m "Update File IDs for deployment"
git push origin main
```

### 4. Streamlit Cloud Form
- **Repository:** `https://github.com/YashasviJadav03/Context_Aware_Trust_Scoring_Recommendation.git`
- **Branch:** `main`
- **Main file path:** `demo/app.py`
- **App URL:** `trust-scoring-system` (optional)

### 5. After Deployment
- [ ] Test the deployed app
- [ ] Verify data loads correctly
- [ ] Update README.md with live URL
- [ ] Test demo flow

---

## Current Status:
- ✅ GitHub repo exists
- ✅ Code is ready
- ⏳ Need to upload CSV files
- ⏳ Need to update File IDs
- ⏳ Need to push changes
- ⏳ Need to deploy on Streamlit Cloud

## Next Action:
**Upload your CSV files to Google Drive first!**