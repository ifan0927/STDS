from ..config.firebase import get_firestore
from ..config.cache import CacheHandler
from ..config.logger import get_logger
from abc import ABC

class BaseHandler(ABC):
    def __init__(self, access_company: str):
        """
        Initialize the base handler.
        
        Args:
            access_company: Company identifier for access control
        """
        self.access_company = access_company
        self.cache = CacheHandler()
        self.db = None
        self.logging = None
    
    async def db_init(self):
        """Initialize database and logging connections."""
        self.db = await get_firestore()
        self.logging = await get_logger()

    def _has_access(self, access_list):
        return self.access_company in access_list