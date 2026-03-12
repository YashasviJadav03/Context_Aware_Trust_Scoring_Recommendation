# Trust Scoring System - API Documentation

## Overview

The Trust Scoring System provides APIs for:
1. **Single Review Scoring** - Predict trust score for one review
2. **Batch Scoring** - Score multiple reviews efficiently
3. **Product Aggregation** - Generate product rankings
4. **Model Management** - Load, update, and monitor models

---

## Core Classes

### TrustScoringApp

Main application class for trust scoring operations.

```python
from demo.app import TrustScoringApp

app = TrustScoringApp(
    model_path="../models/trained/best_trust_model.pkl",
    scaler_path="../models/feature_scaler.pkl",
    features_path="../models/trained/feature_names.txt"
)
```

#### Methods

##### `predict_trust_score(review_data)`

Predict trust score for a single review.

**Parameters:**
- `review_data` (dict): Review information with keys:
  - `product_id` (str): Product identifier
  - `rating` (int): Rating 1-5
  - `text` (str): Review text
  - `verified` (bool): Verified purchase flag
  - `helpful_votes` (int): Number of helpful votes
  - `total_votes` (int): Total votes received
  - `user_id` (str): User identifier
  - `timestamp` (str): Review timestamp (ISO format)

**Returns:**
- `float`: Trust score between 0 and 1

**Example:**
```python
review = {
    'product_id': 'PROD_001',
    'rating': 5,
    'text': 'Great product, highly recommend!',
    'verified': True,
    'helpful_votes': 10,
    'total_votes': 12,
    'user_id': 'USER_123',
    'timestamp': '2024-01-15T10:30:00Z'
}

trust_score = app.predict_trust_score(review)
print(f"Trust Score: {trust_score:.4f}")  # Output: Trust Score: 0.8234
```

**Trust Score Interpretation:**
- `0.0 - 0.3`: Low trust (likely fake/unreliable)
- `0.3 - 0.6`: Medium trust (uncertain)
- `0.6 - 0.8`: High trust (likely genuine)
- `0.8 - 1.0`: Very high trust (very reliable)

---

##### `score_reviews(reviews_df)`

Score multiple reviews efficiently.

**Parameters:**
- `reviews_df` (pd.DataFrame): DataFrame with review data

**Returns:**
- `pd.DataFrame`: Input DataFrame with added `trust_score` column

**Example:**
```python
import pandas as pd

reviews_df = pd.read_csv('reviews.csv')
scored_df = app.score_reviews(reviews_df)

print(scored_df[['product_id', 'rating', 'trust_score']].head())
```

**Performance:**
- 1,000 reviews: ~2 seconds
- 10,000 reviews: ~15 seconds
- 100,000 reviews: ~2 minutes

---

##### `aggregate_product_scores(reviews_df)`

Aggregate review trust scores to product level.

**Parameters:**
- `reviews_df` (pd.DataFrame): DataFrame with reviews and `trust_score` column

**Returns:**
- `pd.DataFrame`: Product-level scores with columns:
  - `product_id`: Product identifier
  - `trust_weighted_score`: Trust-weighted rating (0-5)
  - `baseline_score`: Raw average rating
  - `improvement`: Difference vs baseline
  - `review_count`: Number of reviews
  - `avg_rating`: Average rating

**Formula:**
```
ProductScore = Σ(Trust_i × Rating_i) / Σ(Trust_i)
```

**Example:**
```python
product_scores = app.aggregate_product_scores(scored_df)

# Get top 10 products
top_products = product_scores.head(10)
print(top_products[['product_id', 'trust_weighted_score', 'improvement']])

# Get products with biggest improvement
improved = product_scores.nlargest(5, 'improvement')
print(improved)
```

---

##### `generate_report(reviews_df, product_scores)`

Generate a summary report.

**Parameters:**
- `reviews_df` (pd.DataFrame): Scored reviews
- `product_scores` (pd.DataFrame): Product-level scores

**Returns:**
- None (prints report to console)

**Example:**
```python
app.generate_report(scored_df, product_scores)
```

