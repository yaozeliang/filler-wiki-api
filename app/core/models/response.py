from typing import TypeVar, Generic, Optional, List, Any, Dict
from pydantic import BaseModel

T = TypeVar('T')

class PaginationModel(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int

class BaseResponseModel(BaseModel, Generic[T]):
    status: str = "success"
    message: Optional[str] = None
    data: Optional[T] = None
    pagination: Optional[PaginationModel] = None

class EntityResponseModel(BaseResponseModel, Generic[T]):
    """Generic response model for entity data with pagination"""
    pass

# Specific entity response models
class BrandResponseModel(EntityResponseModel, Generic[T]):
    """Response model for brand data"""
    pass

class MerchantResponseModel(EntityResponseModel, Generic[T]):
    """Response model for merchant data"""
    pass 