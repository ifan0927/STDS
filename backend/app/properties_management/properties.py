from fastapi import APIRouter,Depends,HTTPException
from ..dependency.dependencies import verify_token 

router = APIRouter(prefix="/properties-management")

@router.get("/properties",tags=['properties-management'])
async def get_properties(
    auth_data = Depends(verify_token)
):
    try:
        P_Handler =  auth_data['P_handler']
        result = await P_Handler.properties_list()
        if result is None:
            raise HTTPException(status_code=403,detail="無存取權限")
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error msg: {e}"
        )
    
@router.get("/properties/{property_id}",tags=['properties-management'])
async def get_property(
    property_id : str,
    auth_data = Depends(verify_token)
):
    try:
        P_Handler = auth_data['P_handler']
        result = await P_Handler.get_property(property_id)
        if result is None:
            raise HTTPException(status_code=403,detail="無存取權限")
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error msg:{e}"
        )
    



    
