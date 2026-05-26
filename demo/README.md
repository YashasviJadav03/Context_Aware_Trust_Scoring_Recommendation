# Trust-Based Recommendation Demo

Simple Streamlit app to find trustworthy products based on review analysis.

## Setup

```bash
cd demo
pip install -r requirements.txt
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

## Run

```bash
streamlit run app_dynamic.py
```

## Features

1. **Product Recommendations** - Filter by trust score and review count
2. **Review Analysis** - See why products are trustworthy
3. **Live Prediction** - Test any review text

## Data

- 500 products
- 9,025 reviews
- 10-27 reviews per product (avg: 18)

## Model Performance

- **R² Score**: 0.847 (explains 84.7% of variance)
- **MAE**: 0.082 (predictions within ±0.08)
- **Features**: 10+ including sentiment, text quality, behavioral patterns
