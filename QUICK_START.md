# ⚡ Quick Start - 2 Options

## 🏠 Option 1: Run Locally (Fastest)

### One Command:
```bash
cd demo
streamlit run streamlit_app.py
```

**Opens at:** `http://localhost:8501`

**Uses:** Local CSV files

**Time:** 30 seconds

---

## 🌐 Option 2: Deploy Online (Share with Others)

### Step-by-Step:

#### 1. Google Drive Setup (10 min)

**Upload files:**
- `data/processed/reviews_with_predicted_trust.csv`
- `data/processed/product_trust_scores.csv`

**Share files:**
- Right-click → Share → "Anyone with the link"

**Get IDs:**
- From: `https://drive.google.com/file/d/1ABCxyz123/view`
- Extract: `1ABCxyz123`

**Update code:**
- Edit `demo/app.py` lines 18-19
- Replace `YOUR_REVIEWS_FILE_ID_HERE` with your ID
- Replace `YOUR_PRODUCTS_FILE_ID_HERE` with your ID

#### 2. GitHub (5 min)

```bash
cd demo
git init
git add app.py requirements.txt .gitignore
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/trust-scoring-system.git
git push -u origin main
```

#### 3. Streamlit Cloud (5 min)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repo
5. Main file: `app.py`
6. Deploy

**Your URL:** `https://yourname-trust-scoring.streamlit.app`

---

## 🎯 Which Option?

### Choose Local if:
- ✅ Just testing
- ✅ Don't need to share
- ✅ Want fastest setup

### Choose Deploy if:
- ✅ Want to share with others
- ✅ Need public URL
- ✅ Want it always online

---

## 🆘 Need Help?

**Local not working?**
```bash
pip install -r requirements.txt
```

**Deploy not working?**
- Check File IDs in app.py
- Check files shared on Google Drive

**More help:**
- See `HOW_TO_RUN_AND_DEPLOY.md` for detailed guide
- See `DEPLOYMENT_CHECKLIST.md` for step-by-step checklist

---

*Quick Start - Get Running Fast*
