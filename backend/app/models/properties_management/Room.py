from ..Base import PropertyRelatedHandler, Access
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Dict, Union

class Room(BaseModel):
    id: str
    name: str
    size: float
    storey: float
    type: str
    facilities: Dict[str, int] = Field(default_factory=dict)
    payment_method: Dict[str, Union[int, float]] = Field(default_factory=dict)
    note: Optional[str] = ''
    property_id: str
    file: List = Field(default_factory=list)  # 確保默認為空列表
    access: Access
    updated_at: Optional[datetime] = None

    @field_validator('facilities', 'payment_method', mode='before')
    @classmethod
    def ensure_dict_not_none(cls, v):
        return v if v is not None else {}

    @field_validator('file', mode='before')
    @classmethod
    def ensure_list_not_none(cls, v):
        # 確保file字段始終為列表
        if v is None:
            return []
        if isinstance(v, dict):
            return []
        return v

    @field_validator('note')
    @classmethod
    def ensure_note_not_none(cls, v):
        return v or ''


class RoomHandler(PropertyRelatedHandler):

    def __init__(self, uid: str):
        super().__init__(uid)  
        self.collection_name = "rooms"
        self.model_class = Room
        self.cache_category = "rooms"
        self.id_prefix = "ROOM"  
