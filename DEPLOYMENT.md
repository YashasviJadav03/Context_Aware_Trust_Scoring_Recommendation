# Deploy to Streamlit Cloud

## Quick Deploy

1. **Push to GitHub**:
```bash
git add .
git commit -m "Deploy trust-based recommendation system"
git push origin main
```

2. **Deploy on Streamlit Cloud**:
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Select your repository
   - Set main file: `app.py`
   - Click "Deploy"

## Files for Deployment

- ✅ `app.py` - Main application (root directory)
- ✅ `requirements.txt` - Python dependencies (root directory)
- ✅ `packages.txt` - System packages (if needed)
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `data/` - Data files
- ✅ `models/` - Model files

## Requirements

Make sure these files are committed:
- All model files in `models/` directory
- All data files in `data/processed/` directory
- `requirements.txt` with all dependencies

## Alternative: Deploy to Hugging Face Spaces

1. Create account at https://huggingface.co/
2. Create new Space (Streamlit)
3. Upload all files
4. Set main file to `app.py`
5. Deploy

## Alternative: Deploy to Railway

1. Go to https://railway.app/
2. Connect GitHub repository
3. Add environment variables if needed
4. Deploy automatically

Your app will be live at a public URL!
