from fastapi import HTTPException, Response, status
from ..config.firebase import firebase
from ..config.cache import CacheHandler
from ..config.logger import logger
from .Users import UserHandler
from typing import TypeVar, Generic, Type, Any
from pydantic import BaseModel, Field
from enum import Enum
from abc import ABC
from typing import Optional, List, Dict
import time , random ,string

T = TypeVar('T', bound=BaseModel)

class PropertyResourceType(Enum):
    CACHE = 'property_index_cache'
    COLLECTION = 'property_resource_index'
    ROOM = 'property_room_index'
    LEASES = 'property_lease_index'

    @classmethod
    def get_resource_type(cls, prefix: str) -> Optional[str]:
        prefix_mapping = {
            'ROOM': cls.ROOM.value,
            'LEAS': cls.LEASES.value
        }
        return prefix_mapping.get(prefix)

class Access(BaseModel):
    type: str = Field(..., pattern="^(internal|external)$")  # 限制只能是 internal 或 external
    companies: List[str]
    allowClients: Optional[str]


class BaseHandler(Generic[T],ABC):
    def __init__(self, uid: str):
        """
        初始化處理器模型
        
        Args:
            uid: 識別使用者
        """
        self.cache = CacheHandler()
        self.db = firebase.db
        self.logging = logger
        self.collection_name: str = ""
        self.cache_category: str = ""
        self.id_prefix: str = ""
        self.model_class: Type[T] = None
        self.User = UserHandler(uid)
        self.uid = uid
    async def delete_item(self, item_id: str) -> Response:
        '''
        刪除單一物件

        Args:
            item_id:要刪除的物件id 
        '''
        try:
            doc_ref = self.db.collection(self.collection_name).document(item_id)
            item = doc_ref.get().to_dict()
            if item is None:
                raise HTTPException(status_code=404, detail=f"{str(item_id)} is not exist")
            deleted_item = self.model_class(**item)
            if not self._has_access(deleted_item.access.companies):
                self.logging.info(f"{str(self.uid)}has no access to item :{str(item_id)}")
                raise HTTPException(status_code=403,detail=f"{str(self.uid)}has no access to item :{str(item_id)}")
            
            if self.cache.get(self.cache_category,item_id) is not None:
                self.cache.delete(self.cache_category,item_id)
            self.db.collection(self.collection_name).document(item_id).delete()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            self.logging.error(f"{str(self.id_prefix)}_Handler.delete_item error: {str(e)}")
            raise HTTPException(status_code=500,detail=f"{str(self.id_prefix)}_Handler.delete_item error: {str(e)}")
        
    async def post_item(self, item: T) -> T:
        '''
        創建單一物件
        Args:
            item: 類別
        '''
        return await self._save_item(item,"post")

    async def put_item(self, item:T) -> T:
        '''
        更新單一物件
        Args:
            info: 更新資料內容
        '''
        return await self._save_item(item,"put")

    async def get_item(self, item_id: str, default = True) -> Optional[T]:
        '''
        取得單一物件，同時檢查是否有權限取得若無返回None
        Args:
            item_id: 物件id
        '''
        try:
            
            cache_data = self.cache.get(self.cache_category,item_id)
            if cache_data:
                item = cache_data
                
            else:
                doc_ref = self.db.collection(self.collection_name).document(item_id)
                doc = doc_ref.get()
                if doc: 
                    item = self.model_class(**doc.to_dict())
                else:
                    return None
                
                self.cache.set(self.cache_category,item.id,item)

            if await self._has_access(item.access.companies):
                return item
            elif default is True:
                self.logging.info(f"{str(self.uid)}has no access to item :{str(item_id)}")
                raise HTTPException(status_code=403,detail=f"{str(self.uid)}has no access to item :{str(item_id)}")
            else:
                return None

        except Exception as e:
            self.logging.error(f"{str(self.id_prefix)}_Handler.get_item error: {str(e)}")
            raise HTTPException(status_code=500,detail=f"{str(self.id_prefix)}_Handler.get_item error: {str(e)}")
        
    async def get_items(self, id_list) -> Dict[str, T]:
        '''
        get list of items base on the input list which contain id

        Args:
            id_list : [str]
        Return:
            List[T]
        '''
        try:
            resources = {}
            
            for id in id_list:
                resource = await self.get_item(id, False)
                if resource is not None:
                    if self.id_prefix == "LEAS" and not resource.status:
                        continue
                    resources[resource.id] = resource
            return resources

        except Exception as e:
            self.logging.error(f"{str(self.id_prefix)}_Handler.get_items error: {str(e)}")
            raise HTTPException(status_code=500,detail=f"{str(self.id_prefix)}_Handler.get_items error: {str(e)}")

        

    async def get_item_list(self) -> List[Any]:
        '''
        返回handler處理類別的List
        '''
        try:
            ##只獲取文檔的參考資訊（ID和路徑），不包含文檔內容
            result = []
            docs = self.db.collection(self.cache_category).list_documents()
            for doc in docs:
                doc_ref = self.db.collection(self.cache_category).document(doc.id)
                item = self.model_class(**doc_ref.get().to_dict())
                self.cache.set(self.cache_category,item.id,item)
                if item is not None and self._has_access(item.access.companies):
                    result.append(item)
            return result
        except Exception as e:
            self.logging.error(f"{str(self.id_prefix)}_Handler.get_item_list error: {str(e)}")
            raise HTTPException(status_code=500,detail=f"{str(self.id_prefix)}_Handler.get_item_list error: {str(e)}")
        
        
    async def get_cache_status(self) -> dict:
        try:
            return self.cache.get_cache_stats_category(self.cache_category)
        except Exception as e:
            self.logging.error(f"{str(self.id_prefix)}_Handler.get_cache_status error: {str(e)}")
            raise HTTPException(status_code=500,detail=f"{str(self.id_prefix)}_Handler.get_cache_status error: {str(e)}")
            

    async def _has_access(self, access_list) -> bool:
        return await self.User.get_access() in access_list
    
    async def _save_item(self, item:T,method : str) -> Dict:
        '''
        新增，更新單一物件共用邏輯
        Args:
            item: 完整的item類型
        '''
        
        try:
            if method == "post" or (method == "put" and self._has_access(item.access.companies)):
                data = item.model_dump()
                self.db.collection(self.collection_name).document(item.id).set(data)
                self.cache.set(self.cache_category,item.id,item)

                return item
            else:
                self.logging.info(f"{str(self.uid)}has no access to item :{str(item.id)}")
                raise HTTPException(status_code=403,detail=f"{str(self.uid)}has no access to item :{str(item.id)}")
        except Exception as e:
            self.logging.error(f"{str(self.id_prefix)}_Handler._save_item error: {str(e)}")
            raise HTTPException(status_code=500,detail=f"{str(self.id_prefix)}_Handler._save_item error: {str(e)}")
    
    def id_generate(self) -> str:
        '''
        Generate randomize id based on handler's prefix

        Returns:
            randomize id with prefix
        '''
        timestamp = int(time.time() * 1000)
        random_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
        return f"{self.id_prefix}_{timestamp}_{random_str}"
    

class PropertyRelatedHandler(BaseHandler):
    """Handling property related operation"""
    
    async def find_by_property_id(self, property_id: str) -> Dict[str, T]:
        try:
            cache_data = self.cache.get(PropertyResourceType.CACHE.value, PropertyResourceType.get_resource_type(self.id_prefix))
            if cache_data is None :
                doc_ref = self.db.collection(PropertyResourceType.COLLECTION.value).document(PropertyResourceType.get_resource_type(self.id_prefix))
                resource = doc_ref.get().to_dict()
                self.cache.set(PropertyResourceType.CACHE.value, PropertyResourceType.get_resource_type(self.id_prefix), resource)
            else:
                resource = cache_data
                
            ids = resource[property_id]
            return await self.get_items(ids)
        
        except Exception as e:
            self.logging.error(f"{str(self.id_prefix)}_Handler.find_by_property_id error: {str(e)}")
            raise HTTPException(status_code=500,detail=f"{str(self.id_prefix)}_Handler.find_by_property_id: {str(e)}")
        
