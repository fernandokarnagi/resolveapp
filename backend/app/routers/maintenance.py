from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from bson import ObjectId
from app.database import get_db
from app.models.maintenance import (
    PreventiveMaintenanceCreate, PreventiveMaintenanceUpdate, PreventiveMaintenanceResponse,
    CorrectiveMaintenanceCreate, CorrectiveMaintenanceUpdate, CorrectiveMaintenanceResponse,
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


def oid(val: str):
    try:
        return ObjectId(val)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid id: {val}")


async def enrich_pm(db, m: dict) -> PreventiveMaintenanceResponse:
    building = await db.buildings.find_one({"_id": oid(m["building_id"])}) if m.get("building_id") else None
    vendor = await db.vendors.find_one({"_id": oid(m["assigned_vendor_id"])}) if m.get("assigned_vendor_id") else None
    return PreventiveMaintenanceResponse(
        id=str(m["_id"]),
        building_name=building["name"] if building else None,
        vendor_name=vendor["name"] if vendor else None,
        **{k: v for k, v in m.items() if k != "_id"}
    )


async def enrich_cm(db, m: dict) -> CorrectiveMaintenanceResponse:
    building = await db.buildings.find_one({"_id": oid(m["building_id"])}) if m.get("building_id") else None
    vendor = await db.vendors.find_one({"_id": oid(m["assigned_vendor_id"])}) if m.get("assigned_vendor_id") else None
    return CorrectiveMaintenanceResponse(
        id=str(m["_id"]),
        building_name=building["name"] if building else None,
        vendor_name=vendor["name"] if vendor else None,
        **{k: v for k, v in m.items() if k != "_id"}
    )


# ─── Preventive Maintenance ───────────────────────────────────
@router.get("/preventive", response_model=List[PreventiveMaintenanceResponse])
async def list_pm(skip: int = 0, limit: int = 100, building_id: Optional[str] = None, status: Optional[str] = None, _=Depends(get_current_user)):
    db = get_db()
    query = {}
    if building_id:
        query["building_id"] = building_id
    if status:
        query["status"] = status
    items = await db.preventive_maintenance.find(query).skip(skip).limit(limit).to_list(limit)
    return [await enrich_pm(db, m) for m in items]


@router.post("/preventive", response_model=PreventiveMaintenanceResponse)
async def create_pm(data: PreventiveMaintenanceCreate, _=Depends(get_current_user)):
    db = get_db()
    result = await db.preventive_maintenance.insert_one(data.model_dump())
    m = await db.preventive_maintenance.find_one({"_id": result.inserted_id})
    return await enrich_pm(db, m)


@router.put("/preventive/{pm_id}", response_model=PreventiveMaintenanceResponse)
async def update_pm(pm_id: str, data: PreventiveMaintenanceUpdate, _=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    await db.preventive_maintenance.update_one({"_id": oid(pm_id)}, {"$set": update_data})
    m = await db.preventive_maintenance.find_one({"_id": oid(pm_id)})
    if not m:
        raise HTTPException(status_code=404, detail="Record not found")
    return await enrich_pm(db, m)


@router.delete("/preventive/{pm_id}")
async def delete_pm(pm_id: str, _=Depends(get_current_user)):
    db = get_db()
    result = await db.preventive_maintenance.delete_one({"_id": oid(pm_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Deleted successfully"}


# ─── Corrective Maintenance ───────────────────────────────────
@router.get("/corrective", response_model=List[CorrectiveMaintenanceResponse])
async def list_cm(skip: int = 0, limit: int = 100, building_id: Optional[str] = None, status: Optional[str] = None, _=Depends(get_current_user)):
    db = get_db()
    query = {}
    if building_id:
        query["building_id"] = building_id
    if status:
        query["status"] = status
    items = await db.corrective_maintenance.find(query).skip(skip).limit(limit).to_list(limit)
    return [await enrich_cm(db, m) for m in items]


@router.post("/corrective", response_model=CorrectiveMaintenanceResponse)
async def create_cm(data: CorrectiveMaintenanceCreate, _=Depends(get_current_user)):
    db = get_db()
    result = await db.corrective_maintenance.insert_one(data.model_dump())
    m = await db.corrective_maintenance.find_one({"_id": result.inserted_id})
    return await enrich_cm(db, m)


@router.put("/corrective/{cm_id}", response_model=CorrectiveMaintenanceResponse)
async def update_cm(cm_id: str, data: CorrectiveMaintenanceUpdate, _=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    await db.corrective_maintenance.update_one({"_id": oid(cm_id)}, {"$set": update_data})
    m = await db.corrective_maintenance.find_one({"_id": oid(cm_id)})
    if not m:
        raise HTTPException(status_code=404, detail="Record not found")
    return await enrich_cm(db, m)


@router.delete("/corrective/{cm_id}")
async def delete_cm(cm_id: str, _=Depends(get_current_user)):
    db = get_db()
    result = await db.corrective_maintenance.delete_one({"_id": oid(cm_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Deleted successfully"}
