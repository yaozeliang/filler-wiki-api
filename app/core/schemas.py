from typing import TypeVar, Generic, Optional, List, Any, Dict
from pydantic import BaseModel

T = TypeVar('T')

class PaginationModel(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int

class ResponseModel(BaseModel, Generic[T]):
    status: str = "success"
    message: Optional[str] = None
    data: Optional[T] = None

class BrandResponseModel(BaseModel, Generic[T]):
    status: str = "success"
    data: Optional[T] = None
    pagination: Optional[PaginationModel] = None 