"""Main FastAPI application module."""
from datetime import datetime
from pathlib import Path
import logging
import warnings
from typing import Any

import pytz
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.database import (
    connect_to_mongo,
    close_mongo_connection,
    get_database,
)
from app.routes import auth, brand, merchant, test_axione
from app.core.description import get_api_description

# Suppress the bcrypt warning
warnings.filterwarnings("ignore", message=".*error reading bcrypt version.*")

# Set bcrypt logger to ERROR level
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for database connection."""
    # Startup
    try:
        await connect_to_mongo()
        db = await get_database()
        result = await db.command("ping")
        if result.get("ok") == 1:
            logging.info("Successfully connected to MongoDB")
        else:
            logging.error("Failed to connect to MongoDB: Ping command failed")
    except Exception as e:
        logging.error("Failed to connect to MongoDB: %s", str(e), exc_info=True)
    
    yield
    
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Dermal Filler Wiki API <甄真>",
    description=get_api_description(),
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Auth",
            "description": "Authentication operations",
            "order": 1,
        },
        {
            "name": "Brand",
            "description": "Brand Information",
            "order": 2,
        },
        {
            "name": "Merchant",
            "description": "Merchant Information",
            "order": 3,
        },
    ],
    openapi_url="/openapi.json",
)

# Mount static files directory
current_dir = Path(__file__).parent
images_dir = current_dir / "images"
app.mount("/static", StaticFiles(directory=str(images_dir)), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(brand.router)
app.include_router(merchant.router)
app.include_router(test_axione.router)

@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """Redirect root endpoint to API documentation."""
    return RedirectResponse(url="/docs") 