"""
API Test Script
Run this to test all API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_endpoint(name, method, url, data=None, params=None):
    print(f"Testing: {name}")
    print(f"  {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result:
                if isinstance(result['data'], list):
                    print(f"  Results: {len(result['data'])} items")
                elif isinstance(result['data'], dict):
                    print(f"  Data keys: {list(result['data'].keys())}")
            print("  ✅ Success")
        else:
            print(f"  ❌ Failed: {response.text}")
        
        return response
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return None

# ============================================================================
# RUN TESTS
# ============================================================================

print_section("🚀 API TEST SUITE")

# Test 1: Health Check
print_section("1. HEALTH CHECK")
test_endpoint(
    "Health Check",
    "GET",
    f"{BASE_URL}/health"
)

# Test 2: Root Endpoint
print_section("2. ROOT ENDPOINT")
test_endpoint(
    "API Info",
    "GET",
    f"{BASE_URL}/"
)

# Test 3: Products
print_section("3. PRODUCTS ENDPOINTS")

test_endpoint(
    "List Products",
    "GET",
    f"{BASE_URL}/api/v1/products",
    params={"page": 1, "per_page": 5}
)

test_endpoint(
    "Get Single Product",
    "GET",
    f"{BASE_URL}/api/v1/products/B00006HBUJ"
)

test_endpoint(
    "Top Products",
    "GET",
    f"{BASE_URL}/api/v1/products/top",
    params={"limit": 5}
)

# Test 4: Reviews
print_section("4. REVIEWS ENDPOINTS")

test_endpoint(
    "List Reviews",
    "GET",
    f"{BASE_URL}/api/v1/reviews",
    params={"page": 1, "per_page": 5}
)

test_endpoint(
    "Product Reviews",
    "GET",
    f"{BASE_URL}/api/v1/products/B00006HBUJ/reviews",
    params={"page": 1, "per_page": 5}
)

# Test 5: Search
print_section("5. SEARCH ENDPOINTS")

test_endpoint(
    "Search Products",
    "GET",
    f"{BASE_URL}/api/v1/search/products",
    params={"q": "shirt", "mode": "smart", "limit": 5}
)

test_endpoint(
    "Autocomplete",
    "GET",
    f"{BASE_URL}/api/v1/search/autocomplete",
    params={"q": "shi", "limit": 5}
)

# Test 6: Analytics
print_section("6. ANALYTICS ENDPOINTS")

test_endpoint(
    "System Statistics",
    "GET",
    f"{BASE_URL}/api/v1/analytics/system"
)

test_endpoint(
    "Product Statistics",
    "GET",
    f"{BASE_URL}/api/v1/analytics/product/B00006HBUJ"
)

test_endpoint(
    "Trends",
    "GET",
    f"{BASE_URL}/api/v1/analytics/trends"
)

# Test 7: ML Inference
print_section("7. ML INFERENCE ENDPOINTS")

test_endpoint(
    "Predict Trust Score",
    "POST",
    f"{BASE_URL}/api/v1/predict/trust-score",
    data={
        "rating": 5,
        "review_text": "Excellent product! Highly recommend for anyone looking for quality and value. Fast shipping too!",
        "verified": True,
        "helpful_votes": 10
    }
)

test_endpoint(
    "Batch Prediction",
    "POST",
    f"{BASE_URL}/api/v1/predict/batch",
    data={
        "reviews": [
            {
                "rating": 5,
                "review_text": "Excellent product! Highly recommend.",
                "verified": True,
                "helpful_votes": 10
            },
            {
                "rating": 3,
                "review_text": "Average quality, nothing special.",
                "verified": False,
                "helpful_votes": 2
            }
        ]
    }
)

test_endpoint(
    "Model Info",
    "GET",
    f"{BASE_URL}/api/v1/models/info"
)

# Test 8: Submit Review
print_section("8. SUBMIT REVIEW")

test_endpoint(
    "Submit New Review",
    "POST",
    f"{BASE_URL}/api/v1/reviews",
    data={
        "product_id": "B00006HBUJ",
        "rating": 5,
        "review_text": "This is a test review from the API test script. Great product!",
        "verified": True,
        "helpful_votes": 0
    }
)

# Summary
print_section("✅ TEST SUMMARY")
print("All API endpoints have been tested!")
print("\nNext steps:")
print("1. Check the results above")
print("2. Visit http://localhost:8000/api/docs for interactive documentation")
print("3. Try making your own API requests")
print("\n" + "="*80 + "\n")
