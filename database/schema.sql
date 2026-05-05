-- Trust-Based Product Recommendation System Database Schema
-- Supports both SQLite (local) and PostgreSQL (production)

-- ============================================================================
-- PRODUCTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(500),
    category VARCHAR(100),
    brand VARCHAR(200),
    price VARCHAR(50),
    image_url TEXT,
    description TEXT,
    avg_rating DECIMAL(3,2),
    rating_std DECIMAL(4,3),
    review_count INTEGER DEFAULT 0,
    score_raw_avg DECIMAL(4,3),
    score_count_weighted DECIMAL(4,3),
    score_trust_weighted DECIMAL(4,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_products_trust_score ON products(score_trust_weighted DESC);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(product_name);

-- ============================================================================
-- REVIEWS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    verified BOOLEAN DEFAULT FALSE,
    helpful_votes INTEGER DEFAULT 0,
    trust_score DECIMAL(5,4),
    predicted_trust_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user ON reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_trust_score ON reviews(trust_score DESC);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_created ON reviews(created_at DESC);

-- ============================================================================
-- USERS TABLE (Optional - for future user management)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(255),
    total_reviews INTEGER DEFAULT 0,
    avg_trust_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================================================
-- REVIEW ANALYTICS TABLE (Aggregated statistics)
-- ============================================================================
CREATE TABLE IF NOT EXISTS review_analytics (
    analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    total_reviews INTEGER DEFAULT 0,
    avg_rating DECIMAL(3,2),
    avg_trust_score DECIMAL(5,4),
    high_trust_count INTEGER DEFAULT 0,
    low_trust_count INTEGER DEFAULT 0,
    verified_count INTEGER DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE(product_id, date)
);

CREATE INDEX IF NOT EXISTS idx_analytics_product_date ON review_analytics(product_id, date DESC);

-- ============================================================================
-- SYSTEM LOGS TABLE (Track system events)
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type VARCHAR(50),
    event_data TEXT,
    user_id VARCHAR(50),
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_logs_type ON system_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_logs_created ON system_logs(created_at DESC);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Product Summary with Review Stats
CREATE VIEW IF NOT EXISTS vw_product_summary AS
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    p.price,
    p.score_trust_weighted,
    p.avg_rating,
    COUNT(r.review_id) as actual_review_count,
    AVG(r.trust_score) as calculated_trust_score,
    SUM(CASE WHEN r.verified = 1 THEN 1 ELSE 0 END) as verified_reviews,
    SUM(CASE WHEN r.trust_score >= 0.7 THEN 1 ELSE 0 END) as high_trust_reviews,
    SUM(CASE WHEN r.trust_score < 0.3 THEN 1 ELSE 0 END) as low_trust_reviews
FROM products p
LEFT JOIN reviews r ON p.product_id = r.product_id
GROUP BY p.product_id;

-- View: Top Products by Trust Score
CREATE VIEW IF NOT EXISTS vw_top_products AS
SELECT 
    product_id,
    product_name,
    category,
    brand,
    score_trust_weighted,
    avg_rating,
    review_count
FROM products
WHERE review_count >= 5
ORDER BY score_trust_weighted DESC
LIMIT 100;

-- View: Recent Reviews
CREATE VIEW IF NOT EXISTS vw_recent_reviews AS
SELECT 
    r.review_id,
    r.product_id,
    p.product_name,
    r.user_id,
    r.rating,
    r.trust_score,
    r.verified,
    r.review_text,
    r.created_at
FROM reviews r
JOIN products p ON r.product_id = p.product_id
ORDER BY r.created_at DESC
LIMIT 1000;

-- ============================================================================
-- TRIGGERS (For automatic updates)
-- ============================================================================

-- Trigger: Update product stats when review is added
-- Note: SQLite syntax - adjust for PostgreSQL
CREATE TRIGGER IF NOT EXISTS trg_update_product_stats_insert
AFTER INSERT ON reviews
BEGIN
    UPDATE products
    SET 
        review_count = (SELECT COUNT(*) FROM reviews WHERE product_id = NEW.product_id),
        avg_rating = (SELECT AVG(rating) FROM reviews WHERE product_id = NEW.product_id),
        score_trust_weighted = (
            SELECT AVG(rating * trust_score) / AVG(trust_score)
            FROM reviews 
            WHERE product_id = NEW.product_id
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE product_id = NEW.product_id;
END;

-- Trigger: Update product stats when review is deleted
CREATE TRIGGER IF NOT EXISTS trg_update_product_stats_delete
AFTER DELETE ON reviews
BEGIN
    UPDATE products
    SET 
        review_count = (SELECT COUNT(*) FROM reviews WHERE product_id = OLD.product_id),
        avg_rating = (SELECT COALESCE(AVG(rating), 0) FROM reviews WHERE product_id = OLD.product_id),
        score_trust_weighted = (
            SELECT COALESCE(AVG(rating * trust_score) / NULLIF(AVG(trust_score), 0), 0)
            FROM reviews 
            WHERE product_id = OLD.product_id
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE product_id = OLD.product_id;
END;
