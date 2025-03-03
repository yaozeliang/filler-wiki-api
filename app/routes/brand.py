from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse, StreamingResponse
import pandas as pd
import io
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.crud import MongoManager
from app.core.schemas import BrandResponseModel
from app.core.database import get_database
from app.core.enums import ExportFormat
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from app.core.logging import logger
from app.core.auth import get_current_user
from app.core.models.user import UserInDB

router = APIRouter(prefix="/brands", tags=["Brands"])

@router.get("/", response_model=BrandResponseModel[List[Dict[Any, Any]]])
async def get_brands(
    current_user: UserInDB = Depends(get_current_user),
    name: str = None,
    export_as: Optional[ExportFormat] = Query(
        ExportFormat.JSON,
        description="Export format: json, csv, or excel"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Items per page"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    logger.info(f"User {current_user.username} accessing brands endpoint")
    try:
        logger.info(f"Fetching brands - Page: {page}, Size: {page_size}, Filter: {name}, Format: {export_as}")
        
        # Calculate skip based on page and page_size
        skip: int = (page - 1) * page_size
        limit: int = page_size
        
        crud = MongoManager("brand")
        
        # Get total count for pagination metadata
        total_count = await crud.count(db, name)
        logger.info(f"Total brands count: {total_count}")
        
        # Get paginated data
        brands = await crud.get_all(db, name, limit=limit, skip=skip)
        
        # Add pagination metadata
        pagination = {
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "pages": (total_count + page_size - 1) // page_size
        }
        
        # Early return for standard JSON response with pagination
        if export_as == ExportFormat.JSON:
            logger.info(f"Returning JSON response with {len(brands)} brands")
            return BrandResponseModel(
                data=brands,
                pagination=pagination
            )

        # For exports, get all data
        if export_as != ExportFormat.JSON:
            logger.info(f"Preparing {export_as.value} export")
            all_brands = await crud.get_all(db, name, limit=10000)
            df = pd.DataFrame(all_brands)
            
            # Add export filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_base = f"brands_{timestamp}"
            
            if export_as == ExportFormat.CSV:
                logger.info("Generating CSV export")
                output = io.StringIO()
                df.to_csv(output, index=False)
                output.seek(0)
                return StreamingResponse(
                    output,
                    media_type="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={filename_base}.csv"}
                )
                
            elif export_as == ExportFormat.EXCEL:
                logger.info("Generating Excel export")
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Brands')
                output.seek(0)
                return StreamingResponse(
                    output,
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f"attachment; filename={filename_base}.xlsx"}
                )

    except Exception as e:
        logger.error(f"Error fetching brands: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to fetch brands: {str(e)}"}
        )