**Output:**
```
================================================================================
TRUST SCORING SYSTEM - REPORT
================================================================================

📊 REVIEW-LEVEL STATISTICS
   Total reviews: 1000
   Avg trust score: 0.6234
   Std trust score: 0.1823
   Min trust score: 0.0123
   Max trust score: 0.9876

   High trust (≥0.7):   650 (65.0%)
   Medium trust (0.4-0.7): 300 (30.0%)
   Low trust (<0.4):    50 (5.0%)

📦 PRODUCT-LEVEL STATISTICS
   Total products: 150
   Avg trust-weighted score: 4.2345
   Avg baseline score: 4.1234
   Avg improvement: 0.1111

🏆 TOP 5 PRODUCTS (by trust-weighted score)
   PROD_001             | Score: 4.8234 | Reviews:  250 | Improvement: +0.2345
   PROD_002             | Score: 4.7123 | Reviews:  180 | Improvement: +0.1234
   ...
```

---

## Feature Extraction

### extract_features(review_data)

Extract 27 features from review data.

```python
from src.features.feature_engineering import extract_features

features = extract_features(review_data)
print(features)  # Dict with 27 features
```

**Feature Categories:**

**Text Features (7):**
- `review_length`: Number of words
- `sentiment_score`: Sentiment polarity (-1 to 1)
- `sentiment_extreme`: Extreme sentiment flag
- `repetition_ratio`: Repeated words ratio
- `unique_word_ratio`: Unique words ratio
- `exclamation_count`: Number of exclamation marks
- `question_count`: Number of question marks

**Behavioral Features (7):**
- `user_review_count`: Total reviews by user
- `user_rating_variance`: Variance in user's ratings
- `user_avg_rating_deviation`: Deviation from user's average
- `user_review_frequency`: Reviews per month
- `user_extreme_ratio`: Extreme ratings ratio
- `user_burst_flag`: Burst activity flag
- `user_product_diversity`: Product diversity

**Product Features (5):**
- `product_review_count`: Total reviews for product
- `product_rating_variance`: Variance in product ratings
- `product_rating_std`: Standard deviation
- `product_popularity_log`: Log of popularity
- `product_user_diversity`: User diversity

**Temporal Features (4):**
- `days_since_first_review`: Days since first review
- `review_density`: Reviews per day
- `review_time_gap`: Gap since last review
- `burst_indicator`: Burst activity indicator

**Rating Features (4):**
- `rating`: Review rating (1-5)
- `rating_deviation`: Deviation from product average
- `verified`: Verified purchase flag
- `helpful_ratio`: Helpful votes ratio

---

## Data Formats

### Input Review Format

```json
{
  "product_id": "PROD_001",
  "rating": 5,
  "text": "Great product, highly recommend!",
  "verified": true,
  "helpful_votes": 10,
  "total_votes": 12,
  "user_id": "USER_123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Output Trust Score Format

```json
{
  "product_id": "PROD_001",
  "rating": 5,
  "text": "Great product, highly recommend!",
  "verified": true,
  "helpful_votes": 10,
  "total_votes": 12,
  "user_id": "USER_123",
  "timestamp": "2024-01-15T10:30:00Z",
  "trust_score": 0.8234
}
```

### Product Score Format

```json
{
  "product_id": "PROD_001",
  "trust_weighted_score": 4.5234,
  "baseline_score": 4.2123,
  "improvement": 0.3111,
  "review_count": 250,
  "avg_rating": 4.2123
}
```

---

## REST API Endpoints

### POST /score

Score a single review.

**Request:**
```bash
curl -X POST http://localhost:5000/score \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PROD_001",
    "rating": 5,
    "text": "Great product!",
    "verified": true,
    "helpful_votes": 10,
    "total_votes": 12,
    "user_id": "USER_123",
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

**Response:**
```json
{
  "trust_score": 0.8234,
  "status": "success"
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid input
- `500`: Server error

---

### POST /score_batch

Score multiple reviews.

**Request:**
```bash
curl -X POST http://localhost:5000/score_batch \
  -H "Content-Type: application/json" \
  -d '{
    "reviews": [
      {
        "product_id": "PROD_001",
        "rating": 5,
        "text": "Great product!",
        ...
      },
      {
        "product_id": "PROD_002",
        "rating": 3,
        "text": "Average product",
        ...
      }
    ]
  }'
```

**Response:**
```json
{
  "scores": [
    {"product_id": "PROD_001", "trust_score": 0.8234},
    {"product_id": "PROD_002", "trust_score": 0.5123}
  ],
  "status": "success",
  "count": 2
}
```

---

### POST /aggregate

Aggregate reviews to product level.

**Request:**
```bash
curl -X POST http://localhost:5000/aggregate \
  -H "Content-Type: application/json" \
  -d '{
    "reviews": [
      {
        "product_id": "PROD_001",
        "rating": 5,
        "trust_score": 0.8234
      },
      {
        "product_id": "PROD_001",
        "rating": 4,
        "trust_score": 0.7123
      }
    ]
  }'
