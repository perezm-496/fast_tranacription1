from fastapi import APIRouter, Depends, HTTPException
from elise.models import Patient, PatientCreate
from elise.database import db
from elise.utils.auth import decode_access_token
from fastapi.security import HTTPBearer
from datetime import datetime
from typing import List
from bson import ObjectId

router = APIRouter(prefix="/api/patients", tags=["patients"])
security = HTTPBearer()

async def get_current_user(credentials = Depends(security)):
    try:
        payload = decode_access_token(credentials.credentials)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        user = db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return str(user["_id"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

def serialize_mongo_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if doc is None:
        return None
    
    # Convert ObjectId to string
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    
    # Handle nested ObjectIds
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, datetime):
            doc[key] = value.isoformat()
    
    return doc

@router.post("/", response_model=Patient)
async def create_patient(
    patient: PatientCreate,
    current_user_id: str = Depends(get_current_user)
):
    patient_dict = patient.dict()
    patient_dict["user_id"] = current_user_id
    patient_dict["id"] = str(ObjectId())
    
    result = db.patients.insert_one(patient_dict)
    patient_dict["_id"] = str(result.inserted_id)
    
    return serialize_mongo_doc(patient_dict)

@router.get("/", response_model=List[dict])
async def get_user_patients(
    current_user_id: str = Depends(get_current_user)
):
    patients = db.patients.find(
        {"user_id": current_user_id},
        {"first_name": 1, "last_name": 1, "date_of_birth": 1, "_id": 1}
    )
    
    patients_list = []
    for patient in patients:
        patients_list.append(serialize_mongo_doc(patient))
    
    return patients_list
