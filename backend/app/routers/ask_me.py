import json
import asyncio
import os
from typing import List, Optional

import pymongo
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/ask", tags=["ask"])

# ---------------------------------------------------------------------------
# Lazy sync PyMongo client (thread-safe, reused across requests)
# ---------------------------------------------------------------------------
_sync_client: Optional[pymongo.MongoClient] = None


def _get_sync_db():
    global _sync_client
    if _sync_client is None:
        _sync_client = pymongo.MongoClient(settings.mongodb_url)
    return _sync_client[settings.database_name]


def _serialize(docs: list) -> str:
    """Convert a list of MongoDB documents to a JSON string."""
    return json.dumps(docs, default=str)


# ---------------------------------------------------------------------------
# Strands tools – one per domain
# ---------------------------------------------------------------------------
def _make_tools():
    """Import strands here so startup is not blocked if package is absent."""
    from strands import tool  # noqa: PLC0415

    @tool
    def query_cleaning_schedules(status: Optional[str] = None, limit: int = 20) -> str:
        """Query cleaning schedules from the database.
        Optionally filter by status: pending, in_progress, completed, cancelled.
        Returns a JSON list of cleaning schedule records."""
        db = _get_sync_db()
        query: dict = {}
        if status:
            query["status"] = status
        docs = list(db.cleaning_schedules.find(query, {"_id": 0}).limit(limit))
        return _serialize(docs)

    @tool
    def query_preventive_maintenance(
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> str:
        """Query preventive maintenance records.
        Filter by status (scheduled, in_progress, completed, overdue, cancelled)
        or category (electrical, plumbing, hvac, elevator, fire_safety, general, structural).
        Returns a JSON list."""
        db = _get_sync_db()
        query: dict = {}
        if status:
            query["status"] = status
        if category:
            query["category"] = category
        docs = list(db.preventive_maintenance.find(query, {"_id": 0}).limit(limit))
        return _serialize(docs)

    @tool
    def query_security_roster(limit: int = 20) -> str:
        """Query security roster / shift schedule from the database.
        Returns a JSON list of roster entries."""
        db = _get_sync_db()
        docs = list(db.roster.find({}, {"_id": 0}).sort("date", -1).limit(limit))
        return _serialize(docs)

    @tool
    def query_cases(
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> str:
        """Query cases and calls from the database.
        Filter by status (open, in_progress, resolved, closed),
        priority (low, medium, high, critical),
        or category (complaint, request, emergency, inquiry, other).
        Returns a JSON list sorted by newest first."""
        db = _get_sync_db()
        query: dict = {}
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        if category:
            query["category"] = category
        docs = list(db.cases.find(query, {"_id": 0}).sort("created_at", -1).limit(limit))
        return _serialize(docs)

    @tool
    def query_corrective_maintenance(
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> str:
        """Query corrective maintenance records (reactive repairs).
        Filter by status or category (electrical, plumbing, hvac, elevator, fire_safety, general, structural).
        Returns a JSON list."""
        db = _get_sync_db()
        query: dict = {}
        if status:
            query["status"] = status
        if category:
            query["category"] = category
        docs = list(db.corrective_maintenance.find(query, {"_id": 0}).limit(limit))
        return _serialize(docs)

    @tool
    def query_vendors(limit: int = 20) -> str:
        """Query vendors and service providers from the database.
        Returns a JSON list of vendor records."""
        db = _get_sync_db()
        docs = list(db.vendors.find({}, {"_id": 0}).limit(limit))
        return _serialize(docs)

    @tool
    def query_customers(limit: int = 20) -> str:
        """Query customers / clients from the database.
        Returns a JSON list of client records."""
        db = _get_sync_db()
        docs = list(db.clients.find({}, {"_id": 0}).limit(limit))
        return _serialize(docs)

    @tool
    def query_contracts(status: Optional[str] = None, limit: int = 20) -> str:
        """Query contracts from the database.
        Optionally filter by status (active, expired, pending, terminated).
        Returns a JSON list of contract records."""
        db = _get_sync_db()
        query: dict = {}
        if status:
            query["status"] = status
        docs = list(db.contracts.find(query, {"_id": 0}).limit(limit))
        return _serialize(docs)

    @tool
    def query_buildings(limit: int = 20) -> str:
        """Query buildings managed in the system.
        Returns a JSON list of building records including name, address, status."""
        db = _get_sync_db()
        docs = list(db.buildings.find({}, {"_id": 0}).limit(limit))
        return _serialize(docs)

    return [
        query_cleaning_schedules,
        query_preventive_maintenance,
        query_security_roster,
        query_cases,
        query_corrective_maintenance,
        query_vendors,
        query_customers,
        query_contracts,
        query_buildings,
    ]


SYSTEM_PROMPT = """You are a helpful facility management assistant for Resolve.AI.
You have access to the facility management database and can answer questions about:
- Cleaning schedules
- Preventive maintenance
- Security roster
- Cases and calls (complaints, requests, emergencies)
- Corrective maintenance (reactive repairs)
- Vendors and service providers
- Customers / clients
- Contracts
- Buildings

Always use the available tools to fetch up-to-date data before answering.
Be concise, professional, and helpful. Format your responses clearly."""


def _run_agent(question: str) -> str:
    """Synchronous function that runs the Strands agent. Intended to be called
    in a thread pool from the async FastAPI handler."""
    from strands import Agent  # noqa: PLC0415
    from strands.models.litellm import LiteLLMModel  # noqa: PLC0415

    api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured. "
            "Set it in the .env file or as an environment variable."
        )

    # LiteLLM picks up GEMINI_API_KEY from the environment automatically
    os.environ["GEMINI_API_KEY"] = api_key

    model = LiteLLMModel(model_id=settings.ask_me_model)

    agent = Agent(
        model=model,
        tools=_make_tools(),
        system_prompt=SYSTEM_PROMPT,
    )

    result = agent(question)
    return str(result)


# ---------------------------------------------------------------------------
# API schema
# ---------------------------------------------------------------------------
class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@router.post("", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    current_user: dict = Depends(get_current_user),
):
    """Ask the AI agent anything about facility management data."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    loop = asyncio.get_event_loop()
    try:
        answer = await loop.run_in_executor(None, _run_agent, request.question.strip())
        return AskResponse(answer=answer)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(exc)}",
        ) from exc
