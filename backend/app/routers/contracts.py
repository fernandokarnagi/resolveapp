from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from bson import ObjectId
from app.database import get_db
from app.models.contract import ContractCreate, ContractUpdate, ContractResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/contracts", tags=["contracts"])


def oid(val: str):
    try:
        return ObjectId(val)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid id: {val}")


async def enrich(db, c: dict) -> ContractResponse:
    client = await db.clients.find_one({"_id": oid(c["client_id"])}) if c.get("client_id") else None
    building_names = []
    for bid in (c.get("building_ids") or []):
        try:
            b = await db.buildings.find_one({"_id": oid(bid)})
            if b:
                building_names.append(b["name"])
        except Exception:
            pass
    return ContractResponse(
        id=str(c["_id"]),
        client_name=client["name"] if client else None,
        building_names=building_names,
        **{k: v for k, v in c.items() if k != "_id"}
    )


@router.get("", response_model=List[ContractResponse])
async def list_contracts(
    skip: int = 0, limit: int = 100,
    client_id: Optional[str] = None,
    _=Depends(get_current_user)
):
    db = get_db()
    query = {}
    if client_id:
        query["client_id"] = client_id
    contracts = await db.contracts.find(query).skip(skip).limit(limit).to_list(limit)
    return [await enrich(db, c) for c in contracts]


@router.post("", response_model=ContractResponse)
async def create_contract(data: ContractCreate, _=Depends(get_current_user)):
    db = get_db()
    result = await db.contracts.insert_one(data.model_dump())
    c = await db.contracts.find_one({"_id": result.inserted_id})
    return await enrich(db, c)


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(contract_id: str, _=Depends(get_current_user)):
    db = get_db()
    c = await db.contracts.find_one({"_id": oid(contract_id)})
    if not c:
        raise HTTPException(status_code=404, detail="Contract not found")
    return await enrich(db, c)


@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(contract_id: str, data: ContractUpdate, _=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    await db.contracts.update_one({"_id": oid(contract_id)}, {"$set": update_data})
    c = await db.contracts.find_one({"_id": oid(contract_id)})
    if not c:
        raise HTTPException(status_code=404, detail="Contract not found")
    return await enrich(db, c)


@router.delete("/{contract_id}")
async def delete_contract(contract_id: str, _=Depends(get_current_user)):
    db = get_db()
    result = await db.contracts.delete_one({"_id": oid(contract_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contract not found")
    return {"message": "Deleted successfully"}
