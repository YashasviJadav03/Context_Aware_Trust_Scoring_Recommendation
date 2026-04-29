# Pre-Deployment Checklist

**Date:** April 29, 2026  
**Version:** 2.1.1

---

## ✅ BEFORE YOU DEPLOY

### 1. Upload Product Metadata to Google Drive

- [ ] Go to https://drive.google.com
- [ ] Upload `demo/product_metadata.csv`
- [ ] Set sharing to "Anyone with the link can view"
- [ ] Copy the file ID from the shareable link
- [ ] Update `demo/app.py` line ~190:
  ```python
  METADATA_FILE_ID = "your_actual_file_id_here"
  ```

### 2. Test Locally

```bash
cd demo
pip install -r requirements.txt
python -m textblob.download_corpora
streamlit run app.py
```

**Test these scenarios:**

- [ ] App loads without errors
- [ ] Product images load (test 5 products)
- [ ] Dropdown shows product names
- [ ] Click "🔴 Fake Review" → Predict → Trust score 0.10-0.30
- [ ] Click "🟢 Genuine Review" → Predict → Trust score 0.80-0.95
- [ ] Add 3 fake reviews → Trust drops, rating rises
- [ ] Review History table shows all 3 reviews
- [ ] Clear all reviews → Table disappears

### 3. Commit and Push

```bash
git add .
git commit -m "feat: Complete Phase 1-3 enhancements - ready for deployment"
git push origin main
```

### 4. Deploy to Streamlit Cloud

- [ ] Wait 2-5 minutes for auto-deployment
- [ ] Or manually deploy at https://share.streamlit.io/

### 5. Verify Deployment

- [ ] App loads at https://[your-app].streamlit.app
- [ ] Run fake review attack demo (30 seconds)
- [ ] Verify Review History table works
- [ ] Check Streamlit Cloud logs for errors

---

## 🚨 CRITICAL ITEMS

**Must be done before deployment:**

1. ✅ TextBlob in requirements.txt (already done)
2. ⚠️ Google Drive file ID updated in app.py (TODO)
3. ✅ All code changes committed
4. ⚠️ Local testing complete (TODO)

---

## 📋 QUICK TEST SCRIPT

**Run this 2-minute test before deploying:**

1. `streamlit run app.py`
2. Go to Section 5
3. Click "🔴 Fake Review" 3 times
4. Verify trust drops from 4.5 → 4.0
5. Verify Review History shows 3 rows
6. If all pass → Deploy!

---

## 🎯 SUCCESS CRITERIA

**Deployment is successful when:**

- App loads without errors ✓
- Fake review attack demo works ✓
- Review History table displays ✓
- Images load for most products ✓
- No Python exceptions ✓

---

## 📞 IF SOMETHING BREAKS

1. Check Streamlit Cloud logs
2. Test locally to isolate issue
3. Revert to previous commit if needed:
   ```bash
   git revert HEAD
   git push origin main
   ```

---

**Ready to deploy? Follow DEPLOYMENT_GUIDE.md for detailed steps!**
