from fastapi import HTTPException
from ..config.firebase import get_firestore
from ..config.cache import CacheHandler
from ..config.logger import get_logger



class PropertyHandler():

    def __init__(self, acess_company):
        self.access_company = acess_company
        self.cache = CacheHandler()
    
    async def db_init(self):
        self.db = await get_firestore()
        self.logging = await get_logger()
        
    async def properties_list(self):
        try:
            results = []
            if self.cache.get('properties'):
                value = self.cache.get('properties')
            else:
                properties_dict = {}
                docs = self.db.collection('properties').stream()
                for doc in docs:
                    properties_dict[doc.id] = doc.to_dict()
                value = properties_dict
                self.cache.set('properties',properties_dict)

            for key , item in value.items():
                if self._has_access(item['access']['companies'])  :
                    result = {
                        'id': item['id'],
                        'name' : item['name'],
                        'nickname' : item['nickname'],
                        'address' : item['address'],
                        'phone' : item['phone'],
                        'electric_price' : item['electric_price'],
                        'electric_month' : item['electric_month']
                    }
                    results.append(result)
            if not results:
                return None
            return results
        except Exception as e:
            print(f"Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_property(self,property_id):
        try:
            if self.cache.get(property_id):
                value = self.cache.get(property_id)
            else:
                doc_ref = self.db.collection('properties').document(property_id)
                doc = doc_ref.get()
                self.cache.set(property_id,doc.to_dict())
                value = doc.to_dict()
            if self._has_access(value['access']['companies']):
                return value
            else:
                return None
        except Exception as e:
            self.logging.error(f"取得物業資料失敗{property_id}:{str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    

    def _has_access(self, access_list):
        return self.access_company in access_list