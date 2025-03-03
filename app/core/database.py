from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import Depends
from app.core.config import settings

# Database connection
db = AsyncIOMotorClient()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    db.database = db.client[settings.database_name]

async def close_mongo_connection():
    db.client.close()

async def get_database() -> AsyncIOMotorDatabase:
    return db.database 