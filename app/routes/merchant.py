from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.crud import MongoManager
from app.core.database import get_database
from app.core.logging import logger
from app.core.auth import get_current_user
from app.core.models.user import UserInDB
from app.core.models.response import MerchantResponseModel
from app.core.exceptions import DatabaseException
from typing import List, Dict, Any

router = APIRouter(prefix="/merchant", tags=["Merchant"])

@router.get("/", response_model=MerchantResponseModel[List[Dict[Any, Any]]])
async def get_merchants(
    current_user: UserInDB = Depends(get_current_user),
    name: str = None,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Items per page"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    logger.info(f"User {current_user.username} accessing merchants endpoint")
    try:
        logger.info(f"Fetching merchants - Page: {page}, Size: {page_size}, Filter: {name}")
        
        # Calculate skip based on page and page_size
        skip: int = (page - 1) * page_size
        limit: int = page_size
        
        crud = MongoManager("merchant")
        
        # Get total count for pagination metadata
        total_count = await crud.count(db, name)
        logger.info(f"Total merchants count: {total_count}")
        
        # Get paginated data
        merchants = await crud.get_all(db, name, limit=limit, skip=skip)
        
        # Add pagination metadata
        pagination = {
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "pages": (total_count + page_size - 1) // page_size
        }
        
        logger.info(f"Returning JSON response with {len(merchants)} merchants")
        return MerchantResponseModel(
            data=merchants,
            pagination=pagination
        )

    except Exception as e:
        logger.error(f"Error fetching merchants: {str(e)}", exc_info=True)
        raise DatabaseException(detail=f"Failed to fetch merchants: {str(e)}") 