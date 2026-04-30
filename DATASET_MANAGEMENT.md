# Dataset Management Guide

## Available Datasets

### 1. Full Dataset (883,636 reviews)
- **Best for:** Local demos, impressive presentations
- **File:** `data/processed/reviews_full.csv` (174.8 MB)
- **Products:** 186,189
- **Avg reviews/product:** 4.7
- **RAM usage:** ~437 MB
- **Load time:** ~9 seconds

### 2. Balanced Sample (9,025 reviews)
- **Best for:** Streamlit Cloud deployment, faster loading
- **File:** `data/processed/reviews_sample_old.csv` (backup)
- **Products:** 500
- **Avg reviews/product:** 18.1
- **RAM usage:** ~25 MB
- **Load time:** <1 second

## Quick Switch Commands

### Switch to Full Dataset (for local demos)
```bash
python switch_dataset.py full
```

### Switch to Balanced Sample (for cloud deployment)
```bash
python switch_dataset.py balanced
```

### Check Current Dataset
```bash
python switch_dataset.py info
```

## Current Status

**Currently Active:** FULL DATASET (883,636 reviews)

## Deployment Recommendations

### For Local Development/Demos
✅ Use **Full Dataset**
- More impressive
- Shows real-world scale
- Better trust score calculations
- More products to search

### For Streamlit Cloud (Free Tier)
⚠️ Use **Balanced Sample**
- Faster loading
- Less memory usage
- Stays within 1GB RAM limit
- Still impressive enough

### For Streamlit Cloud (Paid Tier) or Self-Hosted
✅ Use **Full Dataset**
- Upload to Google Drive
- Update `REVIEWS_FILE_ID` in `demo/app.py`
- Or use direct file loading if self-hosted

## File Locations

```
data/processed/
├── reviews_full.csv                    # Full dataset (883K reviews)
├── reviews_sample.csv                  # Currently active dataset
├── reviews_sample_old.csv              # Balanced sample backup
├── reviews_sample_backup.csv           # Auto-backup before switch
├── product_trust_scores_full.csv       # Full product stats
├── product_trust_scores.csv            # Currently active stats
└── product_trust_scores_old.csv        # Balanced stats backup
```

## Creating Custom Samples

If you want a different sample size, edit `create_balanced_sample.py` and adjust:
- Number of products to select
- Reviews per product limit
- Review count filters

Then run:
```bash
python create_balanced_sample.py
```

## Notes

- Backups are created automatically when switching
- Original files are never modified
- You can switch back and forth anytime
- Git ignores CSV files (too large for repo)
- For cloud deployment, upload to Google Drive
