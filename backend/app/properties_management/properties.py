from fastapi import APIRouter, Depends, HTTPException, Response
from ..models.properties_management.Property import PropertyHandler, Property
from ..dependency.dependencies import verify_token 

router = APIRouter(prefix="/properties-management")

@router.get("/properties",tags=['properties-management'])
async def get_properties(
    token = Depends(verify_token)
) -> list:
    """
    get  properties list
    
    Returns:
        Property: The list of properties which user has access to
    
    Raises:
        400: ID mismatch
        404: Property not found
        500: Internal unknown error
    """

    property_handler = PropertyHandler(token['uid'])
    return await property_handler.get_item_list()
        
    
@router.get("/properties/{property_id}",tags=['properties-management'])
async def get_property(
    property_id : str,
    token = Depends(verify_token)
) -> Property:
    """
    get property info
    
    Parameters:
        property_id: The ID of the property to get info 
    
    Returns:
        Property: The property look for
    
    Raises:
        400: ID mismatch
        403: Unauthorized access
        404: Property not found
        500: Internal unknown error
    """

    property_handler = PropertyHandler(token['uid'])
    result = await property_handler.get_item(property_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Property:{str(property_id)} is not found")
    return result
    
    
@router.put("/properties/{property_id}", tags=['properties-management'])
async def put_property(
    item: Property,
    property_id : str,
    token = Depends(verify_token)
) -> Property:
    """
    Update a property
    
    Parameters:
        property_id: The ID of the property to update
        item: The updated property data
    
    Returns:
        Property: The updated property
    
    Raises:
        400: ID mismatch
        403: Unauthorized access
        404: Property not found
        500: Internal unknown error
    """
    if item.id != property_id:
        raise HTTPException(status_code=400, message="Property ID mismatch")
    property_handler = PropertyHandler(token['uid'])
    return await property_handler.put_item(item)

@router.post("/properties/{property_id}", tags=['properties-management'])
async def put_property(
    item: Property,
    property_id : str,
    token = Depends(verify_token)
) -> Property:
    """
    create new property
    
    Parameters:
        property_id: The ID of the property to update
        item: The updated property data
    
    Returns:
        Property: The created property
    
    Raises:
        400: ID mismatch
        404: Property not found
        500: Internal unknown error
    """
    if item.id != property_id:
        raise HTTPException(status_code=400, message="Property ID mismatch")
    property_handler = PropertyHandler(token['uid'])
    return await property_handler.post_item(item)

@router.delete("/properties/{property_id}", tags=['properties-management'])
async def delete_property(
    property_id : str,
    token = Depends(verify_token)
) -> Response:
    '''
    delete property

    Parameters:
        property_id : The ID of the property to delete
    Returns:
        Response : 204 if success
    Raises:
        403: Unauthorized access
        404: Property not found
        500: Internal unknown error
    '''
    property_handler = PropertyHandler(token['uid'])
    return await property_handler.delete_item(property_id)
    
    
@router.get("/properties/{property_id}/leases",tags=['properties-management'])
async def get_leases_list(
    property_id : str,
    token = Depends(verify_token)
):
    '''
    返回房號(包含空房,有房客)，房客姓名，電話，繳費類型，租約到期日，繳租日期
    #TODO 尚未完成
    '''
    return True



    
