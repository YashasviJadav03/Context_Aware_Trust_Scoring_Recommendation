# 📸 Step-by-Step Deployment with Visual Guide

## 🎯 Goal: Deploy Your App Online

**Result:** Get a public URL like `https://yourname-trust-scoring.streamlit.app`

**Time:** 20 minutes total

---

## 📋 Part 1: Google Drive Setup (10 minutes)

### Step 1: Go to Google Drive

1. Open browser
2. Go to [drive.google.com](https://drive.google.com)
3. Sign in with your Google account

### Step 2: Upload Files

1. Click **"New"** button (top left)
2. Click **"File upload"**
3. Navigate to your project folder
4. Select these 2 files:
   - `data/processed/reviews_with_predicted_trust.csv`
   - `data/processed/product_trust_scores.csv`
5. Click **"Open"**
6. Wait for upload (may take 2-3 minutes for 124 MB)

### Step 3: Share First File (reviews)

1. Find `reviews_with_predicted_trust.csv` in Google Drive
2. **Right-click** on the file
3. Click **"Share"**
4. Click **"Change to anyone with the link"**
5. Make sure it says **"Viewer"** (not Editor)
6. Click **"Copy link"**
7. Paste link somewhere (Notepad, etc.)

**Your link looks like:**
```
https://drive.google.com/file/d/1ABCxyz123456789/view?usp=sharing
```

**Extract the File ID (the part between `/d/` and `/view`):**
```
1ABCxyz123456789
```

**Save this ID!** You'll need it soon.

### Step 4: Share Second File (products)

1. Find `product_trust_scores.csv` in Google Drive
2. **Right-click** on the file
3. Click **"Share"**
4. Click **"Change to anyone with the link"**
5. Make sure it says **"Viewer"**
6. Click **"Copy link"**
7. Extract File ID (same way as above)

**Save this ID too!**

### Step 5: Update Your Code

1. Open `demo/app.py` in your code editor
2. Find lines 18-19 (near the top):
   ```python
   REVIEWS_FILE_ID = "YOUR_REVIEWS_FILE_ID_HERE"
   PRODUCTS_FILE_ID = "YOUR_PRODUCTS_FILE_ID_HERE"
   ```

3. Replace with your actual IDs:
   ```python
   REVIEWS_FILE_ID = "1ABCxyz123456789"  # Your reviews ID
   PRODUCTS_FILE_ID = "1DEFabc987654321"  # Your products ID
   ```

4. **Save the file** (Ctrl+S or Cmd+S)

### Step 6: Test Locally

1. Open terminal
2. Navigate to demo folder:
   ```bash
   cd demo
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

4. Wait 10-20 seconds for data to load from Google Drive
5. If it works, you're ready for deployment!
6. Stop the app (Ctrl+C)

---

## 📋 Part 2: GitHub Setup (5 minutes)

### Step 1: Create GitHub Repository

1. Go to [github.com](https://github.com)
2. Sign in (or create account if you don't have one)
3. Click **"+"** icon (top right)
4. Click **"New repository"**
5. Fill in:
   - **Repository name:** `trust-scoring-system`
   - **Description:** "Trust-based product recommendation system"
   - **Public** (select this)
   - **DO NOT** check "Initialize with README"
6. Click **"Create repository"**

### Step 2: Push Your Code

1. Open terminal
2. Navigate to demo folder:
   ```bash
   cd demo
   ```

3. Initialize Git:
   ```bash
   git init
   ```

4. Add files:
   ```bash
   git add app.py requirements.txt .gitignore
   ```

5. Commit:
   ```bash
   git commit -m "Initial commit: Trust-based recommendation system"
   ```

6. Add remote (replace YOUR_USERNAME with your GitHub username):
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/trust-scoring-system.git
   ```

7. Push to GitHub:
   ```bash
   git branch -M main
   git push -u origin main
   ```

8. Enter your GitHub credentials if asked

### Step 3: Verify on GitHub

1. Go to your repository: `https://github.com/YOUR_USERNAME/trust-scoring-system`
2. Check you see:
   - ✅ app.py
   - ✅ requirements.txt
   - ✅ .gitignore
   - ❌ NO CSV files (they're too big)

---

## 📋 Part 3: Streamlit Cloud Deployment (5 minutes)

### Step 1: Go to Streamlit Cloud

1. Open browser
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"Sign in"**
4. Click **"Continue with GitHub"**
5. Authorize Streamlit to access your GitHub

### Step 2: Create New App

1. Click **"New app"** button (big blue button)
2. Fill in the form:
   - **Repository:** Select `YOUR_USERNAME/trust-scoring-system`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL (optional):** Choose a custom name like `yourname-trust-scoring`

3. Click **"Deploy!"** button

### Step 3: Wait for Deployment

You'll see a screen showing:
- "Installing dependencies..."
- "Running app..."
- Progress bar

**Wait 2-5 minutes.** The app is:
1. Cloning your GitHub repo
2. Installing packages from requirements.txt
3. Running app.py
4. Loading data from Google Drive (this takes time)

### Step 4: App is Live!

When deployment completes, you'll see your app!

**Your public URL:**
```
https://yourname-trust-scoring.streamlit.app
```

**Share this URL with anyone!**

---

## ✅ Verification Checklist

After deployment, check:

- [ ] App loads without errors
- [ ] You see "Data loaded: 719,967 reviews, 168,281 products"
- [ ] Dropdown shows products
- [ ] You can select a product
- [ ] Reviews display in table
- [ ] Filter slider works
- [ ] Charts display
- [ ] Product comparison shows
- [ ] Top 10 rankings display
- [ ] No error messages

---

## 🐛 Common Issues & Fixes

### Issue 1: "403 Forbidden" Error

**Problem:** Google Drive files not shared correctly

**Fix:**
1. Go to Google Drive
2. Right-click each file
3. Share → "Anyone with the link"
4. Make sure it says "Viewer"
5. Try again

### Issue 2: "File not found" Error

**Problem:** Wrong File ID in app.py

**Fix:**
1. Check your Google Drive links
2. Extract File IDs correctly (between `/d/` and `/view`)
3. Update app.py lines 18-19
4. Commit and push:
   ```bash
   git add app.py
   git commit -m "Fix File IDs"
   git push
   ```
5. Streamlit Cloud will auto-redeploy

### Issue 3: App Won't Deploy

**Problem:** Missing dependencies or syntax error

**Fix:**
1. Check requirements.txt exists
2. Check app.py has no syntax errors
3. Check GitHub repository has all files
4. Try redeploying from Streamlit Cloud

### Issue 4: Slow Loading

**This is normal!**
- First load: 10-20 seconds (downloading 124 MB from Google Drive)
- After that: Instant (cached)

---

## 🎉 Success!

When everything works, you have:

✅ App deployed online  
✅ Public URL to share  
✅ Data loaded from Google Drive  
✅ All features working  
✅ Professional demo ready  

**Share your URL:**
```
https://yourname-trust-scoring.streamlit.app
```

---

## 📝 Update Your App Later

To make changes:

1. Edit files locally
2. Test locally:
   ```bash
   streamlit run app.py
   ```

3. Commit and push:
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```

4. Streamlit Cloud auto-deploys (no manual action needed!)

---

## 🆘 Still Need Help?

**Check these guides:**
- `HOW_TO_RUN_AND_DEPLOY.md` - Detailed instructions
- `DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist
- `QUICK_START.md` - Quick reference

**Or:**
- Check Streamlit docs: [docs.streamlit.io](https://docs.streamlit.io)
- Check GitHub docs: [docs.github.com](https://docs.github.com)

---

*Step-by-Step Deployment Guide - Visual Walkthrough*
