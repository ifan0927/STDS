from typing import Any, Optional
from datetime import datetime, timedelta
import threading

class Cache:
    def __init__(self):
        self._cache = {}
        self._default_ttl = 3600

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            item = self._cache[key]
            if item['expires_at'] > datetime.now():
                return item['value']
            else:
                del self._cache[key]
        return None
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expires_at = datetime.now() + timedelta(seconds=ttl or self._default_ttl)
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at
        }

    def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()

    # 添加一些有用的管理方法
    def get_cache_stats(self) -> dict:
        total_items = len(self._cache)
        expired_items = sum(
            1 for item in self._cache.values() 
            if item['expires_at'] <= datetime.now()
        )
        return {
            'total_items': total_items,
            'active_items': total_items - expired_items,
            'expired_items': expired_items
        }

    def cleanup_expired(self) -> int:
        """清理過期項目並返回清理的數量"""
        now = datetime.now()
        expired_keys = [
            key for key, item in self._cache.items()
            if item['expires_at'] <= now
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)

class CacheHandler:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                # 初始化實例屬性
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        # 確保初始化只執行一次
        if not self._initialized:
            self._catagory = {}
            self._lock = threading.Lock()
            self._default_ttl = 3600  # 預設過期時間（秒）
            self._initialized = True

    def get(self, catagory:str,key: str) -> Optional[Any]:
        with self._lock:
            if catagory in self._catagory:
                cache = self._catagory[catagory]
                return cache.get(key)
                
            return None
        
    def set(self, catagory: str, key: str, value: Any) -> None:
        with self._lock:
            if catagory not in self._catagory:
                self._catagory[catagory] = Cache()
            self._catagory[catagory].set(key, value)


    def delete(self, catagory: str ,key: str) -> None:
        with self._lock:
            self._catagory[catagory].delete(key)

    def clear(self, catagory: str) -> None:
        with self._lock:
            self._catagory[catagory].clear()


    # 添加一些有用的管理方法
    def get_cache_stats_catagory(self, catagory: str) -> Optional[dict]:
        with self._lock:
            if catagory in self._catagory:
                return self._catagory[catagory].get_cache_stats()
            return None

    def cleanup_expired(self) -> dict:  # 改變返回型別
        """清理過期項目並返回每個category的清理數量"""
        cleanup_results = {}
        with self._lock:
            for category, cache in self._catagory.items():
                cleanup_results[category] = cache.cleanup_expired()
        return cleanup_results