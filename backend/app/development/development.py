from fastapi import APIRouter,HTTPException,Depends
from ..dependencies.dependencies import get_app_settings
from firebase_admin import auth
import requests

router = APIRouter(prefix="/development")

# 開發用的測試路由
@router.get("/get-test-token/{uid}",tags=['development'])
async def get_test_id_token(uid: str,setting:dict = Depends(get_app_settings)):
    if not setting['debug']:
        raise HTTPException(status_code=404)
        
    try:
        # 1. 首先創建 custom token
        custom_token = auth.create_custom_token(uid).decode('utf-8')
        
        # 2. 使用 Firebase Auth REST API 換取 ID token
        response = requests.post(
            f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken',
            params={
                'key': 'AIzaSyCUa8h4RSThTirFsCYcSs4qgAn51fq8n2Q'  # 需要替換成你的 Firebase Web API Key
            },
            json={
                'token': custom_token,
                'returnSecureToken': True
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to get ID token")
            
        # 返回 ID token
        return {
            "id_token": response.json()['idToken'],
            "usage": "在 Postman 中使用這個 token 作為 Bearer Token"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))