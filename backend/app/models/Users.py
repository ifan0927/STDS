from fastapi import HTTPException
from ..config.firebase import get_firestore
from ..config.exception import DatabaseError , CacheError
from ..config.cache import CacheHandler
from ..config.logger import get_logger

class UserHandler:
    
    def __init__(self,uid):
        self.uid = uid
        self.cache = CacheHandler()
    
    async def _get_user_from_db(self):
        """從資料庫獲取用戶數據"""
        try:
            doc_ref = self.db.collection('user').document(self.uid)
            doc = doc_ref.get()
            return doc.to_dict()
        except Exception as e:
            self.logging.error(f"資料庫查詢失敗: {str(e)}")
            raise DatabaseError("無法訪問資料庫")

    async def _cache_user_data(self, user_data):
        """快取用戶數據"""
        try:
            self.cache.set(self.uid, user_data)
        except Exception as e:
            self.logging.error(f"快取存取失敗: {str(e)}")
            raise CacheError("快取失敗")

    async def init_user(self):
        """初始化用戶數據"""
        try:
            self.db = await get_firestore()
            self.logging = await get_logger()
            
            user_data = await self._get_user_from_db()
            await self._cache_user_data(user_data)
            
            return user_data
            
        except (DatabaseError, CacheError) as e:
            # 這裡可以選擇直接拋出異常，或進行特定的錯誤處理
            raise HTTPException(status_code=500, detail=str(e))

    async def get_access(self):
        try:
            if self.cache.get(self.uid):
                value = self.cache.get(self.uid)
            else:
                value = await self._get_user_from_db()
            return value['company']
        except Exception as e:
            self.logging.error(f"使用者{self.uid}取得權限資料失敗:{str(e)}")
            raise HTTPException(status_code=403,detail=str(e))


