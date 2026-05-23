# Database Access Guide

## ✅ Phase 1 Verification: PASSED

Your Trust Scoring System database is working correctly!

**Database Details:**
- Location: `D:\Context_Aware_Trust_Scoring_Recommendation_Fashion\database\reviews.db`
- Size: 39.73 MB
- Products: 168,281
- Reviews: 10,000
- Performance: 16.52ms average query time

---

## 🌐 Method 1: Web Interface (Easiest) ⭐

**Access your database through the live website:**

**URL**: http://localhost:8501

**Features:**
- ✅ Search products by name, ID, category, brand
- ✅ View product details and trust scores
- ✅ Read reviews with trust scores
- ✅ Add new reviews
- ✅ View real-time statistics
- ✅ Filter by trust level and verification

**Status**: ✅ Currently running!

**To restart if needed:**
```bash
streamlit run demo/app_with_database.py
```

---

## 💻 Method 2: Python Code

**Access database programmatically:**

```python
from database.db_manager import DatabaseManager

# Connect to database
db = DatabaseManager(db_type='sqlite', db_path='database/reviews.db')

# Get top 10 products
products = db.get_top_products(limit=10)
for product in products:
    print(f"{product['product_name']}: {product['score_trust_weighted']:.2f}")

# Search for products
results = db.search_products('phone', limit=20)
print(f"Found {len(results)} products")

# Get a specific product
product = db.get_product('B001234567')
if product:
    print(f"Product: {product['product_name']}")
    print(f"Trust Score: {product['score_trust_weighted']}")

# Get product reviews
reviews = db.get_product_reviews('B001234567', min_trust=0.7)
print(f"High-trust reviews: {len(reviews)}")

# Get system statistics
stats = db.get_system_statistics()
print(f"Total products: {stats['total_products']:,}")
print(f"Total reviews: {stats['total_reviews']:,}")
print(f"Average trust: {stats['avg_trust_score']:.3f}")

# Close connection
db.close()
```

**Run your own queries:**
```bash
python your_script.py
```

---

## 🔧 Method 3: SQLite Browser (GUI) ⭐

**Best for browsing and exploring data visually**

### Step 1: Download DB Browser
- **Website**: https://sqlitebrowser.org/
- **Windows**: Download and install the .exe
- **Free and open-source**

### Step 2: Open Database
1. Launch DB Browser for SQLite
2. Click "Open Database"
3. Navigate to: `D:\Context_Aware_Trust_Scoring_Recommendation_Fashion\database\reviews.db`
4. Click "Open"

### Step 3: Browse Data
- **Browse Data tab**: View table contents
- **Execute SQL tab**: Run custom queries
- **Database Structure tab**: View schema

### Example Queries in DB Browser:
```sql
-- Top 10 products by trust score
SELECT product_name, score_trust_weighted, review_count
FROM products
WHERE review_count >= 5
ORDER BY score_trust_weighted DESC
LIMIT 10;

-- High-trust reviews
SELECT product_id, rating, trust_score, review_text
FROM reviews
WHERE trust_score >= 0.7
ORDER BY trust_score DESC
LIMIT 20;

-- Products by category
SELECT category, COUNT(*) as count, AVG(score_trust_weighted) as avg_trust
FROM products
GROUP BY category
ORDER BY avg_trust DESC;

-- Review statistics
SELECT 
    COUNT(*) as total_reviews,
    AVG(trust_score) as avg_trust,
    SUM(CASE WHEN verified = 1 THEN 1 ELSE 0 END) as verified_count,
    SUM(CASE WHEN trust_score >= 0.7 THEN 1 ELSE 0 END) as high_trust_count
FROM reviews;
```

---

## ⚡ Method 4: Command Line (sqlite3)

**Quick access from terminal:**

```bash
# Open database
sqlite3 database/reviews.db

# List all tables
.tables

# View table schema
.schema products

# View first 10 products
SELECT * FROM products LIMIT 10;

# Search products
SELECT product_id, product_name, score_trust_weighted 
FROM products 
WHERE product_name LIKE '%phone%' 
LIMIT 10;

# Get statistics
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM reviews;

# Exit
.quit
```

**Useful sqlite3 commands:**
```sql
.mode column          -- Format output in columns
.headers on           -- Show column headers
.width 20 50 10       -- Set column widths
.output results.txt   -- Save output to file
.output stdout        -- Back to screen
```

---

## 📁 Method 5: Direct File Access

**Database file location:**
```
D:\Context_Aware_Trust_Scoring_Recommendation_Fashion\database\reviews.db
```

**You can:**
- ✅ Copy the file for backup
- ✅ Open with any SQLite tool
- ✅ Share with team members
- ✅ Import into other applications

**Backup command:**
```bash
# Create backup
copy database\reviews.db database\reviews_backup_20260523.db

# Or use Python
python -c "import shutil; shutil.copy('database/reviews.db', 'database/reviews_backup.db')"
```

---

## 📊 Database Schema

### Tables

**1. products** (168,281 rows)
- `product_id` - Unique product identifier
- `product_name` - Product name
- `category` - Product category
- `brand` - Brand name
- `score_trust_weighted` - Trust-weighted score (main ranking)
- `avg_rating` - Average rating
- `review_count` - Number of reviews

