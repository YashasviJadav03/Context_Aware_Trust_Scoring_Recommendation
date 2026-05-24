# 🚀 Trust-Based Product Recommendation API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000` (local) or `https://your-domain.com` (production)  
**Documentation:** `/api/docs` (Swagger UI)

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Endpoints](#endpoints)
5. [Response Format](#response-format)
6. [Error Codes](#error-codes)
7. [Examples](#examples)

---

## 🚀 Getting Started

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Start API server
python start_api.py

# Or use uvicorn directly
uvicorn api.main:app --reload --port 8000
```

### Access Documentation

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc
- **OpenAPI JSON:** http://localhost:8000/api/openapi.json

---

## 🔐 Authentication

**Current Status:** Not implemented (Phase 2.1)  
**Planned:** JWT-based authentication

For now, all endpoints are publicly accessible.

---

## ⏱️ Rate Limiting

**Default Limits:**
- 100 requests per minute
- 1000 requests per hour

**Headers:**
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets

---

## 📡 Endpoints

### Products

#### List Products
```http
GET /api/v1/products
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 50, max: 100)
- `category` (string): Filter by category
- `min_trust` (float): Minimum trust score (0-5)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "product_id": "B001234567",
      "product_name": "Premium Cotton T-Shirt",
      "category": "AMAZON_FASHION",
      "brand": "Nike",
      "avg_rating": 4.5,
      "review_count": 150,
      "score_trust_weighted": 4.7
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 50,
    "total": 168281,
    "total_pages": 3366
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Get Single Product
```http
GET /api/v1/products/{product_id}
```

#### Get Top Products
```http
GET /api/v1/products/top?limit=10
```

#### Get Products by Category
```http
GET /api/v1/products/category/{category}
```

#### Create Product (Admin)
```http
POST /api/v1/products
```

**Request Body:**
```json
{
  "product_id": "B001234567",
  "product_name": "Premium Cotton T-Shirt",
  "category": "AMAZON_FASHION",
  "brand": "Nike"
}
```

#### Update Product (Admin)
```http
PUT /api/v1/products/{product_id}
```

---

### Reviews

#### List Reviews
```http
GET /api/v1/reviews
```

**Query Parameters:**
- `page` (int): Page number
- `per_page` (int): Items per page
- `min_trust` (float): Minimum trust score (0-1)
- `verified_only` (bool): Show only verified reviews

#### Get Single Review
```http
GET /api/v1/reviews/{review_id}
```

#### Get Product Reviews
```http
GET /api/v1/products/{product_id}/reviews
```

#### Submit Review
```http
POST /api/v1/reviews
```

**Request Body:**
```json
{
  "product_id": "B001234567",
  "rating": 5,
  "review_text": "Excellent product! Highly recommend.",
  "verified": true,
  "helpful_votes": 10
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "review_id": 12345,
    "trust_score": 0.85,
    "message": "Review submitted successfully"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Update Review
```http
PUT /api/v1/reviews/{review_id}
```

#### Delete Review
```http
DELETE /api/v1/reviews/{review_id}
```

---

### Search

#### Search Products
```http
GET /api/v1/search/products?q=cotton+shirt&mode=smart&page=1&per_page=20
```

**Query Parameters:**
- `q` (string, required): Search query
- `mode` (enum): `smart`, `product_id`, `high_trust`, `category`
- `page` (int): Page number
- `per_page` (int): Items per page

#### Search Reviews
```http
GET /api/v1/search/reviews?q=excellent&page=1&per_page=20
```

#### Autocomplete
```http
GET /api/v1/search/autocomplete?q=cot&limit=10
```

---

### Analytics

#### Product Statistics
```http
GET /api/v1/analytics/product/{product_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "product_id": "B001234567",
    "total_reviews": 150,
    "avg_rating": 4.5,
    "avg_trust_score": 0.75,
    "high_trust_count": 100,
    "low_trust_count": 10,
    "verified_count": 140
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### System Statistics
```http
GET /api/v1/analytics/system
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_products": 168281,
    "total_reviews": 10000,
    "avg_trust_score": 0.572,
    "verified_reviews": 9350,
    "high_trust_reviews": 900
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Trust Score Trends
```http
GET /api/v1/analytics/trends
```

---

### ML Inference

#### Predict Trust Score
```http
POST /api/v1/predict/trust-score
```

**Request Body:**
```json
{
  "rating": 5,
  "review_text": "This is an excellent product with great quality.",
  "verified": true,
  "helpful_votes": 5
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "trust_score": 0.85,
    "confidence": 0.92,
    "category": "high"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Batch Prediction
```http
POST /api/v1/predict/batch
```

**Request Body:**
```json
{
  "reviews": [
    {
      "rating": 5,
      "review_text": "Excellent product!",
      "verified": true,
      "helpful_votes": 10
    },
    {
      "rating": 3,
      "review_text": "Average quality.",
      "verified": false,
      "helpful_votes": 2
    }
  ]
}
```

#### Model Information
```http
GET /api/v1/models/info
```

---

## 📦 Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "meta": { ... },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Product not found",
    "details": null
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## ❌ Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid input data |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_SERVER_ERROR` | 500 | Server error |

---

## 💡 Examples

### Python
```python
import requests

# Get products
response = requests.get('http://localhost:8000/api/v1/products?page=1&per_page=10')
products = response.json()

# Submit review
review_data = {
    "product_id": "B001234567",
    "rating": 5,
    "review_text": "Excellent product!",
    "verified": True
}
response = requests.post('http://localhost:8000/api/v1/reviews', json=review_data)
result = response.json()

# Predict trust score
prediction_data = {
    "rating": 5,
    "review_text": "Great quality and fast shipping!",
    "verified": True,
    "helpful_votes": 10
}
response = requests.post('http://localhost:8000/api/v1/predict/trust-score', json=prediction_data)
prediction = response.json()
```

### JavaScript
```javascript
// Get products
fetch('http://localhost:8000/api/v1/products?page=1&per_page=10')
  .then(response => response.json())
  .then(data => console.log(data));

// Submit review
fetch('http://localhost:8000/api/v1/reviews', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    product_id: 'B001234567',
    rating: 5,
    review_text: 'Excellent product!',
    verified: true
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

### cURL
```bash
# Get products
curl -X GET "http://localhost:8000/api/v1/products?page=1&per_page=10"

# Submit review
curl -X POST "http://localhost:8000/api/v1/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "B001234567",
    "rating": 5,
    "review_text": "Excellent product!",
    "verified": true
  }'

# Predict trust score
curl -X POST "http://localhost:8000/api/v1/predict/trust-score" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "review_text": "Great quality!",
    "verified": true,
    "helpful_votes": 10
  }'
```

---

## 🚀 Deployment

### Local Development
```bash
python start_api.py
```

### Production (with Gunicorn)
```bash
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📞 Support

- **Documentation:** `/api/docs`
- **Health Check:** `/health`
- **API Info:** `/`

---

**🎉 API is ready to use!**
