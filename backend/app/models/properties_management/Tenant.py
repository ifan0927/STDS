from ..Base import BaseHandler, Access
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import date, datetime

class Tenant(BaseModel):
    id : str
    name : str
    birthday : date
    address : str
    tel : str
    job : Optional[str]
    contact : Optional[str]
    contact_tel : Optional[str]
    email : Optional[str]
    note : Optional[str]
    leases_id : str
    file : List
    access : Access

    @field_validator('birthday')
    def parse_date(cls, value):
        if isinstance(value, datetime):
            return value.date()
        elif isinstance(value, date):
            return value
        raise ValueError('Invalid date format')
    
class TenantHandler(BaseHandler):

    def __init__(self, uid: str):
        super().__init__(uid)
        self.collection_name = "tenants"
        self.model_class = Tenant
        self.cache_category = "tenants"
        self.id_prefix = "TENA"


