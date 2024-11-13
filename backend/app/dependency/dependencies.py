from fastapi import HTTPException,Depends,Request
from ..config.firebase import firebase, security
from firebase_admin import auth
'''
putting all the Depends function here 
'''

async def verify_token(token: str = Depends(security)):
    try:
        decoded_token = auth.verify_id_token(token.credentials)
        return decoded_token  # 返回字典更清晰
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_app_settings(request: Request):
    return {
        "debug": request.app.debug,
    }
