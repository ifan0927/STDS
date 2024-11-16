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
        
    async def get_occupancy_status(self, property_id: str) -> Dict[str, Dict[str, Dict]]:

        """
        Get list of active leases and empty room information for a specific property.

        Args:
            property_id (str): The ID of the property to query

        Returns:    
            Dict[str, Dict[str, Dict]]: A dictionary containing two categories of room information:
                {
                    'success': {
                        'room_id': {
                            'room_name': str,
                            'room_id': str,
                            'room_status': str,  # 'occupied' or 'vacant'
                            ...
                        }
                    },
                    'error': {
                        'room_id': {
                            'room_name': str,
                            'room_id': str,
                            'room_status': 'error',
                            'error_type': str,
                            'error_message': str,
                            ...
                        }
                    }
                }
            
        """
        try:
            result = {}
            rooms = await self.room_handler.find_by_property_id(property_id)
            leases = await self.lease_handler.find_by_property_id(property_id)


            if len(leases) > len(rooms):
                self.logging.debug(f"{property_id}: leases number doesn't match rooms number")
                raise HTTPException(status_code=500, detail=f"{property_id}: leases number doesn't match rooms number")    
            
            # tracking room is occupy or not
            rooms_occupancy_success_status = {}
            rooms_occupancy_error_status = {}
            for _, lease in leases.items():
                try:
                    tenant = await self.tenant_handler.get_item(lease.tenant_id)
                    rooms_occupancy_success_status[lease.room_id] = {
                        'room_name' : rooms[lease.room_id].name,
                        'room_id' : lease.room_id,
                        'room_status' : 'occupied',
                        'tenant_name' : tenant.name,
                        'tenant_tel' : tenant.tel,
                        'tenant_id' : tenant.id,
                        'lease_time_start' : lease.time_start,
                        'lease_time_end' : lease.time_end,
                        'lease_time_early' : lease.time_early
                    }
                    del rooms[lease.room_id]
        
                except Exception as e:
                    self.logging.debug(f"{str(lease.id)}: getting lease data error {str(e)}")
                    rooms_occupancy_success_status[lease.room_id] = {
                        'room_name' : room.name,
                        'room_id' : room.id,
                        'room_status' : 'error',
                        'tenant_name' : None,
                        'tenant_tel' : None,
                        'tenant_id' : None,
                        'lease_time_start' : None,
                        'lease_time_end' : None,
                        'lease_time_early' : None
                     }

            
            for _, room in rooms.items():
                rooms_occupancy_success_status[room.id] = {
                    'room_name' : room.name,
                    'room_id' : room.id,
                    'room_status' : 'vacant',
                    'tenant_name' : None,
                    'tenant_tel' : None,
                    'tenant_id' : None,
                    'lease_time_start' : None,
                    'lease_time_end' : None,
                    'lease_time_early' : None
                }

            result['error'] = rooms_occupancy_error_status
            result['success'] = rooms_occupancy_success_status
            return result
            
        except Exception as e:
            self.logging.error(f"{str(self.id_prefix)}_Service.get_occupancy_status error: {str(e)}")
            raise HTTPException(status_code=500,detail=f"{str(self.id_prefix)}_Service._save_item error: {str(e)}")
        
    async def make_property_index(self):
        try:
            property_room_index  = {
                "PROP_1731656683897_M7FWV" : [], 
                "PROP_1731656683897_Vca3F" : [],
                "PROP_1731656683898_0Zjpn" : [],
                "PROP_1731656683898_4FkXx" : [],
                "PROP_1731656683898_74N9A" : [],
                "PROP_1731656683898_A8W6g" : [],
                "PROP_1731656683898_IVUyY" : [],
                "PROP_1731656683898_OmVpw" : [],
                "PROP_1731656683898_P6h3C" : [],
                "PROP_1731656683898_VnDtU" : [],
                "PROP_1731656683898_XDOZW" : [],
                "PROP_1731656683898_j9uAn" : [],
                "PROP_1731656683898_r1Zlc" : [],
                "PROP_1731656683898_vd16m" : [],
                "PROP_1731656683898_wJxku" : []
            }

            property_lease_index  = {
                "PROP_1731656683897_M7FWV" : [], 
                "PROP_1731656683897_Vca3F" : [],
                "PROP_1731656683898_0Zjpn" : [],
                "PROP_1731656683898_4FkXx" : [],
                "PROP_1731656683898_74N9A" : [],
                "PROP_1731656683898_A8W6g" : [],
                "PROP_1731656683898_IVUyY" : [],
                "PROP_1731656683898_OmVpw" : [],
                "PROP_1731656683898_P6h3C" : [],
                "PROP_1731656683898_VnDtU" : [],
                "PROP_1731656683898_XDOZW" : [],
                "PROP_1731656683898_j9uAn" : [],
                "PROP_1731656683898_r1Zlc" : [],
                "PROP_1731656683898_vd16m" : [],
                "PROP_1731656683898_wJxku" : []
            }

            

            room_docs = self.property_handler.db.collection(self.room_handler.collection_name).stream()
            error_list = []
            for doc in room_docs:
                data = doc.to_dict()
                try:
                    property_room_index[data['property_id']].append(data['id'])
                except Exception as e:
                    error_list.append(doc.id)
            
            leases_docs = self.property_handler.db.collection(self.lease_handler.collection_name).stream()
            for doc in leases_docs:
                data = doc.to_dict()
                try:
                    property_lease_index[data['property_id']].append(data['id'])
                except Exception as e:
                    error_list.append(doc.id)
            try:
                self.property_handler.db.collection('property_resource_index').document('property_lease_index').set(property_lease_index)
                self.property_handler.db.collection('property_resource_index').document('property_room_index').set(property_room_index)
            except Exception as e:
                raise HTTPException(detail=f"{str(e)}")            

            return True
        except Exception as e:
            raise HTTPException(status_code=500 , detail=f"make_index_error {str(e)}")
        