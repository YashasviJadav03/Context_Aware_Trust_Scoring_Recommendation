# 🚀 API Quick Start Guide

**Get your API running in 2 minutes!**

---

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start API Server
```bash
python start_api.py
```

### Step 3: Open Documentation
```
http://localhost:8000/api/docs
```

**That's it!** Your API is running! 🎉

---

## 🧪 Test Your API

### Method 1: Swagger UI (Easiest)
1. Open http://localhost:8000/api/docs
2. Click any endpoint (e.g., "GET /api/v1/products")
3. Click "Try it out"
4. Click "Execute"
5. See the response!

### Method 2: cURL
```bash
# Get products
curl http://localhost:8000/api/v1/products

# Get system stats
curl http://localhost:8000/api/v1/analytics/system

# Search products
curl "http://localhost:8000/api/v1/search/products?q=shirt"
```

### Method 3: Python
```python
import requests

# Get products
response = requests.get('http://localhost:8000/api/v1/products')
print(response.json())
```

---

## 📡 Available Endpoints

### Products
- `GET /api/v1/products` - List all products
- `GET /api/v1/products/{id}` - Get single product
- `GET /api/v1/products/top` - Top products

### Reviews
- `GET /api/v1/reviews` - List all reviews
- `POST /api/v1/reviews` - Submit new review
- `GET /api/v1/products/{id}/reviews` - Product reviews

### Search
- `GET /api/v1/search/products?q=query` - Search products
- `GET /api/v1/search/autocomplete?q=query` - Autocomplete

### Analytics
- `GET /api/v1/analytics/system` - System statistics
- `GET /api/v1/analytics/product/{id}` - Product stats

### ML Inference
- `POST /api/v1/predict/trust-score` - Predict trust score
- `GET /api/v1/models/info` - Model information

---

## 💡 Common Use Cases

### Get Top 10 Products
```bash
curl http://localhost:8000/api/v1/products/top?limit=10
```

### Submit a Review
```bash
curl -X POST http://localhost:8000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "B001234567",
    "rating": 5,
    "review_text": "Excellent product! Highly recommend.",
    "verified": true
  }'
```

### Predict Trust Score
```bash
curl -X POST http://localhost:8000/api/v1/predict/trust-score \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "review_text": "Great quality and fast shipping!",
    "verified": true,
    "helpful_votes": 10
  }'
```

### Search Products
```bash
curl "http://localhost:8000/api/v1/search/products?q=cotton+shirt&page=1&per_page=20"
```

---

## 📚 Full Documentation

- **Complete Guide:** API_DOCUMENTATION.md
- **Implementation Details:** PHASE2_COMPLETE.md
- **Interactive Docs:** http://localhost:8000/api/docs

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use different port
uvicorn api.main:app --port 8001
```

### Module Not Found
```bash
# Install dependencies
pip install -r requirements.txt
```

### Database Not Found
```bash
# Check database exists
ls database/reviews.db
```

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] Server started successfully
- [ ] Can access http://localhost:8000
- [ ] Swagger UI loads at /api/docs
- [ ] Can execute test requests
- [ ] Responses are JSON formatted

---

**🎉 You're ready to use the API!**

**Next:** Read API_DOCUMENTATION.md for detailed information.
