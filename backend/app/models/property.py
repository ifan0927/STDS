from fastapi import HTTPException
from Base import BaseHandler

class PropertyHandler(BaseHandler):

    def __init__(self, access_company: str):
        super().__init__(access_company)
        
    async def properties_list(self):
        """
        取得物業清單，只返回有權限的物業
        
        Returns:
            Optional[List[Dict[str, Any]]]: 物業清單或 None (若無資料)
        """
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
        """
        取得單一物業資料
        
        Args:
            property_id (str): 物業 ID
            
        Returns:
            Optional[Dict[str, Any]]: 物業資料或 None (若無權限或不存在)
        """
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
        
    ##房號r 繳費類型l 租屋者t 剩餘天數(租約到期日期)l 電話t 下次繳租日l room_id , leases_id , tenants_id
