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

class UserBase(BaseModel):
    username: str
    email: EmailStr
    created_at: datetime = Field(default_factory=utc_now)
    last_login: Optional[datetime] = None

    class Config:
        json_encoders = {
            # Format datetime as yyyy-mm-ddThh:mm:ss+0000
            datetime: lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%S+0000") if dt else None
        }

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

class UserResponse(UserBase):
    pass 