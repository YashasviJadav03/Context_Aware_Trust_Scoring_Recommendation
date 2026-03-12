# Trust Scoring System - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda
- 2GB RAM minimum
- 500MB disk space for models

### Installation

```bash
# 1. Clone repository
git clone <repo-url>
cd trust-scoring-system

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download spaCy model (for NLP features)
python -m spacy download en_core_web_sm
```

---

## 📦 Production Deployment

### Option 1: Batch Processing

For processing large batches of reviews:

```python
import pandas as pd
from demo.app import TrustScoringApp

# Initialize
app = TrustScoringApp()

# Load reviews
reviews_df = pd.read_csv("reviews.csv")

# Score reviews
scored_reviews = app.score_reviews(reviews_df)

# Aggregate to products
product_scores = app.aggregate_product_scores(scored_reviews)

# Save results
product_scores.to_csv("product_rankings.csv", index=False)
```

### Option 2: Real-Time API

For real-time scoring via REST API:

```python
from flask import Flask, request, jsonify
from demo.app import TrustScoringApp

app = Flask(__name__)
trust_app = TrustScoringApp()

@app.route('/score', methods=['POST'])
def score_review():
    """Score a single review."""
    review_data = request.json
    trust_score = trust_app.predict_trust_score(review_data)
    return jsonify({'trust_score': float(trust_score)})

@app.route('/score_batch', methods=['POST'])
def score_batch():
    """Score multiple reviews."""
    reviews = request.json['reviews']
    reviews_df = pd.DataFrame(reviews)
    scored = trust_app.score_reviews(reviews_df)
    return jsonify(scored.to_dict('records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Option 3: Scheduled Retraining

For periodic model updates:

```bash
# Create cron job (Linux/Mac)
0 0 * * 0 cd /path/to/project && python notebooks/07_trust_regression_models.ipynb

# Or use Windows Task Scheduler
# Task: Run python notebooks/07_trust_regression_models.ipynb
# Schedule: Weekly (Sunday at midnight)
```

---

## 🔧 Configuration

### Model Parameters

Edit `src/models/trust_model.py` to adjust:

```python
# XGBoost hyperparameters
XGBOOST_PARAMS = {
    'n_estimators': 100,      # Number of trees
    'learning_rate': 0.1,     # Learning rate
    'max_depth': 6,           # Tree depth
    'subsample': 0.8,         # Row sampling
    'colsample_bytree': 0.8,  # Column sampling
    'random_state': 42
}

# Feature scaling
SCALER_TYPE = 'StandardScaler'  # or 'MinMaxScaler'

# Trust score thresholds
HIGH_TRUST_THRESHOLD = 0.7
MEDIUM_TRUST_THRESHOLD = 0.4
```

### Feature Configuration

Edit `src/features/feature_engineering.py` to:
- Add/remove features
- Adjust feature weights
- Change text processing parameters

---

## 📊 Monitoring

### Key Metrics to Track

```python
# Daily monitoring
daily_metrics = {
    'avg_trust_score': reviews_df['trust_score'].mean(),
    'high_trust_ratio': (reviews_df['trust_score'] >= 0.7).sum() / len(reviews_df),
    'prediction_std': reviews_df['trust_score'].std(),
    'processing_time': elapsed_time
}

# Weekly monitoring
weekly_metrics = {
    'ndcg_at_10': calculate_ndcg(product_scores, k=10),
    'precision_at_10': calculate_precision(product_scores, k=10),
    'ranking_stability': compare_rankings(current, previous_week)
}

# Monthly monitoring
monthly_metrics = {
    'model_drift': compare_distributions(current_month, baseline),
    'feature_importance_change': compare_importances(current, baseline),
    'business_impact': measure_recommendation_quality()
}
```

### Alerting

Set up alerts for:
- **CRITICAL**: NDCG@10 drops below 0.75
- **WARNING**: Average trust score changes > 10%
- **INFO**: Model drift detected (KL divergence > 0.1)

---

## 🔄 Retraining Pipeline

### When to Retrain

- **Weekly**: Check model performance
- **Monthly**: Full retraining if drift detected
- **Quarterly**: Scheduled retraining with new data

### Retraining Steps

```bash
# 1. Collect new reviews
python scripts/collect_reviews.py

# 2. Run preprocessing
jupyter nbconvert --to notebook --execute notebooks/02_basic_cleaning.ipynb

# 3. Generate pseudo-labels
jupyter nbconvert --to notebook --execute notebooks/05_weak_labelling.ipynb

# 4. Engineer features
jupyter nbconvert --to notebook --execute notebooks/06_feature_engineering.ipynb

# 5. Train models
jupyter nbconvert --to notebook --execute notebooks/07_trust_regression_models.ipynb

# 6. Evaluate
jupyter nbconvert --to notebook --execute notebooks/09_evaluation_validation.ipynb

