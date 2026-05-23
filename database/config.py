"""
Database Configuration
Centralized configuration for database connections and caching
"""

import os
from typing import Dict, Any

class DatabaseConfig:
    """Database configuration manager"""
    
    # SQLite Configuration
    SQLITE_PATH = os.getenv('SQLITE_PATH', 'database/reviews.db')
    
    # PostgreSQL Configuration
    POSTGRES_CONFIG = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', '5432')),
        'database': os.getenv('POSTGRES_DB', 'trust_reviews'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
    }
    
    # Connection Pool Configuration
    POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '20'))
    MAX_RETRIES = int(os.getenv('DB_MAX_RETRIES', '3'))
    RETRY_DELAY = float(os.getenv('DB_RETRY_DELAY', '1.0'))
    
    # Redis Cache Configuration
    REDIS_CONFIG = {
        'enabled': os.getenv('REDIS_ENABLED', 'true').lower() == 'true',
        'host': os.getenv('REDIS_HOST', 'localhost'),
        'port': int(os.getenv('REDIS_PORT', '6379')),
        'password': os.getenv('REDIS_PASSWORD', None) or None,
        'db': int(os.getenv('REDIS_DB', '0'))
    }
    
    @classmethod
    def get_sqlite_config(cls) -> Dict[str, Any]:
        """Get SQLite configuration"""
        return {
            'db_type': 'sqlite',
            'db_path': cls.SQLITE_PATH
        }
    
    @classmethod
    def get_postgresql_config(cls) -> Dict[str, Any]:
        """Get PostgreSQL configuration"""
        return {
            'db_type': 'postgresql',
            'pool_size': cls.POOL_SIZE,
            'max_retries': cls.MAX_RETRIES,
            'retry_delay': cls.RETRY_DELAY,
            **cls.POSTGRES_CONFIG
        }
    
    @classmethod
    def get_redis_config(cls) -> Dict[str, Any]:
        """Get Redis configuration"""
        return cls.REDIS_CONFIG
    
    @classmethod
    def get_config(cls, db_type: str = 'sqlite') -> Dict[str, Any]:
        """Get configuration for specified database type"""
        if db_type == 'sqlite':
            return cls.get_sqlite_config()
        elif db_type == 'postgresql':
            return cls.get_postgresql_config()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    @classmethod
    def from_env(cls) -> Dict[str, Any]:
        """Get configuration from environment variable DB_TYPE"""
        db_type = os.getenv('DB_TYPE', 'sqlite')
        return cls.get_config(db_type)


# Example usage:
if __name__ == "__main__":
    print("SQLite Configuration:")
    print(DatabaseConfig.get_sqlite_config())
    print("\nPostgreSQL Configuration:")
    print(DatabaseConfig.get_postgresql_config())
    print("\nRedis Configuration:")
    print(DatabaseConfig.get_redis_config())
