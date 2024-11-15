from fastapi import APIRouter,HTTPException,Depends,Response,status
from ..dependency.dependencies import get_app_settings
from ..models.Property import PropertyHandler , Property
from firebase_admin import auth
import requests 
import json

with open('key.json', 'r') as f:
    data = json.load(f)
    api_key = data["key"]

router = APIRouter(prefix="/development")

@router.post("/test-post",tags=['development'])
async def post_test_data(item : Property,setting = Depends(get_app_settings)):
    if not setting['debug']:
        raise HTTPException(status_code=404)
    
    try:
        handler = PropertyHandler('test')
        item.id = handler.id_generate()
        return await handler.post_item(item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"dev_test error : {str(e)}")
    
@router.put("/test-post/{id}",tags=['development'])
async def post_test_data(id: str,info : Property,setting = Depends(get_app_settings)):
    if not setting['debug']:
        raise HTTPException(status_code=404)
    
    try:
        handler = PropertyHandler('test')
        return await handler.put_item(info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"dev_test error : {str(e)}")


@router.get("/check-cache-status",tags=['development'])
async def check_cache_status(setting = Depends(get_app_settings)):
    if not setting['debug']:
        raise HTTPException(status_code=404)
    
    try:
        handler = PropertyHandler('test')
        return await handler.get_cache_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"dev_test error : {str(e)}")

@router.delete("/test-delete/{id}",tags=['development'])
async def post_test_data(id : str,setting = Depends(get_app_settings)):
    if not setting['debug']:
        raise HTTPException(status_code=404)
    
    try:
        handler = PropertyHandler('test')
        return await handler.delete_item(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"dev_test error : {str(e)}")


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
                'key': api_key  # 需要替換成你的 Firebase Web API Key
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