from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from app.core.auth import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.core.logging import logger
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.crud import get_database
from app.core.security import get_password_hash, validate_password
from app.core.models.user import UserCreate, UserResponse, Token
from pymongo.errors import DuplicateKeyError, ConnectionFailure

# Change tags to "Auth" and add openapi_tags metadata
router = APIRouter(
    prefix="/auth",  # Add prefix for better URL organization
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

# Move register endpoint first
@router.post("/register", 
    response_model=UserResponse,
    summary="Register new user",
    description="Create a new user account with username and password"
)
async def register_user(user_create: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    try:
        # Validate password
        if not validate_password(user_create.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet complexity requirements"
            )
        
        # Check if user exists
        if await db.users.find_one({"username": user_create.username}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email exists
        if await db.users.find_one({"email": user_create.email}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user document
        user_dict = {
            "username": user_create.username,
            "email": user_create.email,
            "hashed_password": get_password_hash(user_create.password),
            "created_at": datetime.utcnow().replace(microsecond=0),
            "last_login": None
        }
        
        try:
            result = await db.users.insert_one(user_dict)
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        except ConnectionFailure:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection error"
            )
            
        created_user = await db.users.find_one({"_id": result.inserted_id})
        logger.info(f"User registered successfully: {user_create.username}")
        return UserResponse(**created_user)
        
    except Exception as e:
        logger.error(f"Error registering user {user_create.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create user"
        )

@router.post("/token", 
    response_model=Token,
    summary="Login for access token",
    description="OAuth2 compatible token login, get an access token for future requests"
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last_login
    await db.users.update_one(
        {"username": user.username},
        {"$set": {"last_login": datetime.utcnow().replace(microsecond=0)}}
    )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"} 