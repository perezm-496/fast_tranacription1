from fastapi import APIRouter
from elise.database import db
from elise.models import Membership

router = APIRouter(prefix="/memberships", tags=["memberships"])

@router.post("/")
async def create_membership(membership: Membership):
    result = db.memberships.insert_one(membership.dict())
    return {"id": str(result.inserted_id)}
