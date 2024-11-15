from .Base import PropertyRelatedHandler, Access
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date

class Lease(BaseModel):
    id : str
    time_start : date
    time_end : date
    time_early : date
    deposit : int
    payment_method : str
    electric : float 
    version : int #update lease will change this
    status : bool
    note : Optional[str]
    mini_note : Optional[str]
    property_id : str
    tenant_id : str
    room_id : str
    file : List
    access : Access

    @field_validator('time_start', 'time_end', 'time_early')
    def parse_date(cls, value):
        if isinstance(value, datetime):
            return value.date()
        elif isinstance(value, date):
            return value
        raise ValueError('Invalid date format')



class LeasesHandler(PropertyRelatedHandler):
        
    def __init__(self, uid: str):
            super().__init__(uid)
            self.collection_name = "leases"
            self.model_class = Lease
            self.cache_category = "leases"
            self.id_prefix = "LEAS"

