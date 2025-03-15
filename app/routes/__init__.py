from fastapi import APIRouter
from app.routes import brand
from app.routes import auth
from app.routes import merchant
router = APIRouter()


router.include_router(auth.router)
router.include_router(brand.router)
router.include_router(merchant.router)
