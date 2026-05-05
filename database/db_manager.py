"""
Database Manager for Trust-Based Product Recommendation System
Supports both SQLite (local) and PostgreSQL (production)
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any
import os

class DatabaseManager:
    """Manage database operations for the recommendation system"""
    
    def __init__(self, db_type='sqlite', db_path='database/reviews.db', **kwargs):
        """
        Initialize database connection
        
        Args:
            db_type: 'sqlite' or 'postgresql'
            db_path: Path to SQLite database file
            **kwargs: PostgreSQL connection parameters (host, port, database, user, password)
        """
        self.db_type = db_type
        self.db_path = db_path
        self.conn = None
        
        if db_type == 'sqlite':
            self._connect_sqlite()
        elif db_type == 'postgresql':
            self._connect_postgresql(**kwargs)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _connect_sqlite(self):
        """Connect to SQLite database"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        print(f"Connected to SQLite database: {self.db_path}")
    
    def _connect_postgresql(self, host, port, database, user, password):
        """Connect to PostgreSQL database"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            self.conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            self.cursor_factory = RealDictCursor
            print(f"Connected to PostgreSQL database: {database}")
        except ImportError:
            raise ImportError("psycopg2 not installed. Run: pip install psycopg2-binary")
    
    def initialize_schema(self, schema_file='database/schema.sql'):
        """Initialize database schema from SQL file"""
        try:
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Execute schema
            cursor = self.conn.cursor()
            
            if self.db_type == 'sqlite':
                # SQLite: use executescript which handles multiple statements
                cursor.executescript(schema_sql)
            else:
                # PostgreSQL: can execute all at once
                cursor.execute(schema_sql)
            
            self.conn.commit()
            print("Database schema initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing schema: {e}")
            self.conn.rollback()
            return False
    
    # ========================================================================
    # PRODUCT OPERATIONS
    # ========================================================================
    
    def insert_product(self, product_data: Dict[str, Any]) -> bool:
        """Insert a new product"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO products (
                    product_id, product_name, category, brand, price,
                    image_url, description, avg_rating, rating_std,
                    review_count, score_raw_avg, score_count_weighted,
                    score_trust_weighted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data.get('product_id'),
                product_data.get('product_name'),
                product_data.get('category'),
                product_data.get('brand'),
                product_data.get('price'),
                product_data.get('image_url'),
                product_data.get('description'),
                product_data.get('avg_rating'),
                product_data.get('rating_std'),
                product_data.get('review_count', 0),
                product_data.get('score_raw_avg'),
                product_data.get('score_count_weighted'),
                product_data.get('score_trust_weighted')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting product: {e}")
            self.conn.rollback()
            return False
    
    def get_product(self, product_id: str) -> Optional[Dict]:
        """Get product by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def search_products(self, query: str, limit: int = 20) -> List[Dict]:
        """Search products by name, category, or brand"""
        cursor = self.conn.cursor()
        search_pattern = f"%{query}%"
        cursor.execute("""
            SELECT * FROM products
            WHERE product_name LIKE ? 
               OR category LIKE ?
               OR brand LIKE ?
               OR product_id LIKE ?
            ORDER BY score_trust_weighted DESC
            LIMIT ?
        """, (search_pattern, search_pattern, search_pattern, search_pattern, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_top_products(self, limit: int = 100, min_reviews: int = 5) -> List[Dict]:
        """Get top products by trust score"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM products
            WHERE review_count >= ?
            ORDER BY score_trust_weighted DESC
            LIMIT ?
        """, (min_reviews, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_products_by_category(self, category: str, limit: int = 50) -> List[Dict]:
        """Get products by category"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM products
            WHERE category = ?
            ORDER BY score_trust_weighted DESC
            LIMIT ?
        """, (category, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ========================================================================
    # REVIEW OPERATIONS
    # ========================================================================
    
    def insert_review(self, review_data: Dict[str, Any]) -> Optional[int]:
        """Insert a new review and return review_id"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO reviews (
                    user_id, product_id, rating, review_text,
                    verified, helpful_votes, trust_score, predicted_trust_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                review_data.get('user_id'),
                review_data.get('product_id'),
                review_data.get('rating'),
                review_data.get('review_text'),
                review_data.get('verified', False),
                review_data.get('helpful_votes', 0),
                review_data.get('trust_score'),
                review_data.get('predicted_trust_score')
            ))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error inserting review: {e}")
            self.conn.rollback()
            return None
    
    def get_product_reviews(self, product_id: str, 
                           min_trust: float = 0.0,
                           limit: int = 1000) -> List[Dict]:
        """Get reviews for a product"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM reviews
            WHERE product_id = ? AND trust_score >= ?
            ORDER BY trust_score DESC, created_at DESC
            LIMIT ?
        """, (product_id, min_trust, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_reviews(self, limit: int = 100) -> List[Dict]:
        """Get recent reviews"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT r.*, p.product_name
            FROM reviews r
            JOIN products p ON r.product_id = p.product_id
            ORDER BY r.created_at DESC
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_review_trust_score(self, review_id: int, trust_score: float) -> bool:
        """Update trust score for a review"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE reviews
                SET trust_score = ?, updated_at = CURRENT_TIMESTAMP
                WHERE review_id = ?
            """, (trust_score, review_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating review: {e}")
            self.conn.rollback()
            return False
    
    def delete_review(self, review_id: int) -> bool:
        """Delete a review"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM reviews WHERE review_id = ?", (review_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting review: {e}")
            self.conn.rollback()
            return False
    
    # ========================================================================
    # ANALYTICS OPERATIONS
    # ========================================================================
    
    def get_product_statistics(self, product_id: str) -> Dict:
        """Get comprehensive statistics for a product"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_reviews,
                AVG(rating) as avg_rating,
                AVG(trust_score) as avg_trust_score,
                SUM(CASE WHEN verified = 1 THEN 1 ELSE 0 END) as verified_count,
                SUM(CASE WHEN trust_score >= 0.7 THEN 1 ELSE 0 END) as high_trust_count,
                SUM(CASE WHEN trust_score < 0.3 THEN 1 ELSE 0 END) as low_trust_count,
                MIN(trust_score) as min_trust,
                MAX(trust_score) as max_trust
            FROM reviews
            WHERE product_id = ?
        """, (product_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    def get_system_statistics(self) -> Dict:
        """Get overall system statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Product stats
        cursor.execute("SELECT COUNT(*) as count FROM products")
        stats['total_products'] = cursor.fetchone()[0]
        
        # Review stats
        cursor.execute("SELECT COUNT(*) as count FROM reviews")
        stats['total_reviews'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(trust_score) as avg FROM reviews")
        stats['avg_trust_score'] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) as count FROM reviews WHERE verified = 1")
        stats['verified_reviews'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as count FROM reviews WHERE trust_score >= 0.7")
        stats['high_trust_reviews'] = cursor.fetchone()[0]
        
        return stats
    
    # ========================================================================
    # BULK OPERATIONS
    # ========================================================================
    
    def bulk_insert_products(self, products_df: pd.DataFrame) -> int:
        """Bulk insert products from DataFrame"""
        try:
            products_df.to_sql('products', self.conn, if_exists='append', index=False)
            self.conn.commit()
            return len(products_df)
        except Exception as e:
            print(f"Error bulk inserting products: {e}")
            self.conn.rollback()
            return 0
    
    def bulk_insert_reviews(self, reviews_df: pd.DataFrame) -> int:
        """Bulk insert reviews from DataFrame"""
        try:
            # Remove review_id if exists (auto-increment)
            if 'review_id' in reviews_df.columns:
                reviews_df = reviews_df.drop('review_id', axis=1)
            
            reviews_df.to_sql('reviews', self.conn, if_exists='append', index=False)
            self.conn.commit()
            return len(reviews_df)
        except Exception as e:
            print(f"Error bulk inserting reviews: {e}")
            self.conn.rollback()
            return 0
    
    # ========================================================================
    # EXPORT OPERATIONS
    # ========================================================================
    
    def export_to_dataframe(self, table_name: str) -> pd.DataFrame:
        """Export table to pandas DataFrame"""
        return pd.read_sql_query(f"SELECT * FROM {table_name}", self.conn)
    
    def export_product_reviews_to_df(self, product_id: str) -> pd.DataFrame:
        """Export product reviews to DataFrame"""
        query = "SELECT * FROM reviews WHERE product_id = ?"
        return pd.read_sql_query(query, self.conn, params=(product_id,))
    
    # ========================================================================
    # UTILITY OPERATIONS
    # ========================================================================
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute custom SQL query"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
