from ..Base import BaseHandler, Access
from pydantic import BaseModel, Field
from typing import Optional, List 


class Property(BaseModel):
    id : str
    name : str
    nickname : str
    address : str
    phone : str
    owner: str
    note: Optional[str]
    facilities: List[str]
    electric_price: float   
    electric_month: str = Field(..., pattern="^(單月|雙月)$")  # 限制只能是單月或雙月
    file: List[str] = []
    access: Access

class PropertyHandler(BaseHandler):
    def __init__(self, uid: str):
        super().__init__(uid)
        self.collection_name = "properties"
        self.model_class = Property
        self.cache_category = "properties"
        self.id_prefix = "PROP"



        
    