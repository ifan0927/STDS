from fastapi import APIRouter,Depends,HTTPException
from ..models.Property import PropertyHandler
from ..dependency.dependencies import verify_token 

router = APIRouter(prefix="/properties-management")

@router.get("/properties",tags=['properties-management'])
async def get_properties(
    token = Depends(verify_token)
):
    try:
        property_handler = PropertyHandler(token['uid'])
        return await property_handler.get_item_list()
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"/properties error:{str(e)}")
    
@router.get("/properties/{property_id}",tags=['properties-management'])
async def get_property(
    property_id : str,
    token = Depends(verify_token)
):
    try:
        property_handler = PropertyHandler(token['uid'])
        return await property_handler.get_item(property_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error msg:{e}"
        )
    
@router.get("/properties/{property_id}/leases",tags=['properties-management'])
async def get_leases_list(
    property_id : str,
    token = Depends(verify_token)
):
    '''
    返回房號(包含空房,有房客)，房客姓名，電話，繳費類型，租約到期日，繳租日期
    '''
    return True



    
