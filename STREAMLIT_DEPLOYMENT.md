# Streamlit Cloud Deployment Guide

## Issue: Model Files Not Found

When deploying to Streamlit Cloud, you may encounter:
```
Error loading models: [Errno 2] No such file or directory: 'models/tfidf_vectorizer.pkl'
```

## Solution Options

### Option 1: Configure Main File Path (Recommended)

In Streamlit Cloud settings:
1. Go to your app settings
2. Set **Main file path** to: `demo/app.py`
3. The app will run from the root directory and find the models

### Option 2: Copy Model Files to Demo Folder

Copy the model files to the demo folder:
```bash
# From project root
cp models/tfidf_vectorizer.pkl demo/
cp models/feature_scaler.pkl demo/
mkdir -p demo/models/trained
cp models/trained/best_trust_model.pkl demo/models/trained/
```

Then update `demo/app.py` line 31-33 to:
```python
tfidf = joblib.load("tfidf_vectorizer.pkl")
scaler = joblib.load("feature_scaler.pkl")
model = joblib.load("models/trained/best_trust_model.pkl")
```

### Option 3: Run Without Models (Current State)

The app is already configured to run without models:
- Sections 1-4 work perfectly (use pre-computed scores)
- Section 5 (Dynamic Trust Scoring) will show a message that models aren't loaded
- All other features work normally

## Current App Behavior

✅ **Working Features (No Models Needed):**
- Product search with images
- Product analysis with current scores
- Reviews ranked by trust (pre-computed)
- Trust vs Rating comparison
- Top 10 product rankings

⚠️ **Limited Feature (Needs Models):**
- Section 5: Add new review and predict trust score
  - Will show: "Models not loaded. Running in demo mode."
  - Can still demonstrate the UI and workflow
  - Just can't predict trust scores for new reviews

## Recommended Approach for Demo

**For your professor presentation:**

1. **Use Option 1** - Set main file path to `demo/app.py` in Streamlit Cloud
   - This enables all features including live inference
   - No code changes needed
   - Models load automatically

2. **Or use current state** - App works great without models
   - Show Sections 1-4 (fully functional)
   - Explain Section 5 is the "live inference" feature
   - Mention models would be loaded in production

## Files Needed for Full Functionality

```
models/
├── tfidf_vectorizer.pkl (180 KB)
├── feature_scaler.pkl (< 1 KB)
└── trained/
    └── best_trust_model.pkl (450 KB)
```

Total size: ~630 KB (very small, easy to deploy)

## Verification

After deployment, check the app:
- ✅ Green message: "✅ Models loaded successfully!" → All features work
- ⚠️ Yellow message: "⚠️ Running in Demo Mode" → Sections 1-4 work, Section 5 limited

## Questions?

The app is designed to gracefully handle missing models and still provide a great demo experience!
