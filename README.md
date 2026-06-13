# Context-Aware Trust Scoring System for Fake Review Detection

A machine learning system for detecting fake reviews and improving product rankings through multi-signal trust scoring and weak supervision.

**Project Status:** Production Ready  
**Performance:** Precision@10: 100% (+25% vs baseline) | Spearman: 0.93 | R²: 0.84  
**Live Demo:** [https://trust-scoring-system.streamlit.app/](https://trust-scoring-system.streamlit.app/)

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Dataset](#dataset)
4. [Methodology](#methodology)
5. [Features](#features)
6. [Model Performance](#model-performance)
7. [Installation](#installation)
8. [Usage](#usage)
9. [Database Implementation](#database-implementation)
10. [Project Structure](#project-structure)
11. [Validation and Quality Assurance](#validation-and-quality-assurance)
12. [Deployment](#deployment)
13. [Documentation](#documentation)
14. [License](#license)

---

## Overview

### Problem Statement

E-commerce platforms face significant challenges with fake reviews that mislead consumers and distort product rankings. Traditional approaches rely on simple metrics (average rating, review count) that are easily manipulated.

### Solution

This system implements a context-aware trust scoring mechanism that:
- Analyzes 27 behavioral, linguistic, and temporal features
- Generates pseudo-labels through weak supervision
- Trains regression models to predict continuous trust scores
- Aggregates review-level scores to product-level rankings using Bayesian averaging
- Validates results through multiple independent signals

### Key Contributions

1. **Multi-Signal Trust Scoring:** Combines behavioral patterns, linguistic features, and temporal dynamics
2. **Weak Supervision Framework:** Generates training labels without manual annotation
3. **Data Leakage Prevention:** Proper train/test separation for TF-IDF and all features
4. **External Validation:** Four independent tests prove model validity beyond pseudo-labels
5. **Bayesian Product Aggregation:** Prevents single-review products from dominating rankings
6. **Database Architecture:** Production-ready database implementation with SQLite and PostgreSQL support

---

## System Architecture

```
Input: Raw Reviews
    ↓
[Data Cleaning & Preprocessing]
    ↓
[Feature Engineering: 27 Features + TF-IDF (5000 dimensions)]
    ↓
[Weak Labeling: Rule-based Trust Score Generation]
    ↓
[Model Training: XGBoost Regression]
    ↓
[Product Aggregation: Bayesian Trust-Weighted Ranking]
    ↓
[External Validation: 4 Independent Tests]
    ↓
[Database Storage: SQLite/PostgreSQL]
    ↓
Output: Trust Scores & Product Rankings
```

---

## Dataset

**Source:** Amazon Fashion Reviews Dataset

**Statistics:**
- Total Reviews: 883,636 (full dataset)
- Sample Dataset: 9,000 reviews (balanced for cloud deployment)
- Products: 168,281 unique products
- Users: 339,231 unique users
- Time Period: 2000-2018
- Review Length: 3-500 words (after filtering)

**Data Split:**
- Training: 70% (503,976 reviews)
- Validation: 15% (107,995 reviews)
- Test: 15% (107,996 reviews)

**Key Characteristics:**
- Verified Purchase: 73.2%
- Helpful Votes: 10.5% of reviews have votes
- Rating Distribution: Mean 4.1, Std 1.2
- Review Length: Mean 47 words, Median 32 words

---

## Methodology

### Phase 1: Data Preprocessing

**Notebooks:** `01_dataset_overview.ipynb`, `02_basic_cleaning.ipynb`

**Steps:**
1. Load raw JSON data
2. Remove duplicates and null values
3. Filter reviews with length < 3 words
4. Parse timestamps and helpful votes
5. Text cleaning (lowercase, remove special characters)
6. Handle missing values

### Phase 2: Exploratory Data Analysis

**Notebook:** `03_review_eda.ipynb`

**Analysis:**
- Rating distribution and temporal patterns
- User behavior analysis (review frequency, rating variance)
- Product popularity and review density
- Helpful votes distribution
- Verified purchase patterns

### Phase 3: Weak Labeling

**Notebook:** `05_1_weak_labelling.ipynb`

**Trust Score Formula:**

For reviews WITH helpful votes (10.5%):
```
trust_score = 0.35 × helpful_ratio + 0.25 × rating_score + 
              0.25 × user_consistency + 0.15 × verified_score - penalties
```

For reviews WITHOUT helpful votes (89.5%):
```
trust_score = 0.40 × rating_score + 0.35 × user_consistency + 
              0.25 × verified_score - penalties
```

**Penalties:**
- Duplicate reviews: -0.15
- High frequency (>3 reviews/day): -0.10
- Short extreme reviews: -0.05
- Rating deviation (>3 stars from product mean): -0.05

### Phase 4: Feature Engineering

**Notebook:** `06_feature_engineering.ipynb`

**Critical Implementation:**
- TF-IDF fitted ONLY on training data (prevents data leakage)
- Validation and test sets transformed using training vocabulary
- All features computed independently per split

**Features:** 27 structured features + 5000 TF-IDF features = 5027 total dimensions

### Phase 5: Binary Classification

**Notebook:** `05_2_unified_classifier_comparison.ipynb`

**Purpose:** Train binary fake/real classifier for cross-system validation

**Best Model:** XGBoost Classifier (F1=0.75)

### Phase 6: Model Training

**Notebook:** `07_trust_regression_models.ipynb`

**Models Evaluated:**
1. XGBoost Regressor (best performer)
2. Gradient Boosting Regressor
3. Random Forest Regressor
4. Linear Regression (baseline)

**Best Model Performance:**
- Test Spearman: 0.9306
- Test R²: 0.8429
- Test RMSE: 0.0501

### Phase 7: Product Aggregation

**Notebook:** `08_product_trust_aggregation.ipynb`

**Bayesian Average Formula:**
```
product_score = (n × trust_weighted_rating + m × C) / (n + m)

where:
  n = number of reviews for product
  m = 5 (minimum review threshold)
  C = global mean rating (3.78)
```

### Phase 8: Evaluation and Validation

**Notebook:** `09_evaluation_validation.ipynb`

**Evaluation Components:**
1. Review-level metrics (RMSE, MAE, R², Spearman)
2. Product-level metrics (NDCG@K, Precision@K)
3. Feature importance analysis
4. Ablation studies
5. External validation tests (4 independent tests)
6. Cross-system validation

---

## Features

### Structured Features (27 total)

#### Text Features (7)
- `review_length`: Word count
- `sentiment_score`: VADER compound sentiment (-1 to 1)
- `sentiment_extreme`: Absolute sentiment value
- `repetition_ratio`: 1 - (unique words / total words)
- `unique_word_ratio`: Unique words / total words
- `exclamation_count`: Number of exclamation marks
- `question_count`: Number of question marks

#### Behavioral Features (7)
- `user_review_count`: Total reviews by user
- `user_rating_variance`: Variance in user's ratings
- `user_avg_rating_deviation`: Mean deviation from product averages
- `user_review_frequency`: Reviews per day active
- `user_extreme_ratio`: Proportion of 1 or 5-star ratings
- `user_burst_flag`: More than 3 reviews in one day
- `user_product_diversity`: Number of unique products reviewed

#### Product Features (5)
- `product_review_count`: Total reviews for product
- `product_rating_variance`: Variance in product ratings
- `product_rating_std`: Standard deviation of ratings
- `product_popularity_log`: Log-transformed review count
- `product_user_diversity`: Number of unique reviewers

#### Temporal Features (4)
- `days_since_first_review`: Days since product's first review
- `review_density`: Reviews per day for product
- `review_time_gap`: Days since previous review for product
- `burst_indicator`: Review during high-activity period

#### Rating Features (4)
- `rating`: Star rating (1-5)
- `rating_deviation`: Absolute difference from product mean
- `verified`: Verified purchase indicator (0/1)
- `helpful_ratio`: Helpful votes / (helpful votes + 1)

### TF-IDF Features (5000)

- N-gram range: (1, 2)
- Max features: 5000
- Stop words: English
- Fitted on training data only

---

## Model Performance

### Review-Level Metrics (Test Set)

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Spearman Correlation | 0.93 | Excellent monotonic relationship |
| R² Score | 0.84 | 84% variance explained |
| RMSE | 0.050 | Low prediction error |
| MAE | 0.024 | Mean absolute error |

### Product-Level Metrics

| Metric | Trust-Weighted | Baseline (Avg Rating) | Improvement |
|--------|----------------|----------------------|-------------|
| **Precision@10** | **100%** | **80%** | **+25.0%** |
| **Precision@5** | **100%** | **60%** | **+66.7%** |
| NDCG@10 | 0.965 | 0.859 | +12.3% |
| NDCG@5 | 0.973 | 0.821 | +18.5% |

### Feature Importance (Top 5)

| Feature | Importance | Type |
|---------|-----------|------|
| verified | 0.496 | Rating |
| rating_deviation | 0.300 | Rating |
| user_review_count | 0.116 | Behavioral |
| rating | 0.031 | Rating |
| review_length | 0.025 | Text |

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- 8GB RAM minimum (16GB recommended)
- 5GB disk space

### Setup

```bash
# Clone repository
git clone <repository-url>
cd trust-scoring-system

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows bash)
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Verify installation
python -c "import sklearn, xgboost, pandas, numpy; print('Installation successful')"
```

### Dependencies

**Core Libraries:**
- pandas >= 1.3.0
- numpy >= 1.21.0
- scikit-learn >= 1.0.0
- xgboost >= 1.5.0
- scipy >= 1.7.0

**NLP Libraries:**
- vaderSentiment >= 3.3.2
- spacy >= 3.0.0

**Visualization:**
- matplotlib >= 3.4.0
- seaborn >= 0.11.0
- plotly >= 5.0.0

**Database:**
- sqlite3 (built-in)
- psycopg2-binary >= 2.9.0 (for PostgreSQL)

**Web Application:**
- streamlit >= 1.20.0

---

## Usage

### Basic Usage

```python
import pandas as pd
from src.models.trust_model import TrustModel

# Initialize model
model = TrustModel()

# Load reviews
reviews = pd.DataFrame({
    'user_id': ['U001', 'U002', 'U003'],
    'product_id': ['P001', 'P001', 'P002'],
    'rating': [5, 4, 1],
    'review_text': [
        'Great product, highly recommend!',
        'Good quality, fast shipping.',
        'Terrible, broke after one use.'
    ],
    'verified': [True, True, False],
    'helpful_votes': [10, 5, 0]
})

# Score reviews
scored_reviews = model.predict_trust_scores(reviews)
print(scored_reviews[['user_id', 'product_id', 'trust_score']])
```

### Running the Demo Application

```bash
# Navigate to demo folder
cd demo

# Run Streamlit app
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Dataset Management

Switch between full dataset (883K reviews) and balanced sample (9K reviews):

```bash
# Switch to full dataset
python switch_dataset.py --mode full

# Switch to sample dataset
python switch_dataset.py --mode sample
```

---

## Database Implementation

### Overview

The system includes a production-ready database implementation supporting both SQLite (local development) and PostgreSQL (production deployment).

### Database Schema

**Tables:**
- `products`: Product information and trust scores
- `reviews`: Individual review data with trust scores
- `users`: User information and statistics
- `review_analytics`: Aggregated review statistics
- `system_logs`: System event tracking

**Views:**
- `vw_product_summary`: Product statistics with review counts
- `vw_top_products`: Top 100 products by trust score
- `vw_recent_reviews`: Recent 1000 reviews

**Triggers:**
- Automatic product statistics updates on review insert/delete
- Timestamp updates on record modifications

### Database Setup

#### Initialize Database

```bash
# Create database and schema
python database/migrate_csv_to_db.py
```

This script:
1. Creates database schema from `database/schema.sql`
2. Migrates data from CSV files to database
3. Creates indexes for optimized queries
4. Validates data integrity

#### Database Configuration

**SQLite (Local Development):**
```python
from database.db_manager import DatabaseManager

db = DatabaseManager(db_type='sqlite', db_path='database/reviews.db')
```

**PostgreSQL (Production):**
```python
db = DatabaseManager(
    db_type='postgresql',
    host='localhost',
    port=5432,
    database='trust_scoring',
    user='your_user',
    password='your_password'
)
```

### Database Operations

#### Query Products

```python
# Search products
products = db.search_products('laptop', limit=20)

# Get top products
top_products = db.get_top_products(limit=100, min_reviews=5)

# Get product by ID
product = db.get_product('B00XT15P8E')
```

#### Query Reviews

```python
# Get product reviews
reviews = db.get_product_reviews('B00XT15P8E', min_trust=0.5)

# Get recent reviews
recent = db.get_recent_reviews(limit=100)
```

#### Insert Data

```python
# Insert single review
review_data = {
    'user_id': 'U001',
    'product_id': 'P001',
    'rating': 5,
    'review_text': 'Excellent product!',
    'verified': True,
    'helpful_votes': 10,
    'trust_score': 0.85
}
review_id = db.insert_review(review_data)

# Bulk insert from DataFrame
db.bulk_insert_reviews(reviews_df)
```

#### Analytics

```python
# Get product statistics
stats = db.get_product_statistics('B00XT15P8E')

# Get system statistics
system_stats = db.get_system_statistics()
```

### Running Database Version

```bash
# Run database-powered demo
streamlit run demo/app_with_database.py
```

### Database Performance

**Query Performance:**
- Product search: <50ms
- Review retrieval (1000 reviews): <100ms
- Product statistics: <30ms
- Bulk insert (10K reviews): ~2 seconds

**Optimization:**
- Indexed columns for fast lookups
- Materialized views for common queries
- Automatic statistics updates via triggers
- Connection pooling for concurrent access

---

## Project Structure

```
trust-scoring-system/
│
├── notebooks/                          # Jupyter notebooks (analysis pipeline)
│   ├── 01_dataset_overview.ipynb
│   ├── 02_basic_cleaning.ipynb
│   ├── 03_review_eda.ipynb
│   ├── 05_1_weak_labelling.ipynb
│   ├── 05_2_unified_classifier_comparison.ipynb
│   ├── 06_feature_engineering.ipynb
│   ├── 07_trust_regression_models.ipynb
│   ├── 08_product_trust_aggregation.ipynb
│   └── 09_evaluation_validation.ipynb
│
├── src/                                # Source code
│   ├── data/
│   │   ├── __init__.py
│   │   └── preprocess.py
│   ├── features/
│   │   ├── __init__.py
│   │   └── feature_engineering.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── trust_model.py
│   └── __init__.py
│
├── database/                           # Database implementation
│   ├── schema.sql                      # Database schema
│   ├── db_manager.py                   # Database operations
│   └── migrate_csv_to_db.py            # CSV to database migration
│
├── models/                             # Trained models
│   ├── feature_scaler.pkl
│   ├── tfidf_vectorizer.pkl
│   └── trained/
│       ├── best_trust_model.pkl
│       ├── binary_classifier_xgboost.pkl
│       └── feature_names.txt
│
├── data/                               # Data directory
│   ├── raw/                            # Original datasets
│   │   ├── AMAZON_FASHION.json
│   │   ├── Electronics.json.gz
│   │   ├── meta_AMAZON_FASHION.json.gz
│   │   └── meta_Electronics.json.gz
│   └── processed/                      # Processed datasets
│       ├── reviews_full.csv            # Full dataset (883K reviews)
│       ├── reviews_sample.csv          # Sample dataset (9K reviews)
│       ├── product_trust_scores_full.csv
│       └── product_trust_scores.csv
│
├── results/                            # Results and outputs
│   ├── reports/                        # Metric reports (CSV)
│   │   ├── trust_model_comparison.csv
│   │   ├── ranking_metrics.csv
│   │   ├── feature_importance.csv
│   │   └── FINAL_EVALUATION_REPORT.txt
│   └── figures/                        # Visualizations (PNG)
│       ├── feature_importance.png
│       ├── trust_model_comparison.png
│       └── prediction_analysis.png
│
├── demo/                               # Demo applications
│   ├── app.py                          # Main Streamlit app (CSV-based)
│   ├── app_dynamic.py                  # Dynamic version with Plotly
│   ├── app_with_database.py            # Database-powered version
│   ├── requirements.txt
│   ├── README.md
│   ├── reviews_sample.csv
│   ├── products_sample.csv
│   └── product_metadata.csv
│
├── .gitignore
├── requirements.txt
├── README.md                           # This file
├── QUICK_START.md
├── FINAL_PROJECT_REPORT.md
├── DEMO_SCRIPT.md
├── STREAMLIT_DEPLOYMENT.md
├── DATASET_MANAGEMENT.md
├── DYNAMIC_FEATURES_GUIDE.md
└── switch_dataset.py
```

---

## Validation and Quality Assurance

### Data Leakage Prevention

**Solution Implemented:**
1. Split data FIRST into train/val/test
2. Fit TF-IDF vectorizer ONLY on training text
3. Transform validation and test sets using training vocabulary
4. No test set information leaks into training

### External Validation

Four independent validation tests:

#### Test 1: Verified Purchase Validation
- Result: Mean trust 0.58 (verified) vs 0.54 (unverified)
- Statistical Test: Mann-Whitney U, p < 0.001
- Status: PASSED

#### Test 2: Helpful Votes Validation
- Result: Mean trust 0.62 (with votes) vs 0.57 (no votes)
- Statistical Test: Mann-Whitney U, p < 0.001
- Status: PASSED

#### Test 3: Rating Patterns Validation
- Result: Mean trust 0.57 (extreme) vs 0.59 (moderate)
- Statistical Test: Mann-Whitney U, p < 0.001
- Status: PASSED

#### Test 4: Binary Classification Agreement
- Result: Reviews predicted as fake have significantly lower trust scores
- Statistical Test: Mann-Whitney U, p < 0.001
- Status: PASSED

### Cross-Validation

**Method:** 5-fold stratified cross-validation

**Results:**
- Mean R²: 0.84 ± 0.01
- Mean Spearman: 0.93 ± 0.01

### Ablation Study

**Results (R² Degradation):**
- Full Model R²: 0.843
- Without Rating Features: R² = 0.368 (-56.4%)
- Without User-Behavioral Features: R² = 0.680 (-19.3%)
- Without Text Features: R² = 0.798 (-5.3%)

---

## Deployment

### Live Demo (Production)

**URL:** [https://context-aware-trust-scoring-recommendation.streamlit.app](https://context-aware-trust-scoring-recommendation.streamlit.app)

**Features:**
- Real product search with 3 search modes
- Dynamic product analysis
- Trust score distribution visualization
- Side-by-side ranking comparison
- Interactive review filtering
- Live ML inference for trust score prediction
- Dynamic review addition with real-time updates

**Technical Stack:**
- Platform: Streamlit Cloud
- Data Hosting: Google Drive (cloud-hosted CSV files)
- ML Models: XGBoost Regressor, TF-IDF Vectorizer, StandardScaler
- Dataset: Amazon Fashion reviews (9K sample)
- Performance: 2-3s first load, instant subsequent loads

### Local Deployment

```bash
# Navigate to demo folder
cd demo

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py
```

### Docker Deployment

```bash
# Build Docker image
docker build -t trust-scoring-system .

# Run container
docker run -p 8501:8501 trust-scoring-system
```

### Streamlit Cloud Deployment

1. Push to GitHub
2. Go to https://share.streamlit.io
3. Click "New app"
4. Select repository and branch
5. Set main file path: `demo/app.py`
6. Click "Deploy"

### Performance Considerations

**Demo App Performance:**
- First load: 2-3 seconds
- Subsequent loads: Instant (cached)
- Search: Real-time filtering (<100ms)

**Production API Performance:**
- Single review scoring: ~50ms
- Batch processing (1000 reviews): ~5 seconds
- Product aggregation (10,000 products): ~2 seconds

**Resource Requirements:**
- Demo App: 512MB RAM, 1 CPU core
- Production API: 4GB RAM, 2-4 CPU cores
- Storage: 5GB for models and data

---

## Documentation

### Available Documentation

- **README.md** - Complete project overview and usage guide
- **demo/README.md** - Demo application documentation
- **QUICK_START.md** - Quick start guide
- **FINAL_PROJECT_REPORT.md** - Comprehensive academic report
- **DEMO_SCRIPT.md** - Demo presentation script
- **STREAMLIT_DEPLOYMENT.md** - Deployment guide
- **DATASET_MANAGEMENT.md** - Dataset switching guide
- **DYNAMIC_FEATURES_GUIDE.md** - Dynamic features implementation

### Notebooks Documentation

Each notebook contains:
- Markdown cells explaining methodology
- Code comments for complex operations
- Output cells showing results
- Diagnostic plots and tables

---

## License

MIT License

---

## Contact

**Project Repository:** [Repository URL]  
**Live Demo:** https://trust-scoring-system.streamlit.app/

---

**Version:** 2.1.0  
**Last Updated:** May 5, 2026  
**Status:** Production Ready  
**Python Version:** 3.8+
