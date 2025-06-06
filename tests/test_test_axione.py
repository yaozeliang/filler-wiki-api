from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest  # type: ignore

from app.routes import test_axione
from app.routes.test_axione import TicketCreate, TicketStatus, TicketUpdate


@pytest.fixture
def mock_db():
    class MockCollection:
        def __init__(self):
            self.docs = []
        async def insert_one(self, doc):
            self.docs.append(doc)
        def find(self, query):
            class Cursor:
                def __init__(self, docs):
                    self.docs = docs
                def limit(self, n):
                    self.docs = self.docs[:n]
                    return self
                async def __aiter__(self):
                    for doc in self.docs:
                        yield doc
            filtered = self.docs
            if "title" in query:
                filtered = [d for d in filtered if query["title"]["$regex"].lower() in d["title"].lower()]  # noqa: E501
            if "status" in query:
                filtered = [d for d in filtered if d["status"] == query["status"]]
            return Cursor(filtered)
        async def find_one(self, query):
            for doc in self.docs:
                if doc["id"] == query["id"]:
                    return doc
            return None
        async def update_one(self, query, update):
            for doc in self.docs:
                if doc["id"] == query["id"]:
                    doc.update(update["$set"])
                    class Result: matched_count = 1
                    return Result()
            class Result: matched_count = 0
            return Result()
    class MockDB(dict):
        def __getitem__(self, item):
            if item not in self:
                self[item] = MockCollection()
            return dict.__getitem__(self, item)
    return MockDB()

@pytest.mark.asyncio
async def test_create_tickets(mock_db):
    tickets = [
        TicketCreate(title="Incident 1", description="Desc 1"),
        TicketCreate(title="Incident 2", description="Desc 2", status=TicketStatus.stalled)
    ]
    user = {}  # noqa: F841, RUF100
    result = await test_axione.create_tickets(tickets, db=mock_db, user=user)
    assert len(result) == 2
    assert result[0].title == "Incident 1"
    assert result[1].status == TicketStatus.stalled

@pytest.mark.asyncio
async def test_list_tickets(mock_db):
    ticket_id = str(uuid4())
    mock_db["tickets"].docs.append({
        "id": ticket_id,
        "title": "Incident fibre",
        "description": "Coupure",
        "status": "open",
        "created_at": datetime.now(timezone.utc)
    })
    tickets = await test_axione.list_tickets(db=mock_db, title=None, status=None, limit=10)
    assert len(tickets) == 1
    assert tickets[0].id == UUID(ticket_id)

@pytest.mark.asyncio
async def test_list_tickets_with_filter(mock_db):
    mock_db["tickets"].docs.append({
        "id": str(uuid4()),
        "title": "Incident wifi",
        "description": "Wifi down",
        "status": "open",
        "created_at": datetime.now(timezone.utc)
    })
    mock_db["tickets"].docs.append({
        "id": str(uuid4()),
        "title": "Incident fibre",
        "description": "Fibre down",
        "status": "closed",
        "created_at": datetime.now(timezone.utc)
    })
    user = {}  # noqa: F841, RUF100
    tickets = await test_axione.list_tickets(db=mock_db, title="wifi", status=None, limit=10)
    assert len(tickets) == 1
    assert "wifi" in tickets[0].title.lower()
    tickets = await test_axione.list_tickets(db=mock_db, title=None, status=TicketStatus.closed, limit=10)
    assert len(tickets) == 1
    assert tickets[0].status == TicketStatus.closed

@pytest.mark.asyncio
async def test_get_ticket(mock_db):
    ticket_id = str(uuid4())
    mock_db["tickets"].docs.append({
        "id": ticket_id,
        "title": "Incident",
        "description": "Desc",
        "status": "open",
        "created_at": datetime.now(timezone.utc)
    })
    user = {}  # noqa: F841, RUF100
    ticket = await test_axione.get_ticket(ticket_id=UUID(ticket_id), db=mock_db, user=user)
    assert ticket.id == UUID(ticket_id)
    assert ticket.title == "Incident"

@pytest.mark.asyncio
async def test_update_ticket(mock_db):
    ticket_id = str(uuid4())
    mock_db["tickets"].docs.append({
        "id": ticket_id,
        "title": "Old",
        "description": "Old desc",
        "status": "open",
        "created_at": datetime.now(timezone.utc)
    })
    user = {}  # noqa: F841, RUF100
    update = TicketUpdate(title="New", description="New desc", status=TicketStatus.closed)
    ticket = await test_axione.update_ticket(ticket_id=UUID(ticket_id), update=update, db=mock_db, user=user)  # noqa: E501
    assert ticket.title == "New"
    assert ticket.status == TicketStatus.closed

@pytest.mark.asyncio
async def test_close_ticket(mock_db):
    ticket_id = str(uuid4())
    mock_db["tickets"].docs.append({
        "id": ticket_id,
        "title": "To close",
        "description": "Desc",
        "status": "open",
        "created_at": datetime.now(timezone.utc)
    })
    user = {}  # noqa: F841, RUF100 
    ticket = await test_axione.close_ticket(ticket_id=UUID(ticket_id), db=mock_db, user=user)  # noqa: E501
    assert ticket.status == TicketStatus.closed
