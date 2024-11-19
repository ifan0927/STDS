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
import asyncio

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

    def has_access(self, user_access_level: str, company_access_list: List[str]) -> bool:
        return user_access_level in company_access_list


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
            doc = doc_ref.get()
            if not doc.exists:
                raise HTTPException(status_code=404, detail=f"{str(item_id)} is not exist")
            item = doc.to_dict()
            deleted_item = self.model_class(**item)
            if hasattr(deleted_item, 'access'):
                if not deleted_item.access.has_access(await self.User.get_access(), deleted_item.access.companies):
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

    async def get_item(self, item_id: str) -> Optional[T]:
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
                if doc.exists: 
                    

                    item = self.model_class(**doc.to_dict())
                else:
                    print(f'找不到 ID 為 {item_id} 的文件')
                    return None
                
                self.cache.set(self.cache_category,item.id,item)

            if hasattr(item, 'access'):
                if item.access.has_access(await self.User.get_access(), item.access.companies):
                    return item
                else:
                    return None
            return item

        except Exception as e:
            self.logging.error(f"{str(self.id_prefix)}_Handler.get_item error: {str(e)}")
            raise HTTPException(status_code=500,detail=f"{str(self.id_prefix)}_Handler.get_item error: {str(e)}")
        
    async def get_items(self, id_list) -> Dict[str, T]:
        try:
            resources = {}
            uncached_ids = []
            
            # 檢查快取
            for item_id in id_list:
                cache_data = self.cache.get(self.cache_category, item_id)
                if cache_data:
                    if hasattr(cache_data, 'access'):
                        if cache_data.access.has_access(await self.User.get_access(), cache_data.access.companies):
                            resources[cache_data.id] = cache_data
                    continue
                else:
                    uncached_ids.append(item_id)

            # 批次處理未快取的文檔
            if uncached_ids:
                # 將 ID 列表分成每組 30 個
                batch_size = 30
                tasks = []
                
                for i in range(0, len(uncached_ids), batch_size):
                    batch_ids = uncached_ids[i:i + batch_size]
                    tasks.append(self._fetch_batch(batch_ids))
                
                # 併發執行所有批次
                batch_results = await asyncio.gather(*tasks)
                
                # 合併結果
                for batch_result in batch_results:
                    resources.update(batch_result)
                        
            return resources

        except Exception as e:
            self.logging.error(f"{str(self.id_prefix)}_Handler.get_items error: {str(e)}")
            raise HTTPException(status_code=500,
                detail=f"{str(self.id_prefix)}_Handler.get_items error: {str(e)}")

        

    async def get_item_list(self) -> Dict[str, T]:
        '''
        返回handler處理類別的List
        '''
        try:
            ##只獲取文檔的參考資訊（ID和路徑），不包含文檔內容
            tasks = []
            uncached_ids = []
            resources = {}
            docs = self.db.collection(self.collection_name).list_documents()   
            for doc in docs:
                
                cache_data = self.cache.get(self.cache_category, doc.id)
                if cache_data is not None:
                    if hasattr(cache_data, 'access'):
                        if cache_data.access.has_access(await self.User.get_access(), cache_data.access.companies):
                            resources[cache_data.id] = cache_data
                    continue
                else:
                    uncached_ids.append(doc.id)

            if uncached_ids:
                batch_size = 30
                for i in range(0, len(uncached_ids),batch_size):
                    batch_ids = uncached_ids[i:i + batch_size]
                    tasks.append(self._fetch_batch(batch_ids))
            if tasks:
                batch_results = await asyncio.gather(*tasks)
                for batch_result in batch_results:
                    resources.update(batch_result)

            return resources
        except Exception as e:
            self.logging.error(f"{str(self.id_prefix)}_Handler.get_item_list error: {str(e)}")
            raise HTTPException(status_code=500,detail=f"{str(self.id_prefix)}_Handler.get_item_list error: {str(e)}")
        
        
    async def get_cache_status(self) -> dict:
        try:
            return self.cache.get_cache_stats_category(self.cache_category)
        except Exception as e:
            self.logging.error(f"{str(self.id_prefix)}_Handler.get_cache_status error: {str(e)}")
            raise HTTPException(status_code=500,detail=f"{str(self.id_prefix)}_Handler.get_cache_status error: {str(e)}")
            

    async def _fetch_batch(self, batch_ids) -> Dict[str, T]:
        batch_resources = {}
        docs = self.db.collection(self.collection_name)\
                    .where('id', 'in', batch_ids)\
                    .stream()
                    
        for doc in docs:
            item = self.model_class(**doc.to_dict())
            # 檢查權限並決定是否加入結果
            has_permission = (
                not hasattr(item, 'access') or 
                item.access.has_access(await self.User.get_access(), item.access.companies)
            )
            if has_permission:
                batch_resources[item.id] = item
                self.cache.set(self.cache_category, item.id, item)

        return batch_resources
    
    async def _save_item(self, item:T,method : str) -> Dict:
        '''
        新增，更新單一物件共用邏輯
        Args:
            item: 完整的item類型
        '''
        
        try:
            async def save_to_db():

                data = item.model_dump()
                self.db.collection(self.collection_name).document(item.id).set(data)
                self.cache.set(self.cache_category,item.id,item)

                return item
            if method == "post":
                return await save_to_db()
            elif method == "put":
                if hasattr(item, 'access'):
                    if not item.access.has_access(await self.User.get_access(), item.access.companies):
                        self.logging.info(f"{str(self.uid)}has no access to item :{str(item.id)}")
                        raise HTTPException(status_code=403,detail=f"{str(self.uid)}has no access to item :{str(item.id)}")
                return await save_to_db()
            
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
    


class PropertyLogHandler(BaseHandler):
    pass


class PropertyRelatedHandler(BaseHandler):
    """Handling property related operation"""
    async def get_id_list_by_property_id(self, property_id:str)-> List[str]:
        """return the id list of resource which belong to the specific property_id

        Args:
            property_id (str): property_id which want to search

        Raises:
            HTTPException: internal error

        Returns:
            List[str]: the id list of the object
        """
        try:
            cache_data = self.cache.get(PropertyResourceType.CACHE.value, PropertyResourceType.get_resource_type(self.id_prefix))
            if cache_data is None :
                doc_ref = self.db.collection(PropertyResourceType.COLLECTION.value).document(PropertyResourceType.get_resource_type(self.id_prefix))
                resource = doc_ref.get().to_dict()
                self.cache.set(PropertyResourceType.CACHE.value, PropertyResourceType.get_resource_type(self.id_prefix), resource)
            else:
                resource = cache_data
            return resource[property_id]
        except Exception as e:
            self.logging.error(f"{str(self.id_prefix)}_Handler.find_by_property_id error: {str(e)}")
            raise HTTPException(status_code=500,detail=f"{str(self.id_prefix)}_Handler.find_by_property_id: {str(e)}")
    
    async def get_resources_by_property_id(self, property_id: str) -> Dict[str, T]:
        """return info of item based on which property and which handler 

        Args:
            property_id (str): property_id which want to search

        Raises:
            HTTPException: 500 , internal error

        Returns:
            Dict[str, T]: Dict with item which key is id value is object 
        """
        try:
            ids = self.get_id_list_by_property_id(property_id)
            return await self.get_items(ids)
        
        except Exception as e:
            self.logging.error(f"{str(self.id_prefix)}_Handler.find_by_property_id error: {str(e)}")
            raise HTTPException(status_code=500,detail=f"{str(self.id_prefix)}_Handler.find_by_property_id: {str(e)}")
        