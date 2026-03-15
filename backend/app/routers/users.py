from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from app.database import get_db
from app.models.user import UserCreate, UserUpdate, UserResponse
from app.utils.auth import hash_password, get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


def oid(val: str):
    try:
        return ObjectId(val)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid id: {val}")


def to_resp(u: dict) -> UserResponse:
    return UserResponse(
        id=str(u["_id"]),
        name=u["name"],
        email=u["email"],
        role=u["role"],
        phone=u.get("phone"),
        status=u["status"],
    )


@router.get("", response_model=List[UserResponse])
async def list_users(skip: int = 0, limit: int = 100, _=Depends(get_current_user)):
    db = get_db()
    users = await db.users.find().skip(skip).limit(limit).to_list(limit)
    return [to_resp(u) for u in users]


@router.post("", response_model=UserResponse)
async def create_user(data: UserCreate, _=Depends(get_current_user)):
    db = get_db()
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    user_dict = data.model_dump()
    user_dict["password_hash"] = hash_password(user_dict.pop("password"))
    result = await db.users.insert_one(user_dict)
    u = await db.users.find_one({"_id": result.inserted_id})
    return to_resp(u)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, _=Depends(get_current_user)):
    db = get_db()
    u = await db.users.find_one({"_id": oid(user_id)})
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return to_resp(u)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, data: UserUpdate, _=Depends(get_current_user)):
    db = get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    await db.users.update_one({"_id": oid(user_id)}, {"$set": update_data})
    u = await db.users.find_one({"_id": oid(user_id)})
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return to_resp(u)


@router.delete("/{user_id}")
async def delete_user(user_id: str, _=Depends(get_current_user)):
    db = get_db()
    result = await db.users.delete_one({"_id": oid(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Deleted successfully"}
