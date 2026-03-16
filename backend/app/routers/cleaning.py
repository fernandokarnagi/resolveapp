from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from bson import ObjectId
from app.database import get_db
from app.models.cleaning import CleaningScheduleCreate, CleaningScheduleUpdate, CleaningScheduleResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/cleaning", tags=["cleaning"])


def oid(val: str):
    try:
        return ObjectId(val)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid id: {val}")


async def enrich(db, s: dict) -> CleaningScheduleResponse:
    building = await db.buildings.find_one({"_id": oid(s["building_id"])}) if s.get("building_id") else None
    vendor = await db.vendors.find_one({"_id": oid(s["assigned_vendor_id"])}) if s.get("assigned_vendor_id") else None
    contract = await db.contracts.find_one({"_id": oid(s["contract_id"])}) if s.get("contract_id") else None
    return CleaningScheduleResponse(
        id=str(s["_id"]),
        building_name=building["name"] if building else None,
        vendor_name=vendor["name"] if vendor else None,
        contract_number=contract["contract_number"] if contract else None,
        **{k: v for k, v in s.items() if k != "_id"}
    )


@router.get("", response_model=List[CleaningScheduleResponse])
async def list_schedules(skip: int = 0, limit: int = 100, building_id: Optional[str] = None, _=Depends(get_current_user)):
    db = get_db()
    query = {}
    if building_id:
        query["building_id"] = building_id
    schedules = await db.cleaning_schedules.find(query).skip(skip).limit(limit).to_list(limit)
    return [await enrich(db, s) for s in schedules]


@router.post("", response_model=CleaningScheduleResponse)
async def create_schedule(data: CleaningScheduleCreate, _=Depends(get_current_user)):
    db = get_db()
    result = await db.cleaning_schedules.insert_one(data.model_dump())
    s = await db.cleaning_schedules.find_one({"_id": result.inserted_id})
    return await enrich(db, s)


@router.get("/{schedule_id}", response_model=CleaningScheduleResponse)
async def get_schedule(schedule_id: str, _=Depends(get_current_user)):
    db = get_db()
    s = await db.cleaning_schedules.find_one({"_id": oid(schedule_id)})
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return await enrich(db, s)


@router.put("/{schedule_id}", response_model=CleaningScheduleResponse)
async def update_schedule(schedule_id: str, data: CleaningScheduleUpdate, _=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    await db.cleaning_schedules.update_one({"_id": oid(schedule_id)}, {"$set": update_data})
    s = await db.cleaning_schedules.find_one({"_id": oid(schedule_id)})
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return await enrich(db, s)


@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: str, _=Depends(get_current_user)):
    db = get_db()
    result = await db.cleaning_schedules.delete_one({"_id": oid(schedule_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"message": "Deleted successfully"}
