import firebase_admin
from firebase_admin import  credentials, firestore
from fastapi.security import HTTPBearer

class FirebaseClient:
    _instance = None

    def __init__(self):
        if not FirebaseClient._instance:
            # 初始化 Firebase
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)

            self.db = firestore.client()
        
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = FirebaseClient()
        return cls._instance
    
security = HTTPBearer()
firebase = FirebaseClient.get_instance()
