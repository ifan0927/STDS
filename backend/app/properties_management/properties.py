from fastapi import APIRouter,Depends,HTTPException
from ..models.Property import PropertyHandler
from ..dependency.dependencies import verify_token 

router = APIRouter(prefix="/properties-management")

@router.get("/properties",tags=['properties-management'])
async def get_properties(
    token = Depends(verify_token)
):
    return True
    
@router.get("/properties/{property_id}",tags=['properties-management'])
async def get_property(
    property_id : str,
    token = Depends(verify_token)
):
    try:
        property_handler = PropertyHandler(token['uid'])
        result = await property_handler.get_item(property_id)
        if result is None:
            raise HTTPException(status_code=403,detail="無存取權限")
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error msg:{e}"
        )
    



    
