from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.core.database import connect_to_mongo, close_mongo_connection, get_database
from app.routes import auth, brand, merchant  # Import individual routers directly
from app.core.description import get_api_description
import pytz
import warnings
import logging
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2PasswordBearer
import os
from pathlib import Path

app = FastAPI(
    title="Dermal Filler Wiki API <甄真>",
    description=get_api_description(),
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Auth",
            "description": "Authentication operations",
            "order": 1
        },
        {
            "name": "Brand",
            "description": "Brand Information",
            "order": 2
        },
        {
            "name": "Merchant",
            "description": "Merchant Information",
            "order": 3
        }
    ],
    openapi_url="/openapi.json",
)

# Mount static files directory
# Get the directory of the current file (main.py)
current_dir = Path(__file__).parent
# Path to the images directory
images_dir = current_dir / "images"
# Mount the images directory to /static
app.mount("/static", StaticFiles(directory=str(images_dir)), name="static")

# Include routers - ONLY INCLUDE EACH ROUTER ONCE
app.include_router(auth.router)
app.include_router(brand.router)
app.include_router(merchant.router)  # Add merchant router if not already included

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

# Replace the root endpoint with a redirect to /docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs") 