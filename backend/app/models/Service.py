from fastapi import HTTPException
from .Property import PropertyHandler
from .Room import RoomHandler
from .Tenant import TenantHandler
from .Leases import LeasesHandler
from typing import List, Dict 
from ..config.logger import logger
from ..config.exception import CacheError

class PropertyService:
    
    def __init__(self, uid: str):
        self.property_handler = PropertyHandler(uid)
        self.room_handler = RoomHandler(uid)
        self.tenant_handler = TenantHandler(uid)
        self.lease_handler = LeasesHandler(uid)
        self.logging = logger
        self.id_prefix = "Property"

    async def get_occupancy_status(self, property_id: str) -> List[Dict]:
        """
        Get list of active leases and empty room information for a specific property.

        Args:
            property_id (str): The ID of the property to query

        Returns:
            List[Dict]: A list of dictionaries containing room and lease information.
            Each dictionary contains:
                {
                    "room_name": str,    # Name of the room
                    "room_id": str,      # Room identifier
                    "tenant_name": str,  # Name of tenant (None if vacant)
                    "tenant_tel": str,   # Tenant's contact number (None if vacant)
                    "tenant_id": str,    # Tenant identifier (None if vacant)
                    "lease_time_start": datetime,  # Lease start date (None if vacant)
                    "lease_time_end": datetime,    # Lease end date (None if vacant)
                    "lease_id": str,     # Lease identifier (None if vacant)
                }
            
        """
        # TODO: 找到符合的property id中的room/lease 列表，從lease列表中去抓tenant 抓取資料
        try:
            pass
        except Exception as e:
            self.logging.error(f"{str(self.id_prefix)}_Service.get_occupancy_status error: {str(e)}")
            raise HTTPException(status_code=500,detail=f"{str(self.id_prefix)}_Service._save_item error: {str(e)}")
            