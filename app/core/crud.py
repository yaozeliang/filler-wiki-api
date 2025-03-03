from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends
from app.core.database import get_database
from datetime import datetime

class MongoManager:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    async def get_all(self, db: AsyncIOMotorDatabase, name: str = None, limit: int = 0, skip: int = 0) -> List[Dict[Any, Any]]:
        collection = db[self.collection_name]
        
        # Set projection to exclude _id field
        projection = {"_id": 0}
        
        if name:
            # Case-insensitive search for either name or manufacturer field
            query = {
                "$or": [
                    {"name": {"$regex": name, "$options": "i"}},
                    {"manufacturer": {"$regex": name, "$options": "i"}}
                ]
            }
            cursor = collection.find(query, projection)
        else:
            cursor = collection.find({}, projection)
        
        # Apply pagination
        if skip > 0:
            cursor = cursor.skip(skip)
        if limit > 0:
            cursor = cursor.limit(limit)
        
        documents = await cursor.to_list(length=None)
        return documents

    async def get_by_id(self, id: str, db: AsyncIOMotorDatabase):
        # Add more methods as needed
        pass 

    async def count(self, db: AsyncIOMotorDatabase, name: str = None) -> int:
        collection = db[self.collection_name]
        if name:
            # Case-insensitive search for either name or manufacturer field
            query = {
                "$or": [
                    {"name": {"$regex": name, "$options": "i"}},
                    {"manufacturer": {"$regex": name, "$options": "i"}}
                ]
            }
            return await collection.count_documents(query)
        else:
            return await collection.count_documents({}) 

    async def create(self, db, data: Dict[Any, Any]) -> Dict[Any, Any]:
        # Add created_at field automatically
        data["created_at"] = {"$currentDate": {"$type": "date"}}
        
        collection = db[self.collection_name]
        result = await collection.insert_one(data)
        
        # Fetch and return the created document
        return await collection.find_one({"_id": result.inserted_id}) 