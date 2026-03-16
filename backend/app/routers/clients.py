from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from app.database import get_db
from app.models.client import ClientCreate, ClientUpdate, ClientResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/clients", tags=["clients"])


def oid(val: str):
    try:
        return ObjectId(val)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid id: {val}")


def to_response(c: dict) -> ClientResponse:
    return ClientResponse(id=str(c["_id"]), **{k: v for k, v in c.items() if k != "_id"})


@router.get("", response_model=List[ClientResponse])
async def list_clients(skip: int = 0, limit: int = 100, _=Depends(get_current_user)):
    db = get_db()
    clients = await db.clients.find().skip(skip).limit(limit).to_list(limit)
    return [to_response(c) for c in clients]


@router.post("", response_model=ClientResponse)
async def create_client(data: ClientCreate, _=Depends(get_current_user)):
    db = get_db()
    result = await db.clients.insert_one(data.model_dump())
    c = await db.clients.find_one({"_id": result.inserted_id})
    return to_response(c)


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str, _=Depends(get_current_user)):
    db = get_db()
    c = await db.clients.find_one({"_id": oid(client_id)})
    if not c:
        raise HTTPException(status_code=404, detail="Client not found")
    return to_response(c)


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(client_id: str, data: ClientUpdate, _=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    await db.clients.update_one({"_id": oid(client_id)}, {"$set": update_data})
    c = await db.clients.find_one({"_id": oid(client_id)})
    if not c:
        raise HTTPException(status_code=404, detail="Client not found")
    return to_response(c)


@router.delete("/{client_id}")
async def delete_client(client_id: str, _=Depends(get_current_user)):
    db = get_db()
    result = await db.clients.delete_one({"_id": oid(client_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Deleted successfully"}
