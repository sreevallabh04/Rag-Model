"""
Configuration file for Intelligent RAG Assistant
Author: Sreevallabh kakarala
Version: 2.0
"""

import os
from typing import Dict, Any
from pathlib import Path

class Config:
    """Production configuration class for the RAG Assistant"""
    
    # Application Information
    APP_NAME = "Intelligent RAG Assistant"
    APP_VERSION = "2.0"
    AUTHOR = "Sreevallabh kakarala"
    AUTHOR_EMAIL = "srivallabhkakarala@gmail.com"
    
    # Model Configuration
    DEFAULT_MODEL = os.getenv('OLLAMA_MODEL', 'mistral:latest')
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost:11434')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    
    # Processing Settings
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '400'))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '100'))
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', '10'))
    
    # UI Configuration
    APP_TITLE = os.getenv('APP_TITLE', f"RAG Assistant by {AUTHOR}")
    THEME_COLOR = os.getenv('THEME_COLOR', '#667eea')
    PAGE_ICON = "🧠"
    
    # OCR Settings
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', 'tesseract')
    OCR_LANGUAGE = os.getenv('OCR_LANGUAGE', 'eng')
    
    # File Settings
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '100')) * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg']
    TEMP_DIR = Path(os.getenv('TEMP_DIR', 'temp'))
    
    # Performance Settings
    EMBEDDING_BATCH_SIZE = int(os.getenv('EMBEDDING_BATCH_SIZE', '32'))
    VECTOR_DIMENSIONS = int(os.getenv('VECTOR_DIMENSIONS', '384'))
    MAX_MEMORY_USAGE = int(os.getenv('MAX_MEMORY_USAGE', '8')) * 1024 * 1024 * 1024  # 8GB
    
    # Security Settings
    ENABLE_HTTPS = os.getenv('ENABLE_HTTPS', 'False').lower() == 'true'
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))  # 1 hour
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/rag_assistant.log')
    LOG_ROTATION = os.getenv('LOG_ROTATION', '10 MB')
    LOG_RETENTION = os.getenv('LOG_RETENTION', '7 days')
    
    # Health Check Settings
    HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))
    
    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Get model configuration"""
        return {
            'model_name': cls.DEFAULT_MODEL,
            'host': cls.OLLAMA_HOST,
            'embedding_model': cls.EMBEDDING_MODEL,
            'temperature_range': (0.1, 1.0),
            'default_temperature': 0.7
        }
    
    @classmethod
    def get_processing_config(cls) -> Dict[str, Any]:
        """Get document processing configuration"""
        return {
            'chunk_size': cls.CHUNK_SIZE,
            'chunk_overlap': cls.CHUNK_OVERLAP,
            'max_search_results': cls.MAX_SEARCH_RESULTS,
            'batch_size': cls.EMBEDDING_BATCH_SIZE,
            'vector_dimensions': cls.VECTOR_DIMENSIONS
        }
    
    @classmethod
    def get_ui_config(cls) -> Dict[str, Any]:
        """Get UI configuration"""
        return {
            'title': cls.APP_TITLE,
            'icon': cls.PAGE_ICON,
            'theme_color': cls.THEME_COLOR,
            'author': cls.AUTHOR,
            'version': cls.APP_VERSION
        }
    
    @classmethod
    def get_security_config(cls) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            'max_file_size': cls.MAX_FILE_SIZE,
            'allowed_extensions': cls.ALLOWED_EXTENSIONS,
            'session_timeout': cls.SESSION_TIMEOUT,
            'enable_https': cls.ENABLE_HTTPS
        }

# Production deployment configurations
class ProductionConfig(Config):
    """Production-specific configuration"""
    LOG_LEVEL = 'WARNING'
    DEBUG = False
    DEVELOPMENT = False

class DevelopmentConfig(Config):
    """Development-specific configuration"""
    LOG_LEVEL = 'DEBUG'
    DEBUG = True
    DEVELOPMENT = True

class TestingConfig(Config):
    """Testing-specific configuration"""
    LOG_LEVEL = 'DEBUG'
    TESTING = True
    CHUNK_SIZE = 100  # Smaller for faster testing

# Configuration factory
def get_config(env: str = None) -> Config:
    """Get configuration based on environment"""
    env = env or os.getenv('ENVIRONMENT', 'production')
    
    configs = {
        'production': ProductionConfig,
        'development': DevelopmentConfig,
        'testing': TestingConfig
    }
    
    return configs.get(env, ProductionConfig)() 