from ..Base import PropertyLogHandler
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime, date

class Logs(BaseModel):
    id : str
    old_id : str
    property_id : str
    room_id : str
    user_id : str
    member : List
    old_user_id : str
    updated_at : datetime
    category : str
    facility : str
    content : str
    file : List

    @field_validator('updated_at')
    def parse_time(cls, value):
        if isinstance(value, datetime):
            return value
        raise ValueError('Invalid date format')
    
    @field_validator('room_id')
    def parse_room_id(cls, value):
        if isinstance(value, str):
            return value
        elif isinstance(value, int):
            return "default"
        raise ValueError(f'Invalid room id {str(value)}')
    
class LogsHandler(PropertyLogHandler):

    def __init__(self, uid):
        super().__init__(uid)
        self.collection_name = "Logs"
        self.model_class = Logs
        self.cache_category = "Property_Logs"
        self.id_prefix = "ESTA"