# 7. Deploy if performance improved
python scripts/deploy_model.py
```

---

## 🐛 Troubleshooting

### Issue: Model predictions are all zeros

**Solution:**
```python
# Check feature scaling
X_scaled = scaler.transform(X)
print(X_scaled.mean(axis=0))  # Should be close to 0
print(X_scaled.std(axis=0))   # Should be close to 1

# Verify features exist
print(X.columns)
print(feature_names)
```

### Issue: Out of memory error

**Solution:**
```python
# Process in batches
batch_size = 10000
for i in range(0, len(df), batch_size):
    batch = df.iloc[i:i+batch_size]
    scores = app.score_reviews(batch)
    scores.to_csv(f"batch_{i}.csv", index=False)
```

### Issue: Slow predictions

**Solution:**
```python
# Use GPU acceleration
from xgboost import XGBRegressor
model = XGBRegressor(tree_method='gpu_hist', gpu_id=0)

# Or batch process
import numpy as np
X_batches = np.array_split(X, 10)
predictions = np.concatenate([
    model.predict(batch) for batch in X_batches
])
```

---

## 📈 Performance Optimization

### Vectorization

```python
# ❌ Slow: Loop over rows
scores = []
for idx, row in df.iterrows():
    score = model.predict(row.values.reshape(1, -1))
    scores.append(score)

# ✅ Fast: Vectorized prediction
scores = model.predict(df.values)
```

### Caching

```python
# Cache feature extraction
from functools import lru_cache

@lru_cache(maxsize=10000)
def extract_features_cached(review_id, review_text):
    return extract_features({'id': review_id, 'text': review_text})
```

### Parallel Processing

```python
from multiprocessing import Pool

def score_review_parallel(review):
    return app.predict_trust_score(review)

with Pool(processes=4) as pool:
    scores = pool.map(score_review_parallel, reviews)
```

---

## 🔐 Security

### Model Protection

```python
# Encrypt model file
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

with open('best_trust_model.pkl', 'rb') as f:
    encrypted = cipher.encrypt(f.read())

with open('best_trust_model.pkl.enc', 'wb') as f:
    f.write(encrypted)
```

### Input Validation

```python
def validate_review(review_data):
    """Validate review data before scoring."""
    required_fields = ['product_id', 'rating', 'text']
    
    for field in required_fields:
        if field not in review_data:
            raise ValueError(f"Missing required field: {field}")
    
    if not 1 <= review_data['rating'] <= 5:
        raise ValueError("Rating must be between 1 and 5")
    
    if len(review_data['text']) < 10:
        raise ValueError("Review text too short")
    
    return True
```

---

## 📝 Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trust_scoring.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usage
logger.info(f"Scored {len(reviews_df)} reviews")
logger.warning(f"Model drift detected: KL divergence = {kl_div}")
logger.error(f"Failed to load model: {error}")
```

---

## 🧪 Testing

### Unit Tests

```python
import unittest

class TestTrustScoring(unittest.TestCase):
    
    def setUp(self):
        self.app = TrustScoringApp()
    
    def test_score_range(self):
        """Trust scores should be between 0 and 1."""
        score = self.app.predict_trust_score(sample_review)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)
    
    def test_reproducibility(self):
        """Same input should produce same output."""
        score1 = self.app.predict_trust_score(sample_review)
        score2 = self.app.predict_trust_score(sample_review)
        self.assertEqual(score1, score2)

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

```bash
# Run all notebooks
pytest notebooks/ --nbval

# Run specific notebook
pytest notebooks/07_trust_regression_models.ipynb --nbval
```

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks

- **Daily**: Monitor prediction distribution
- **Weekly**: Check model performance metrics
- **Monthly**: Review feature importance changes
- **Quarterly**: Full model retraining
- **Annually**: Architecture review and optimization

### Contact & Escalation

- **Performance Issues**: Check monitoring dashboard
- **Model Drift**: Trigger retraining pipeline
- **Data Quality**: Review preprocessing pipeline
- **Production Errors**: Check logs and error handling

---

## ✅ Deployment Checklist

- [ ] All dependencies installed
- [ ] Model files present and accessible
- [ ] Feature scaler loaded correctly
- [ ] Sample predictions working
- [ ] Monitoring dashboard set up
- [ ] Logging configured
- [ ] Error handling in place
- [ ] Backup strategy defined
- [ ] Retraining schedule set
- [ ] Documentation reviewed

---

## 🎯 Success Criteria

After deployment, verify:

✅ **Performance**
- NDCG@10 ≥ 0.80
- Spearman correlation ≥ 0.75
- Prediction latency < 100ms

✅ **Reliability**
- 99.9% uptime
- < 0.1% error rate
- Graceful degradation

✅ **Scalability**
- Process 1M reviews/day
- Real-time API response < 500ms
- Memory usage < 2GB

✅ **Maintainability**
- Clear logs and monitoring
- Documented procedures
- Automated retraining

---

**For questions or issues, refer to the main README.md or contact the development team.**
