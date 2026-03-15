from fastapi import APIRouter, HTTPException, status, Depends
from app.database import get_db
from app.models.user import UserCreate, UserResponse, LoginRequest, TokenResponse
from app.utils.auth import hash_password, verify_password, create_access_token, get_current_user
from bson import ObjectId

router = APIRouter(prefix="/api/auth", tags=["auth"])


def user_to_response(user: dict) -> UserResponse:
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        role=user["role"],
        phone=user.get("phone"),
        status=user["status"],
    )


@router.post("/register", response_model=TokenResponse)
async def register(data: UserCreate):
    db = get_db()
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_dict = data.model_dump()
    user_dict["password_hash"] = hash_password(user_dict.pop("password"))
    result = await db.users.insert_one(user_dict)
    user = await db.users.find_one({"_id": result.inserted_id})
    token = create_access_token({"sub": str(user["_id"])})
    return TokenResponse(access_token=token, user=user_to_response(user))


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    db = get_db()
    user = await db.users.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.get("status") == "inactive":
        raise HTTPException(status_code=403, detail="Account is inactive")
    token = create_access_token({"sub": str(user["_id"])})
    return TokenResponse(access_token=token, user=user_to_response(user))


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return user_to_response(current_user)
