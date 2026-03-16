from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timezone
from app.database import get_db
from app.models.case import CaseCreate, CaseUpdate, CaseResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/cases", tags=["cases"])


def oid(val: str):
    try:
        return ObjectId(val)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid id: {val}")


async def generate_case_number(db) -> str:
    now = datetime.now(timezone.utc)
    prefix = f"CASE-{now.strftime('%Y%m')}-"
    count = await db.cases.count_documents({"case_number": {"$regex": f"^{prefix}"}})
    return f"{prefix}{str(count + 1).zfill(4)}"


async def enrich(db, c: dict) -> CaseResponse:
    building = await db.buildings.find_one({"_id": oid(c["building_id"])}) if c.get("building_id") else None
    floor = await db.floors.find_one({"_id": oid(c["floor_id"])}) if c.get("floor_id") else None
    unit = await db.units.find_one({"_id": oid(c["unit_id"])}) if c.get("unit_id") else None
    contract = await db.contracts.find_one({"_id": oid(c["contract_id"])}) if c.get("contract_id") else None
    return CaseResponse(
        id=str(c["_id"]),
        building_name=building["name"] if building else None,
        floor_name=floor["name"] if floor else None,
        unit_number=unit["unit_number"] if unit else None,
        contract_number=contract["contract_number"] if contract else None,
        created_at=c.get("created_at"),
        updated_at=c.get("updated_at"),
        **{k: v for k, v in c.items() if k not in ("_id", "created_at", "updated_at")}
    )


@router.get("", response_model=List[CaseResponse])
async def list_cases(
    skip: int = 0, limit: int = 100,
    building_id: Optional[str] = None,
    status: Optional[str] = None,
    _=Depends(get_current_user)
):
    db = get_db()
    query = {}
    if building_id:
        query["building_id"] = building_id
    if status:
        query["status"] = status
    cases = await db.cases.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return [await enrich(db, c) for c in cases]


@router.post("", response_model=CaseResponse)
async def create_case(data: CaseCreate, _=Depends(get_current_user)):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    case_dict = data.model_dump()
    case_dict["case_number"] = await generate_case_number(db)
    case_dict["created_at"] = now
    case_dict["updated_at"] = now
    result = await db.cases.insert_one(case_dict)
    c = await db.cases.find_one({"_id": result.inserted_id})
    return await enrich(db, c)


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(case_id: str, _=Depends(get_current_user)):
    db = get_db()
    c = await db.cases.find_one({"_id": oid(case_id)})
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    return await enrich(db, c)


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(case_id: str, data: CaseUpdate, _=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.cases.update_one({"_id": oid(case_id)}, {"$set": update_data})
    c = await db.cases.find_one({"_id": oid(case_id)})
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    return await enrich(db, c)


@router.delete("/{case_id}")
async def delete_case(case_id: str, _=Depends(get_current_user)):
    db = get_db()
    result = await db.cases.delete_one({"_id": oid(case_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"message": "Deleted successfully"}
