from fastapi import HTTPException
from .Base import BaseHandler

class LeasesHandler(BaseHandler):
        
    def __init__(self, access_company):
            super().__init__(access_company)

    async def leases_list(self):
        '''
        取得租約清單，只返回有權限的物業

        Returns:
            Optional[List[Dict[str, Any]]]: 租約清單或 None (若無資料)
        '''
        return 

        