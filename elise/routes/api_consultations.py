from fastapi import APIRouter, Depends, HTTPException
from elise.models import Consultation, ConsultationCreate
from elise.database import db
from elise.utils.auth import decode_access_token
from fastapi.security import HTTPBearer
from datetime import datetime
from typing import List
from bson import ObjectId
import json

router = APIRouter(prefix="/api/consultations", tags=["consultations"])
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

@router.post("/", response_model=Consultation)
async def create_consultation(
    consultation: ConsultationCreate,
    current_user_id: str = Depends(get_current_user)
):
    # Verify that the patient belongs to the current user
    patient = db.patients.find_one({
        "_id": ObjectId(consultation.patient_id),
        "user_id": current_user_id
    })
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found or not authorized")
    
    consultation_dict = consultation.dict()
    consultation_dict["consultation_id"] = str(ObjectId())
    consultation_dict["user_id"] = current_user_id
    # Ensure resources list is initialized
    if "resources" not in consultation_dict:
        consultation_dict["resources"] = []
    
    result = db.consultations.insert_one(consultation_dict)
    consultation_dict["_id"] = str(result.inserted_id)
    
    return serialize_mongo_doc(consultation_dict)

@router.get("/patient/{patient_id}", response_model=List[dict])
async def get_consultations_by_patient(
    patient_id: str,
    current_user_id: str = Depends(get_current_user)
):
    # Verify that the patient belongs to the current user
    patient = db.patients.find_one({
        "_id": ObjectId(patient_id),
        "user_id": current_user_id
    })
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found or not authorized")
    
    # Get consultations for this patient
    consultations = db.consultations.find(
        {"patient_id": patient_id},
        {"consultation_id": 1, "date": 1, "time": 1, "description": 1, "report_txt": 1, "resources": 1, "_id": 0}
    )
    
    consultations_list = []
    for consultation in consultations:
        consultation_doc = serialize_mongo_doc(consultation)
        # Add patient info to each consultation
        consultation_doc["patient_name"] = patient["first_name"]
        consultation_doc["patient_last_name"] = patient["last_name"]
        consultation_doc["patient_date_of_birth"] = patient["date_of_birth"].isoformat()
        consultation_doc["patient_description"] = patient.get("description", "")
        consultations_list.append(consultation_doc)
    
    return consultations_list

@router.get("/{consultation_id}/resources")
async def get_all_resources(
    consultation_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Get all resources (transcriptions and chat Q&A) for a specific consultation
    """
    # Verify that the consultation exists and belongs to the current user
    consultation = db.consultations.find_one({
        "consultation_id": consultation_id,
        "user_id": current_user_id
    })
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found or not authorized")
    
    # Return the resources list (list of tuples)
    resources = consultation.get("resources", [])
    
    # Convert datetime objects to ISO format for JSON serialization
    serialized_resources = []
    for resource in resources:
        # MongoDB stores tuples as lists, so we check for list instead of tuple
        if isinstance(resource, (tuple, list)) and len(resource) >= 2:
            # Handle different resource types
            if resource[0] == 'transcript' and len(resource) == 3:
                # ('transcript', upload_time, transcription)
                serialized_resource = [
                    resource[0],
                    resource[1].isoformat() if isinstance(resource[1], datetime) else resource[1],
                    resource[2]
                ]
            elif resource[0] == 'question' and len(resource) == 3:
                # ('question', prompt, answer)
                continue
                # serialized_resource = list(resource)
            elif resource[0] == 'report' and len(resource) == 3:
                # ('report', creation_time, report_text)
                continue 
                # serialized_resource = [
                #     resource[0],
                #     resource[1].isoformat() if isinstance(resource[1], datetime) else resource[1],
                #     resource[2]
                # ]
            else:
                # Fallback for other resource types
                serialized_resource = list(resource)
            
            serialized_resources.append(serialized_resource)
    
    return {
        "consultation_id": consultation_id,
        "resources": serialized_resources,
        "total_resources": len(serialized_resources)
    }

@router.get("/{consultation_id}")
async def get_consultation(
    consultation_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Get a specific consultation with patient information and resources
    """
    # Verify that the consultation exists and belongs to the current user
    consultation = db.consultations.find_one({
        "consultation_id": consultation_id,
        "user_id": current_user_id
    })
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found or not authorized")
    
    # Get patient information
    patient = db.patients.find_one({
        "_id": ObjectId(consultation["patient_id"]),
        "user_id": current_user_id
    })
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Serialize consultation
    consultation_doc = serialize_mongo_doc(consultation)
    
    # Add patient information
    consultation_doc["patient_name"] = patient["first_name"]
    consultation_doc["patient_last_name"] = patient["last_name"]
    consultation_doc["patient_date_of_birth"] = patient["date_of_birth"].isoformat()
    consultation_doc["patient_description"] = patient.get("description", "")
    
    # Serialize resources
    resources = consultation.get("resources", [])
    serialized_resources = []
    for resource in resources:
        # MongoDB stores tuples as lists, so we check for list instead of tuple
        if isinstance(resource, (tuple, list)) and len(resource) >= 2:
            # Handle different resource types
            if resource[0] == 'transcript' and len(resource) == 3:
                # ('transcript', upload_time, transcription)
                serialized_resource = [
                    resource[0],
                    resource[1].isoformat() if isinstance(resource[1], datetime) else resource[1],
                    resource[2]
                ]
            elif resource[0] == 'question' and len(resource) == 3:
                # ('question', prompt, answer)
                serialized_resource = list(resource)
            elif resource[0] == 'report' and len(resource) == 3:
                # ('report', creation_time, report_text)
                serialized_resource = [
                    resource[0],
                    resource[1].isoformat() if isinstance(resource[1], datetime) else resource[1],
                    resource[2]
                ]
            else:
                # Fallback for other resource types
                serialized_resource = list(resource)
            
            serialized_resources.append(serialized_resource)
    
    consultation_doc["resources"] = serialized_resources
    consultation_doc["total_resources"] = len(serialized_resources)
    
    print(f"Returning consultation with {len(serialized_resources)} resources")
    print(f"Resources: {serialized_resources}")
    
    return consultation_doc 