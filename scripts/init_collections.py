from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from app.core.config import settings


async def init_collections():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]

    # Create users collection with schema validation
    await db.create_collection("user", 
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["username", "email", "hashed_password", "created_at"],
                "properties": {
                    "username": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "email": {
                        "bsonType": "string",
                        "pattern": "^.+@.+$",
                        "description": "must be a valid email address"
                    },
                    "hashed_password": {
                        "bsonType": "string",
                        "description": "must be a string and is required"
                    },
                    "created_at": {
                        "bsonType": "date",
                        "description": "must be a date and is required"
                    },
                    "last_login": {
                        "bsonType": ["date", "null"],
                        "description": "must be a date or null"
                    }
                },
                "additionalProperties": False  # Prevents additional fields
            }
        }
    )

    # Create indexes
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)
    await db.users.create_index("created_at")

    print("Collections initialized successfully")
    client.close()

if __name__ == "__main__":
    asyncio.run(init_collections()) 