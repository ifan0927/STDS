# exceptions.py
class DatabaseError(Exception):
    """資料庫相關錯誤"""
    pass

class CacheError(Exception):
    """快取相關錯誤"""
    pass

class AuthorizationError(Exception):
    """授權相關錯誤"""
    pass

class ValueError(Exception):
    pass
