from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from bson import ObjectId
from app.database import get_db
from app.models.vendor import VendorCreate, VendorUpdate, VendorResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/vendors", tags=["vendors"])


def oid(val: str):
    try:
        return ObjectId(val)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid id: {val}")


def to_resp(v: dict) -> VendorResponse:
    return VendorResponse(id=str(v["_id"]), **{k: val for k, val in v.items() if k != "_id"})


@router.get("", response_model=List[VendorResponse])
async def list_vendors(skip: int = 0, limit: int = 100, type: Optional[str] = None, _=Depends(get_current_user)):
    db = get_db()
    query = {}
    if type:
        query["type"] = type
    vendors = await db.vendors.find(query).skip(skip).limit(limit).to_list(limit)
    return [to_resp(v) for v in vendors]


@router.post("", response_model=VendorResponse)
async def create_vendor(data: VendorCreate, _=Depends(get_current_user)):
    db = get_db()
    result = await db.vendors.insert_one(data.model_dump())
    v = await db.vendors.find_one({"_id": result.inserted_id})
    return to_resp(v)


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: str, _=Depends(get_current_user)):
    db = get_db()
    v = await db.vendors.find_one({"_id": oid(vendor_id)})
    if not v:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return to_resp(v)


@router.put("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(vendor_id: str, data: VendorUpdate, _=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    await db.vendors.update_one({"_id": oid(vendor_id)}, {"$set": update_data})
    v = await db.vendors.find_one({"_id": oid(vendor_id)})
    if not v:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return to_resp(v)


@router.delete("/{vendor_id}")
async def delete_vendor(vendor_id: str, _=Depends(get_current_user)):
    db = get_db()
    result = await db.vendors.delete_one({"_id": oid(vendor_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Deleted successfully"}
