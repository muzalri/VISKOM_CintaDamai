"""
Konfigurasi aplikasi untuk Flask + SQLAlchemy + MySQL
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""
    
    # Flask Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'viskom-cinta-damai-2024-secret-key'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Upload Config
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    RESULT_FOLDER = os.path.join(os.path.dirname(__file__), 'results')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}
    
    # SQLAlchemy Config
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True untuk debugging SQL queries
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    TESTING = False
    
    # MySQL Connection String
    # Format: mysql+pymysql://username:password@localhost:3306/database_name
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        'mysql+pymysql://root:@localhost:3306/pothole_detection'
    )


class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Untuk production, set DATABASE_URL via environment variable
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        'mysql+pymysql://root:password@localhost:3306/pothole_detection'
    )


class TestingConfig(Config):
    """Testing configuration"""
    
    DEBUG = True
    TESTING = True
    
    # SQLite untuk testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Pilih config berdasarkan FLASK_ENV
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