```

**Response:**
```json
{
  "products": [
    {
      "product_id": "PROD_001",
      "trust_weighted_score": 4.5234,
      "baseline_score": 4.5,
      "improvement": 0.0234,
      "review_count": 2
    }
  ],
  "status": "success"
}
```

---

### GET /health

Check API health.

**Request:**
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0",
  "uptime_seconds": 3600
}
```

---

### GET /metrics

Get current metrics.

**Request:**
```bash
curl http://localhost:5000/metrics
```

**Response:**
```json
{
  "total_reviews_scored": 10000,
  "avg_trust_score": 0.6234,
  "high_trust_ratio": 0.65,
  "avg_processing_time_ms": 2.5,
  "errors_count": 5
}
```

---

## Error Handling

### Common Errors

**Missing Required Field:**
```json
{
  "error": "Missing required field: product_id",
  "status": "error",
  "code": 400
}
```

**Invalid Rating:**
```json
{
  "error": "Rating must be between 1 and 5",
  "status": "error",
  "code": 400
}
```

**Model Not Loaded:**
```json
{
  "error": "Model not loaded",
  "status": "error",
  "code": 500
}
```

### Error Handling Best Practices

```python
try:
    trust_score = app.predict_trust_score(review)
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
    # Fallback to baseline score
    trust_score = 0.5
```

---

## Performance Optimization

### Batch Processing

```python
# Process in batches for memory efficiency
batch_size = 10000
for i in range(0, len(df), batch_size):
    batch = df.iloc[i:i+batch_size]
    scored = app.score_reviews(batch)
    scored.to_csv(f"batch_{i}.csv", index=False)
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=10000)
def get_trust_score(review_id):
    return app.predict_trust_score(review_id)
```

### Parallel Processing

```python
from multiprocessing import Pool

with Pool(processes=4) as pool:
    scores = pool.map(app.predict_trust_score, reviews)
```

---

## Examples

### Example 1: Score Single Review

```python
from demo.app import TrustScoringApp

app = TrustScoringApp()

review = {
    'product_id': 'PROD_001',
    'rating': 5,
    'text': 'Excellent product, very satisfied!',
    'verified': True,
    'helpful_votes': 15,
    'total_votes': 16,
    'user_id': 'USER_123',
    'timestamp': '2024-01-15T10:30:00Z'
}

score = app.predict_trust_score(review)
print(f"Trust Score: {score:.4f}")
```

### Example 2: Score and Rank Products

```python
import pandas as pd
from demo.app import TrustScoringApp

app = TrustScoringApp()

# Load reviews
reviews = pd.read_csv('reviews.csv')

# Score reviews
scored = app.score_reviews(reviews)

# Aggregate to products
products = app.aggregate_product_scores(scored)

# Get top 10
top_10 = products.nlargest(10, 'trust_weighted_score')
print(top_10[['product_id', 'trust_weighted_score', 'review_count']])
```

### Example 3: Monitor Model Performance

```python
import pandas as pd
from demo.app import TrustScoringApp

app = TrustScoringApp()

# Score reviews
reviews = pd.read_csv('reviews.csv')
scored = app.score_reviews(reviews)

# Generate report
products = app.aggregate_product_scores(scored)
app.generate_report(scored, products)

# Save results
scored.to_csv('reviews_with_trust.csv', index=False)
products.to_csv('product_rankings.csv', index=False)
```

---

## Troubleshooting

### Q: Why are all trust scores the same?

**A:** Check if features are being extracted correctly:
```python
from src.features.feature_engineering import extract_features
features = extract_features(review)
print(features)  # Verify all features are present
```

### Q: Why is prediction slow?

**A:** Use batch processing instead of single predictions:
```python
# Slow
for review in reviews:
    score = app.predict_trust_score(review)

# Fast
scored = app.score_reviews(pd.DataFrame(reviews))
```

### Q: How do I update the model?

**A:** Retrain using the notebook:
```bash
jupyter nbconvert --to notebook --execute notebooks/07_trust_regression_models.ipynb
```

---

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the DEPLOYMENT_GUIDE.md
3. Check logs in `trust_scoring.log`
4. Contact the development team

---

**API Version:** 1.0  
**Last Updated:** 2024  
**Status:** Production Ready ✅
