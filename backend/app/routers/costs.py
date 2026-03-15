from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from bson import ObjectId
from app.database import get_db
from app.models.cost import CostCreate, CostUpdate, CostResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/costs", tags=["costs"])


def oid(val: str):
    try:
        return ObjectId(val)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid id: {val}")


async def enrich(db, c: dict) -> CostResponse:
    building = await db.buildings.find_one({"_id": oid(c["building_id"])}) if c.get("building_id") else None
    vendor = await db.vendors.find_one({"_id": oid(c["vendor_id"])}) if c.get("vendor_id") else None
    return CostResponse(
        id=str(c["_id"]),
        building_name=building["name"] if building else None,
        vendor_name=vendor["name"] if vendor else None,
        **{k: v for k, v in c.items() if k != "_id"}
    )


@router.get("", response_model=List[CostResponse])
async def list_costs(
    skip: int = 0, limit: int = 100,
    building_id: Optional[str] = None,
    category: Optional[str] = None,
    _=Depends(get_current_user)
):
    db = get_db()
    query = {}
    if building_id:
        query["building_id"] = building_id
    if category:
        query["category"] = category
    costs = await db.costs.find(query).sort("date", -1).skip(skip).limit(limit).to_list(limit)
    return [await enrich(db, c) for c in costs]


@router.post("", response_model=CostResponse)
async def create_cost(data: CostCreate, _=Depends(get_current_user)):
    db = get_db()
    result = await db.costs.insert_one(data.model_dump())
    c = await db.costs.find_one({"_id": result.inserted_id})
    return await enrich(db, c)


@router.get("/{cost_id}", response_model=CostResponse)
async def get_cost(cost_id: str, _=Depends(get_current_user)):
    db = get_db()
    c = await db.costs.find_one({"_id": oid(cost_id)})
    if not c:
        raise HTTPException(status_code=404, detail="Cost record not found")
    return await enrich(db, c)


@router.put("/{cost_id}", response_model=CostResponse)
async def update_cost(cost_id: str, data: CostUpdate, _=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    await db.costs.update_one({"_id": oid(cost_id)}, {"$set": update_data})
    c = await db.costs.find_one({"_id": oid(cost_id)})
    if not c:
        raise HTTPException(status_code=404, detail="Cost record not found")
    return await enrich(db, c)


@router.delete("/{cost_id}")
async def delete_cost(cost_id: str, _=Depends(get_current_user)):
    db = get_db()
    result = await db.costs.delete_one({"_id": oid(cost_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cost record not found")
    return {"message": "Deleted successfully"}


@router.get("/summary/monthly")
async def monthly_summary(year: int, building_id: Optional[str] = None, _=Depends(get_current_user)):
    db = get_db()
    match = {"date": {"$regex": f"^{year}"}}
    if building_id:
        match["building_id"] = building_id
    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": {"month": {"$substr": ["$date", 5, 2]}, "category": "$category"},
            "total": {"$sum": "$amount"}
        }},
        {"$sort": {"_id.month": 1}}
    ]
    results = await db.costs.aggregate(pipeline).to_list(200)
    return results
