from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from bson import ObjectId
from app.database import get_db
from app.models.roster import RosterCreate, RosterUpdate, RosterResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/roster", tags=["roster"])


def oid(val: str):
    try:
        return ObjectId(val)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid id: {val}")


async def enrich(db, r: dict) -> RosterResponse:
    building = await db.buildings.find_one({"_id": oid(r["building_id"])}) if r.get("building_id") else None
    officer_names = []
    for uid in r.get("assigned_officer_ids", []):
        try:
            u = await db.users.find_one({"_id": oid(uid)})
            if u:
                officer_names.append(u["name"])
        except Exception:
            pass
    contract = await db.contracts.find_one({"_id": oid(r["contract_id"])}) if r.get("contract_id") else None
    return RosterResponse(
        id=str(r["_id"]),
        building_name=building["name"] if building else None,
        officer_names=officer_names,
        contract_number=contract["contract_number"] if contract else None,
        **{k: v for k, v in r.items() if k != "_id"}
    )


@router.get("", response_model=List[RosterResponse])
async def list_roster(
    skip: int = 0, limit: int = 100,
    building_id: Optional[str] = None,
    date: Optional[str] = None,
    _=Depends(get_current_user)
):
    db = get_db()
    query = {}
    if building_id:
        query["building_id"] = building_id
    if date:
        query["date"] = date
    items = await db.roster.find(query).sort("date", -1).skip(skip).limit(limit).to_list(limit)
    return [await enrich(db, r) for r in items]


@router.post("", response_model=RosterResponse)
async def create_roster(data: RosterCreate, _=Depends(get_current_user)):
    db = get_db()
    result = await db.roster.insert_one(data.model_dump())
    r = await db.roster.find_one({"_id": result.inserted_id})
    return await enrich(db, r)


@router.put("/{roster_id}", response_model=RosterResponse)
async def update_roster(roster_id: str, data: RosterUpdate, _=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    await db.roster.update_one({"_id": oid(roster_id)}, {"$set": update_data})
    r = await db.roster.find_one({"_id": oid(roster_id)})
    if not r:
        raise HTTPException(status_code=404, detail="Roster not found")
    return await enrich(db, r)


@router.delete("/{roster_id}")
async def delete_roster(roster_id: str, _=Depends(get_current_user)):
    db = get_db()
    result = await db.roster.delete_one({"_id": oid(roster_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Roster not found")
    return {"message": "Deleted successfully"}
