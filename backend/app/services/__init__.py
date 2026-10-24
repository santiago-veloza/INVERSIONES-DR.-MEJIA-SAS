
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from backend.app import db
from flask import current_app
import logging

# Configurar logging
logger = logging.getLogger(__name__)

class BaseService(ABC):
    """Clase base para todos los servicios"""
    
    def __init__(self):
        pass
    
    def commit_changes(self) -> bool:
        """Commit changes to database with error handling"""
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error committing database changes: {e}")
            return False
    
    def safe_get_or_404(self, model_class, id_value, error_message: str = None):
        """Safely get object or return None instead of 404"""
        try:
            return model_class.query.get(id_value)
        except Exception as e:
            logger.error(f"Error getting {model_class.__name__} with id {id_value}: {e}")
            return None


class ValidationMixin:
    """Mixin para validaciones comunes"""
    
    def validate_required_fields(self, data: Dict, required_fields: List[str]) -> tuple:
        """Validate that all required fields are present and not empty"""
        missing_fields = []
        for field in required_fields:
            if field not in data or not data[field] or str(data[field]).strip() == '':
                missing_fields.append(field)
        
        is_valid = len(missing_fields) == 0
        error_message = f"Campos requeridos faltantes: {', '.join(missing_fields)}" if missing_fields else None
        
        return is_valid, error_message
    
    def sanitize_string(self, value: str, max_length: int = None) -> str:
        """Sanitize string input"""
        if not value:
            return ""
        
        # Basic sanitization
        sanitized = str(value).strip()
        
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized


class CacheService:
    """Simple caching service for performance optimization"""
    
    _cache = {}
    _cache_ttl = {}
    
    @classmethod
    def get(cls, key: str):
        """Get value from cache"""
        import time
        
        if key not in cls._cache:
            return None
        
        # Check TTL
        if key in cls._cache_ttl and time.time() > cls._cache_ttl[key]:
            cls.delete(key)
            return None
        
        return cls._cache[key]
    
    @classmethod
    def set(cls, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL (default 5 minutes)"""
        import time
        
        cls._cache[key] = value
        cls._cache_ttl[key] = time.time() + ttl
    
    @classmethod
    def delete(cls, key: str):
        """Delete value from cache"""
        cls._cache.pop(key, None)
        cls._cache_ttl.pop(key, None)
    
    @classmethod
    def clear(cls):
        """Clear all cache"""
        cls._cache.clear()
        cls._cache_ttl.clear()