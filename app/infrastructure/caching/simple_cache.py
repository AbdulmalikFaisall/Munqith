"""
Simple in-memory caching service for Sprint 10.

Implements lightweight caching for read-heavy endpoints.
Uses in-memory dictionary with TTL (time-to-live) mechanism.
No Redis required - suitable for single-instance deployments.
"""
import time
from typing import Any, Optional, Callable
from functools import wraps


class CacheEntry:
    """Single cache entry with TTL."""
    
    def __init__(self, value: Any, ttl: int):
        """
        Initialize cache entry.
        
        Args:
            value: Cached value
            ttl: Time-to-live in seconds
        """
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return time.time() - self.created_at > self.ttl


class SimpleCache:
    """
    Simple in-memory cache with TTL and key expiration.
    
    Thread-safe for read-heavy workloads.
    Suitable for caching read endpoints.
    
    Usage:
        cache = SimpleCache()
        cache.set("key", "value", ttl=60)
        value = cache.get("key")
        cache.delete("key")
        cache.clear()
    """
    
    def __init__(self):
        """Initialize cache store."""
        self._store = {}
    
    def set(self, key: str, value: Any, ttl: int = 60) -> None:
        """
        Set cache value with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default: 60)
        """
        self._store[key] = CacheEntry(value, ttl)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value if exists and not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        entry = self._store.get(key)
        
        if entry is None:
            return None
        
        if entry.is_expired():
            del self._store[key]
            return None
        
        return entry.value
    
    def delete(self, key: str) -> None:
        """
        Delete cache entry.
        
        Args:
            key: Cache key to delete
        """
        if key in self._store:
            del self._store[key]
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._store.clear()
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries and return count removed.
        
        Returns:
            Number of entries removed
        """
        expired_keys = [k for k, v in self._store.items() if v.is_expired()]
        for key in expired_keys:
            del self._store[key]
        return len(expired_keys)


# Global cache instance
_cache = SimpleCache()


def cached(ttl: int = 60, key_prefix: str = ""):
    """
    Decorator for caching function results.
    
    Usage:
        @cached(ttl=60, key_prefix="timeline")
        def get_timeline(company_id):
            ...
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Cache key prefix for namespacing
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key from function name, args, and kwargs
            cache_key = f"{key_prefix}:{func.__name__}"
            
            # Include first arg if it exists (usually ID)
            if args:
                cache_key += f":{args[0]}"
            
            # Check cache first
            cached_value = _cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Cache miss - call function
            result = func(*args, **kwargs)
            
            # Store in cache
            _cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


def clear_cache(pattern: str = "") -> None:
    """
    Clear cache entries matching pattern.
    
    Args:
        pattern: Key pattern to match (empty = clear all)
    """
    if not pattern:
        _cache.clear()
    else:
        keys_to_delete = [k for k in _cache._store.keys() if pattern in k]
        for key in keys_to_delete:
            _cache.delete(key)


def get_cache_instance() -> SimpleCache:
    """Get global cache instance."""
    return _cache
