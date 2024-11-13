from fastapi import HTTPException,Depends,Request
from ..config.firebase import firebase, security
from ..models.Property import PropertyHandler
from ..models.Users import UserHandler
from firebase_admin import auth
'''
putting all the Depends function here 
'''

async def verify_token(token: str = Depends(security)):
    try:
        decoded_token = auth.verify_id_token(token.credentials)
        U_handler = UserHandler(decoded_token['uid'])
        await U_handler.init_user()
        P_handler =  PropertyHandler(await U_handler.get_access())
        await P_handler.db_init()
        return {"token": decoded_token, "P_handler": P_handler}  # 返回字典更清晰
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
