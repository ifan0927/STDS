from fastapi import APIRouter,Depends,HTTPException
from google.cloud.firestore import FieldFilter
from ..dependencies.dependencies import verify_token, get_firestore
from ..dependencies.dependencies import get_document,get_collection

router = APIRouter(prefix="/properties-management")

@router.get("/properties",tags=['properties-management'])
async def get_properties(
    token:dict = Depends(verify_token)
):
    try:
        datas = []
        docs = await get_collection("properties",20,0)
        for doc in docs:
            property = doc.to_dict() 
            data = {
                'id' : property['id'],
                'nickname': property['nickname'],
                'address': property['address'],
                'owner':property['owner'],
                'electric_price': property['electric_price'],
                'electric_month': property['electric_month']
            }
            datas.append(data)
        return datas
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error msg: {e}"
        )

@router.get("/properties/{properties_id}", tags=['properties-management'])
async def get_property(
    properties_id :str,
    token:dict = Depends(verify_token)
):
    return await get_document("properties",properties_id)
    
##之後可能設備格式會換
@router.get("/properties/{properties_id}/facilities", tags=['properties-management'])
async def get_property_facilities(
    properties_id : str,
    token: dict = Depends(verify_token)
):
    property = await get_document("properties",properties_id)
    data = []
    for facility in property['facilities']:
        data.append(facility)
    return data

@router.get("/properties/{properties_id}/leases", tags=['properties-management'])
async def get_property_leases(
    properties_id : str,
    token: dict = Depends(verify_token),
    db = Depends(get_firestore)
):
    try:
        rooms_docs = (
            db.collection("rooms")
            .where(filter=FieldFilter("property_id","==",properties_id))
        )
        leases_docs = (
            db.collection("leases")
            .where(filter=FieldFilter("property_id", "==", properties_id))
            .where(filter=FieldFilter("status", "==", True))
            .stream()
        )
        leases_list = []
        for doc in leases_docs:
            l = doc.to_dict()
            

        return(datas)  
    except Exception as e:
        raise HTTPException(
            status_code= 500,
            detail=f"Error msg: {e}"
        )
    



