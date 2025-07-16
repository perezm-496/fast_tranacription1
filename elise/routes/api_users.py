from fastapi import APIRouter, Depends
from elise.database import db
from elise.models import UserCreate
from datetime import datetime
from elise.utils.auth import hash_password
from elise.dependencies.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

# @router.post("/")
# async def create_user(user: UserCreate):
#     if db.users.find_one({"email": user.email}):
#         return {"error": "Email already exists"}
#     user_dict = user.dict()
#     user_dict["password"] = hash_password(user.password)
#     user_dict["creation_date"] = datetime.utcnow()
#     result = db.users.insert_one(user_dict)
#     return {"id": str(result.inserted_id)}


@router.get("/ping")
async def ping():
    return {"message": "pong"}

@router.get("/me")
async def read_me(user: dict = Depends(get_current_user)):
    return {"name": user["name"], "email": user["email"]}
