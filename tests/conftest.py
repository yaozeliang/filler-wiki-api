import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import os

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def mongodb_client():
    # Use a test database for testing
    test_mongodb_url = os.getenv("TEST_MONGODB_URL", settings.mongodb_url)
    client = AsyncIOMotorClient(test_mongodb_url)
    yield client
    client.close()

@pytest.fixture(scope="function")
async def mongodb(mongodb_client):
    # Use a separate test database to avoid affecting production data
    test_db_name = os.getenv("TEST_DATABASE_NAME", f"{settings.database_name}_test")
    db = mongodb_client[test_db_name]
    
    # Clear test collections before each test (don't drop the database in Atlas)
    collections = await db.list_collection_names()
    for collection in collections:
        await db.drop_collection(collection)
    
    # Initialize collections
    if "users" not in collections:
        await db.create_collection("users")
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)
    
    yield db

@pytest.fixture
async def override_get_db(mongodb):
    async def _override_get_db():
        return mongodb
    return _override_get_db 