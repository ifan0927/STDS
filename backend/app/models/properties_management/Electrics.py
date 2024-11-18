from ..Base import PropertyLogHandler
from pydantic import BaseModel, field_validator
from datetime import datetime

class Electric(BaseModel):
    id : str
    room_id : str
    degrees : float
    user_id : str
    old_user_id : str
    updated_at : datetime

    @field_validator
    def parse_date(cls, value):
        if isinstance(value, datetime):
            return value
        raise ValueError('Invalid date format')
    
class ElectricHandler(PropertyLogHandler):

    def __init__(self, uid):
        super().__init__(uid)
        self.collection_name = "electrics"
        self.model_class = Electric
        self.cache_category = "electric"
        self.id_prefix = "ELEC"