**2. reviews** (10,000 rows)
- `review_id` - Unique review identifier
- `user_id` - User who wrote review
- `product_id` - Product being reviewed
- `rating` - Star rating (1-5)
- `review_text` - Review content
- `trust_score` - Calculated trust score (0-1)
- `verified` - Verified purchase (0/1)
- `created_at` - Review date

**3. users**
- User profile information
- Review statistics

**4. review_analytics**
- Daily aggregated statistics
- Historical trends

**5. system_logs**
- System events
- Audit trail

---

## 🔍 Common Queries

### Top Products
```sql
SELECT product_name, score_trust_weighted, review_count
FROM products
WHERE review_count >= 5
ORDER BY score_trust_weighted DESC
LIMIT 100;
```

### Search Products
```sql
SELECT product_id, product_name, category, score_trust_weighted
FROM products
WHERE product_name LIKE '%search_term%'
   OR category LIKE '%search_term%'
ORDER BY score_trust_weighted DESC;
```

### Product Reviews
```sql
SELECT rating, trust_score, verified, review_text
FROM reviews
WHERE product_id = 'B001234567'
  AND trust_score >= 0.7
ORDER BY trust_score DESC;
```

### Statistics
```sql
-- Overall statistics
SELECT 
    COUNT(DISTINCT product_id) as total_products,
    COUNT(*) as total_reviews,
    AVG(trust_score) as avg_trust,
    SUM(CASE WHEN verified = 1 THEN 1 ELSE 0 END) as verified_reviews
FROM reviews;

-- Category statistics
SELECT 
    category,
    COUNT(*) as product_count,
    AVG(score_trust_weighted) as avg_trust,
    SUM(review_count) as total_reviews
FROM products
GROUP BY category
ORDER BY avg_trust DESC;
```

---

## 🚀 Performance Tips

### Current Performance
- Average query time: **16.52ms** ✅
- Top 100 products: **18.85ms** ✅
- Search: **18.02ms** ✅
- Statistics: **12.69ms** ✅

### Optimization Options

**1. Add Indexes** (if needed)
```sql
CREATE INDEX idx_custom ON products(column_name);
```

**2. Use Redis Cache** (80-90% faster)
```bash
# Install Redis (see database/REDIS_SETUP.md)
pip install redis

# Use cached database manager
from database.db_manager_cached import CachedDatabaseManager
db = CachedDatabaseManager(cache_enabled=True)
```

**3. Migrate to PostgreSQL** (for production)
```bash
# See database/MIGRATION_GUIDE.md
python database/migrate_sqlite_to_postgresql.py
```

---

## 🛠️ Troubleshooting

### Issue: "Database is locked"
**Solution:**
```bash
# Close all connections
# Restart application
```

### Issue: "Cannot find database file"
**Solution:**
```bash
# Check path
python -c "import os; print(os.path.abspath('database/reviews.db'))"

# Verify file exists
dir database\reviews.db
```

### Issue: "Slow queries"
**Solution:**
```sql
-- Run ANALYZE to update statistics
ANALYZE;

-- Check query plan
EXPLAIN QUERY PLAN SELECT ...;
```

---

## 📚 Additional Resources

### Documentation
- **Database Manager API**: `database/README.md`
- **Migration Guide**: `database/MIGRATION_GUIDE.md`
- **Redis Setup**: `database/REDIS_SETUP.md`
- **Advanced Features**: `database/ADVANCED_FEATURES.md`

### Tools
- **DB Browser for SQLite**: https://sqlitebrowser.org/
- **SQLite Documentation**: https://www.sqlite.org/docs.html
- **Python sqlite3**: https://docs.python.org/3/library/sqlite3.html

### Scripts
- **Verify database**: `python verify_phase1_complete.py`
- **Test performance**: `python database/test_db_manager.py`
- **Verify data**: `python verify_metrics.py`

---

## ✅ Quick Access Summary

| Method | Best For | Difficulty | Features |
|--------|----------|------------|----------|
| **Web Interface** | General use | ⭐ Easy | Search, view, add reviews |
| **Python Code** | Automation | ⭐⭐ Medium | Full programmatic access |
| **DB Browser** | Exploration | ⭐ Easy | Visual browsing, SQL queries |
| **Command Line** | Quick queries | ⭐⭐ Medium | Fast terminal access |
| **Direct File** | Backup/sharing | ⭐ Easy | File operations |

---

## 🎯 Recommended Workflow

**For daily use:**
1. Use **Web Interface** (http://localhost:8501) for browsing and searching
2. Use **Python Code** for automation and integration
3. Use **DB Browser** for data exploration and analysis

**For development:**
1. Use **Python Code** for testing and debugging
2. Use **Command Line** for quick queries
3. Use **DB Browser** for schema inspection

**For production:**
1. Migrate to **PostgreSQL** for scalability
2. Add **Redis cache** for performance
3. Use **REST API** for application integration

---

**Your database is ready to use! Choose the method that works best for you.** 🚀
