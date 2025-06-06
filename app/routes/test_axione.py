from datetime import datetime, timezone
from enum import Enum
from typing import List  # noqa: UP035
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.core.database import get_database


class TicketStatus(str, Enum):
    open = "open"
    stalled = "stalled"
    closed = "closed"

class TicketCreate(BaseModel):
    title: str
    description: str
    status: TicketStatus = TicketStatus.open  # Default to "open"

class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TicketStatus | None = None

class Ticket(BaseModel):
    id: UUID
    title: str
    description: str
    status: TicketStatus
    created_at: datetime

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/", response_model=List[Ticket], status_code=status.HTTP_201_CREATED)  # noqa: UP006
async def create_tickets(
    tickets: list[TicketCreate],
    db: AsyncIOMotorDatabase = Depends(get_database),  # noqa: B008
    user: dict = Depends(get_current_user),  # noqa: B008
):
    created = []
    for ticket in tickets:
        ticket_id = uuid4()
        ticket_doc = {
            "id": str(ticket_id),
            "title": ticket.title,
            "description": ticket.description,
            "status": ticket.status.value,
            "created_at": datetime.now(timezone.utc),
        }
        await db["tickets"].insert_one(ticket_doc)
        created.append(Ticket(**{**ticket_doc, "id": ticket_id}))
    return created

@router.get("/", response_model=list[Ticket])
async def list_tickets(
    db: AsyncIOMotorDatabase = Depends(get_database),  # noqa: B008
    title: str | None = Query(None, description="Filter by title substring"),
    status: TicketStatus | None = Query(None, description="Filter by status"),  # noqa: B008
    limit: int = Query(20, ge=1, le=100, description="Max items to return"),
):
    query = {}
    if title:
        query["title"] = {"$regex": title, "$options": "i"}
    if status:
        query["status"] = status.value

    cursor = db["tickets"].find(query).limit(limit)
    tickets = [Ticket(**{**doc, "id": UUID(doc["id"])}) async for doc in cursor]
    return tickets

@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: UUID,
    db: AsyncIOMotorDatabase = Depends(get_database),  # noqa: B008
    user: dict = Depends(get_current_user),  # noqa: B008
):
    doc = await db["tickets"].find_one({"id": str(ticket_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return Ticket(**{**doc, "id": UUID(doc["id"])})

@router.put("/{ticket_id}", response_model=Ticket)
async def update_ticket(
    ticket_id: UUID,
    update: TicketUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),  # noqa: B008
    user: dict = Depends(get_current_user),  # noqa: B008
):
    update_data = {k: v for k, v in update.model_dump(exclude_unset=True).items() if v is not None}  # noqa: E501
    if update_data:
        result = await db["tickets"].update_one(
            {"id": str(ticket_id)},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Ticket not found")
    doc = await db["tickets"].find_one({"id": str(ticket_id)})
    return Ticket(**{**doc, "id": UUID(doc["id"])})

@router.patch("/{ticket_id}/close", response_model=Ticket)
async def close_ticket(
    ticket_id: UUID,
    db: AsyncIOMotorDatabase = Depends(get_database),  # noqa: B008
    user: dict = Depends(get_current_user),  # noqa: B008
):
    result = await db["tickets"].update_one(
        {"id": str(ticket_id)},
        {"$set": {"status": TicketStatus.closed.value}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    doc = await db["tickets"].find_one({"id": str(ticket_id)})
    return Ticket(**{**doc, "id": UUID(doc["id"])}) 