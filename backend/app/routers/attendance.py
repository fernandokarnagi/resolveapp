from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from bson import ObjectId
from app.database import get_db
from app.models.attendance import AttendanceCreate, AttendanceUpdate, AttendanceResponse, AttendanceType
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


def oid(val: str):
    try:
        return ObjectId(val)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid id: {val}")


async def enrich(db, a: dict) -> AttendanceResponse:
    building = await db.buildings.find_one({"_id": oid(a["building_id"])}) if a.get("building_id") else None
    person_name = None
    if a.get("person_id"):
        try:
            # Try users first, then vendors
            person = await db.users.find_one({"_id": oid(a["person_id"])})
            if not person:
                person = await db.vendors.find_one({"_id": oid(a["person_id"])})
            if person:
                person_name = person.get("name")
        except Exception:
            pass
    return AttendanceResponse(
        id=str(a["_id"]),
        building_name=building["name"] if building else None,
        person_name=person_name,
        **{k: v for k, v in a.items() if k != "_id"}
    )


@router.get("", response_model=List[AttendanceResponse])
async def list_attendance(
    skip: int = 0, limit: int = 100,
    attendance_type: Optional[str] = None,
    building_id: Optional[str] = None,
    date: Optional[str] = None,
    _=Depends(get_current_user)
):
    db = get_db()
    query = {}
    if attendance_type:
        query["attendance_type"] = attendance_type
    if building_id:
        query["building_id"] = building_id
    if date:
        query["date"] = date
    items = await db.attendance.find(query).sort("date", -1).skip(skip).limit(limit).to_list(limit)
    return [await enrich(db, a) for a in items]


@router.post("", response_model=AttendanceResponse)
async def create_attendance(data: AttendanceCreate, _=Depends(get_current_user)):
    db = get_db()
    result = await db.attendance.insert_one(data.model_dump())
    a = await db.attendance.find_one({"_id": result.inserted_id})
    return await enrich(db, a)


@router.put("/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(attendance_id: str, data: AttendanceUpdate, _=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    await db.attendance.update_one({"_id": oid(attendance_id)}, {"$set": update_data})
    a = await db.attendance.find_one({"_id": oid(attendance_id)})
    if not a:
        raise HTTPException(status_code=404, detail="Record not found")
    return await enrich(db, a)


@router.delete("/{attendance_id}")
async def delete_attendance(attendance_id: str, _=Depends(get_current_user)):
    db = get_db()
    result = await db.attendance.delete_one({"_id": oid(attendance_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Deleted successfully"}
