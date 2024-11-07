from fastapi import HTTPException,Depends,Request
from ..config.firebase import firebase, security
from firebase_admin import auth
'''
putting all the Depends function here 
'''
async def get_firestore():
    return firebase.db

async def get_collection(col: str, limit:int , offset:int):
    try:
        db = firebase.db
        docs = db.collection(col).limit(limit).offset(offset).get()
        if docs:
            return docs
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Cant find collection: {col}"
            ) 
    except Exception as e:
        raise HTTPException(
            status_code= 404,
            detail=f"Error msg: {e}"
        )
    
async def get_document(col: str , doc_id: str):
    try:
        db = firebase.db
        doc_ref = db.collection(col).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Cant find doc:{doc_id} in {col}"
            ) 
    except Exception as e:
        raise HTTPException(
            status_code= 404,
            detail=f"Error msg: {e}"
        )

async def verify_token(token: str = Depends(security)):
    try:
        decoded_token = auth.verify_id_token(token.credentials)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_app_settings(request: Request):
    return {
        "debug": request.app.debug,
    }
