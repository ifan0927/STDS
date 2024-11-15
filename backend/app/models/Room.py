from .Base import PropertyRelatedHandler, Access
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict

class Room(BaseModel):
    id : str
    name : str
    size : float
    storey : float
    type : str
    facilities : Dict
    payment_method : Dict
    note : Optional[str]
    property_id : str
    file : List
    access : Access


class RoomHandler(PropertyRelatedHandler):

    def __init__(self, uid: str):
        super().__init__(uid)  
        self.collection_name = "rooms"
        self.model_class = Room
        self.cache_category = "rooms"
        self.id_prefix = "ROOM"  
