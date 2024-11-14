from fastapi import HTTPException
from ..config.firebase import firebase
from ..config.cache import CacheHandler
from ..config.logger import logger
from .Users import UserHandler
from typing import TypeVar, Generic, Type, Any
from pydantic import BaseModel, Field
from abc import ABC
from typing import List, Optional

# 定義一個泛型類型 T，它必須是 BaseModel 的子類
T = TypeVar('T', bound=BaseModel)

class Access(BaseModel):
    type: str = Field(..., pattern="^(internal|external)$")  # 限制只能是 internal 或 external
    companies: List[str]
    allowClients: str

# 使用泛型的基礎類別
class BaseHandler(Generic[T],ABC):
    def __init__(self, uid: str):
        """
        初始化處理器模型
        
        Args:
            access_company: 權限識別資料
        """
        self.cache = CacheHandler()
        self.db = firebase.db
        self.logging = logger
        self.collection_name: str = ""
        self.cache_catagory: str = ""
        self.model_class: Type[T] = None
        self.User = UserHandler(uid)
        self.uid = uid
    

    async def get_item(self,item_id:str) -> Optional[T]:
        '''
        取得單一物件，同時檢查是否有權限取得若無返回None
        Args:
            item_id: 物件id
        '''
        try:
            cache_data = self.cache.get(self.cache_catagory,item_id)
            if cache_data:
                item = self.model_class(**cache_data)
            else:
                doc_ref = self.db.collection(self.collection_name).document(item_id)
                doc = doc_ref.get()
                if doc: 
                    item = self.model_class(**doc.to_dict())
                else:
                    return None
                
                self.cache.set(self.cache_catagory,item.id,item)

            if await self._has_access(item.access.companies):
                return item
            return None


        except Exception as e:
            raise HTTPException(status_code=500,detail=f"{str(e)}")
        

    async def get_item_list(self) -> List[Any]:
        '''
        返回handler處理類別的List
        '''
        try:
            ##只獲取文檔的參考資訊（ID和路徑），不包含文檔內容
            result = []
            docs = self.db.collection(self.cache_catagory).list_documents()
            for doc in docs:
                item = self.cache.get(self.cache_catagory,doc.id)
                if item:
                    result.append(item)
                else:
                    doc_ref = self.db.collection(self.cache_catagory).document(doc.id)
                    item = self.model_class(**doc_ref.get().to_dict())
                    self.cache.set(self.cache_catagory,item.id,item)
                if item is not None and self._has_access(item.access.companies):
                    result.append(item)
            return result
        except Exception as e:
            raise HTTPException(status_code=500,detail=f"PropertyHandler.get_item_list error: {str(e)}")
            

    async def _has_access(self, access_list):
        return await self.User.get_access() in access_list