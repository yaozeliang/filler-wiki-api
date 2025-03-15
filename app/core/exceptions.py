from fastapi import HTTPException, status
from typing import Optional, Dict, Any

class BaseAPIException(HTTPException):
    """Base exception for API errors"""
    def __init__(
        self, 
        status_code: int, 
        detail: str, 
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class DatabaseException(BaseAPIException):
    """Exception for database-related errors"""
    def __init__(
        self, 
        detail: str = "Database operation failed", 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        super().__init__(status_code=status_code, detail=detail)

class ResourceNotFoundException(BaseAPIException):
    """Exception for when a requested resource is not found"""
    def __init__(
        self, 
        resource_type: str, 
        detail: Optional[str] = None
    ):
        if detail is None:
            detail = f"{resource_type} not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class AuthenticationException(BaseAPIException):
    """Exception for authentication errors"""
    def __init__(
        self, 
        detail: str = "Authentication failed", 
        headers: Optional[Dict[str, Any]] = None
    ):
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=detail, 
            headers=headers
        )

class ValidationException(BaseAPIException):
    """Exception for validation errors"""
    def __init__(
        self, 
        detail: str = "Validation error"
    ):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) 