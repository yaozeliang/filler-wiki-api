from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

def utc_now() -> datetime:
    """Returns current UTC time in the required format"""
    return datetime.utcnow().replace(microsecond=0)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Base user model without authentication fields
class UserBase(BaseModel):
    username: str
    email: EmailStr

    class Config:
        json_encoders = {
            # Format datetime as yyyy-mm-ddThh:mm:ss+0000
            datetime: lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%S+0000") if dt else None
        }

# Model for user creation - only includes fields needed for registration
class UserCreate(UserBase):
    password: str

# Internal model with all fields including timestamps
class UserInternal(UserBase):
    created_at: datetime = Field(default_factory=utc_now)
    last_login: Optional[datetime] = None

# Complete user model for database storage
class UserInDB(UserInternal):
    hashed_password: str

# Response model for user information
class UserResponse(UserBase):
    created_at: datetime
    last_login: Optional[datetime] = None 