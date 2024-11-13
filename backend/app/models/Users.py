from fastapi import HTTPException
from ..config.firebase import firebase
from ..config.exception import DatabaseError , CacheError
from ..config.cache import CacheHandler

class UserHandler:

    def __init__(self,uid):
        
        self.uid = uid
        self.cache_catagory = "users"
        self.cache = CacheHandler()
        self.db = firebase.db
        


    async def _get_user_from_db(self):
        """快取用戶數據"""
        try:
            doc_ref = self.db.collection('user').document(self.uid)
            user_data = doc_ref.get()
            if user_data:
                self.cache.set('users',self.uid,user_data.to_dict())
                return user_data.to_dict()
            else:
                raise DatabaseError(f"無法取得使用者:{self.uid}資料")
        except Exception as e:
            
            raise CacheError("快取失敗")

    async def get_access(self):
        try:
            if self.cache.get(self.cache_catagory,self.uid):
                value = self.cache.get(self.cache_catagory,self.uid)
            else:
                value = await self._get_user_from_db()
            return value['company']
        except Exception as e:
            
            raise HTTPException(status_code=403,detail=str(e))


