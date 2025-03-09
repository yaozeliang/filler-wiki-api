from datetime import datetime
from fastapi import FastAPI
from app.core.database import connect_to_mongo, close_mongo_connection, get_database
from app.routes import router, auth, brand
from app.core.description import get_api_description
import pytz
import warnings
import logging

app = FastAPI(
    title="Filler Wiki API",
    description=get_api_description(),
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Auth",
            "description": "Authentication operations",
            "order": 1
        },
        {
            "name": "Brands",
            "description": "Brand management operations",
            "order": 2
        }
    ]
)

# Include combined router
app.include_router(router)
app.include_router(auth.router)
app.include_router(brand.router)

# Suppress the bcrypt warning
warnings.filterwarnings("ignore", message=".*error reading bcrypt version.*")

# Or redirect it to debug level instead of warning
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

@app.on_event("startup")
async def startup_db_client():
    try:
        await connect_to_mongo()
        # Test the connection
        db = await get_database()
        result = await db.command("ping")
        if result.get("ok") == 1:
            logging.info("Successfully connected to MongoDB")
        else:
            logging.error("Failed to connect to MongoDB: Ping command failed")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {str(e)}", exc_info=True)
        # Don't raise the exception here, let the app start anyway
        # but log the error for debugging

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/")
async def root():
    return {"message": "Hello World"} 