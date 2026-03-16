from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from bson import ObjectId
from app.database import get_db
from app.models.building import (
    BuildingCreate, BuildingUpdate, BuildingResponse,
    FloorCreate, FloorUpdate, FloorResponse,
    UnitCreate, UnitUpdate, UnitResponse,
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/buildings", tags=["buildings"])


def oid(val: str):
    try:
        return ObjectId(val)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid id: {val}")


# ─── Buildings ────────────────────────────────────────────────
async def enrich_building(db, b: dict) -> BuildingResponse:
    client = await db.clients.find_one({"_id": oid(b["client_id"])}) if b.get("client_id") else None
    return BuildingResponse(
        id=str(b["_id"]),
        client_name=client["name"] if client else None,
        **{k: v for k, v in b.items() if k != "_id"}
    )


@router.get("", response_model=List[BuildingResponse])
async def list_buildings(skip: int = 0, limit: int = 100, _=Depends(get_current_user)):
    db = get_db()
    buildings = await db.buildings.find().skip(skip).limit(limit).to_list(limit)
    return [await enrich_building(db, b) for b in buildings]


@router.post("", response_model=BuildingResponse)
async def create_building(data: BuildingCreate, _=Depends(get_current_user)):
    db = get_db()
    result = await db.buildings.insert_one(data.model_dump())
    b = await db.buildings.find_one({"_id": result.inserted_id})
    return await enrich_building(db, b)


@router.get("/{building_id}", response_model=BuildingResponse)
async def get_building(building_id: str, _=Depends(get_current_user)):
    db = get_db()
    b = await db.buildings.find_one({"_id": oid(building_id)})
    if not b:
        raise HTTPException(status_code=404, detail="Building not found")
    return await enrich_building(db, b)


@router.put("/{building_id}", response_model=BuildingResponse)
async def update_building(building_id: str, data: BuildingUpdate, _=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    await db.buildings.update_one({"_id": oid(building_id)}, {"$set": update_data})
    b = await db.buildings.find_one({"_id": oid(building_id)})
    if not b:
        raise HTTPException(status_code=404, detail="Building not found")
    return await enrich_building(db, b)


@router.delete("/{building_id}")
async def delete_building(building_id: str, _=Depends(get_current_user)):
    db = get_db()
    result = await db.buildings.delete_one({"_id": oid(building_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Building not found")
    return {"message": "Deleted successfully"}


# ─── Floors ───────────────────────────────────────────────────
@router.get("/{building_id}/floors", response_model=List[FloorResponse])
async def list_floors(building_id: str, _=Depends(get_current_user)):
    db = get_db()
    floors = await db.floors.find({"building_id": building_id}).to_list(200)
    building = await db.buildings.find_one({"_id": oid(building_id)})
    bname = building["name"] if building else None
    result = []
    for f in floors:
        result.append(FloorResponse(
            id=str(f["_id"]),
            building_name=bname,
            **{k: v for k, v in f.items() if k != "_id"}
        ))
    return result


@router.post("/{building_id}/floors", response_model=FloorResponse)
async def create_floor(building_id: str, data: FloorCreate, _=Depends(get_current_user)):
    db = get_db()
    floor_dict = data.model_dump()
    floor_dict["building_id"] = building_id
    result = await db.floors.insert_one(floor_dict)
    f = await db.floors.find_one({"_id": result.inserted_id})
    return FloorResponse(id=str(f["_id"]), **{k: v for k, v in f.items() if k != "_id"})


@router.put("/floors/{floor_id}", response_model=FloorResponse)
async def update_floor(floor_id: str, data: FloorUpdate, _=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    await db.floors.update_one({"_id": oid(floor_id)}, {"$set": update_data})
    f = await db.floors.find_one({"_id": oid(floor_id)})
    if not f:
        raise HTTPException(status_code=404, detail="Floor not found")
    return FloorResponse(id=str(f["_id"]), **{k: v for k, v in f.items() if k != "_id"})


@router.delete("/floors/{floor_id}")
async def delete_floor(floor_id: str, _=Depends(get_current_user)):
    db = get_db()
    result = await db.floors.delete_one({"_id": oid(floor_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Floor not found")
    return {"message": "Deleted successfully"}


# ─── Units ────────────────────────────────────────────────────
@router.get("/{building_id}/units", response_model=List[UnitResponse])
async def list_units(building_id: str, floor_id: Optional[str] = None, _=Depends(get_current_user)):
    db = get_db()
    query = {"building_id": building_id}
    if floor_id:
        query["floor_id"] = floor_id
    units = await db.units.find(query).to_list(500)
    building = await db.buildings.find_one({"_id": oid(building_id)})
    bname = building["name"] if building else None
    result = []
    for u in units:
        floor = await db.floors.find_one({"_id": oid(u["floor_id"])}) if u.get("floor_id") else None
        result.append(UnitResponse(
            id=str(u["_id"]),
            building_name=bname,
            floor_name=floor["name"] if floor else None,
            **{k: v for k, v in u.items() if k != "_id"}
        ))
    return result


@router.post("/{building_id}/units", response_model=UnitResponse)
async def create_unit(building_id: str, data: UnitCreate, _=Depends(get_current_user)):
    db = get_db()
    unit_dict = data.model_dump()
    unit_dict["building_id"] = building_id
    result = await db.units.insert_one(unit_dict)
    u = await db.units.find_one({"_id": result.inserted_id})
    return UnitResponse(id=str(u["_id"]), **{k: v for k, v in u.items() if k != "_id"})


@router.put("/units/{unit_id}", response_model=UnitResponse)
async def update_unit(unit_id: str, data: UnitUpdate, _=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    await db.units.update_one({"_id": oid(unit_id)}, {"$set": update_data})
    u = await db.units.find_one({"_id": oid(unit_id)})
    if not u:
        raise HTTPException(status_code=404, detail="Unit not found")
    return UnitResponse(id=str(u["_id"]), **{k: v for k, v in u.items() if k != "_id"})


@router.delete("/units/{unit_id}")
async def delete_unit(unit_id: str, _=Depends(get_current_user)):
    db = get_db()
    result = await db.units.delete_one({"_id": oid(unit_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Unit not found")
    return {"message": "Deleted successfully"}
