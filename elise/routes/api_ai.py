from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from ..openai_helper import transcribe_audio, complete_chat
from ..task import transcribe_audio_task, complete_chat_task, create_report_task
from ..database import db
from ..utils.auth import decode_access_token
from bson import ObjectId
import os
import tempfile
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/ai", tags=["AI"])
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

@router.post("/transcribe")
async def transcribe_audio_endpoint(
    file: UploadFile = File(...),
    consultation_id: str = Form(...),
    current_user_id: str = Depends(get_current_user)
):
    """
    Upload an audio file and get its transcription
    """
    # Validate that the consultation exists and belongs to the current user
    consultation = db.consultations.find_one({
        "consultation_id": consultation_id,
        "user_id": current_user_id
    })
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found or not authorized")
    
    # Validate file type
    print(f"File: {file}")
    print("File is an audio file")
    
    try:
        # Read the file content
        content = await file.read()
        
        # Generate a unique file ID
        file_id = str(uuid.uuid4())
        
        # Store the file in MongoDB temp_files collection
        temp_file_doc = {
            "file_id": file_id,
            "consultation_id": consultation_id,
            "user_id": current_user_id,
            "filename": file.filename or "audio.webm",
            "content_type": file.content_type or "audio/webm",
            "file_data": content,
            "created_at": datetime.utcnow()
        }
        
        db.temp_files.insert_one(temp_file_doc)
        
        # Process the transcription asynchronously using Celery
        task = transcribe_audio_task.delay(file_id, consultation_id)
        
        return JSONResponse({
            "message": "Audio transcription started",
            "task_id": task.id,
            "status": "processing",
            "consultation_id": consultation_id,
            "file_id": file_id
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@router.get("/transcribe/{task_id}")
async def get_transcription_status(
    task_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Get the status and result of a transcription task
    """
    print(f"Getting transcription status for task: {task_id}")
    task = transcribe_audio_task.AsyncResult(task_id)
    print(f"Task: {task}")

    if task.ready():
        if task.successful():
            result = task.get()
            return JSONResponse({
                "task_id": task_id,
                "status": "completed",
                "transcription": result,
                "message": "Transcription completed and added to consultation resources"
            })
        else:
            return JSONResponse({
                "task_id": task_id,
                "status": "failed",
                "error": str(task.info)
            })
    else:
        return JSONResponse({
            "task_id": task_id,
            "status": "processing"
        })

@router.post("/chat")
async def complete_chat_endpoint(
    prompt: str = Form(...),
    consultation_id: str = Form(...),
    current_user_id: str = Depends(get_current_user)
):
    """
    Send a prompt and get a chat completion
    """
    # Validate that the consultation exists and belongs to the current user
    consultation = db.consultations.find_one({
        "consultation_id": consultation_id,
        "user_id": current_user_id
    })
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found or not authorized")
    
    try:
        # Process the chat completion asynchronously using Celery
        print(f"Processing chat completion for prompt: {prompt}")
        task = complete_chat_task.delay(prompt, consultation_id)
        print(f"Chat completion task started: {task.id}")
        
        return JSONResponse({
            "message": "Chat completion started",
            "task_id": task.id,
            "status": "processing"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat completion: {str(e)}")

@router.get("/chat/{task_id}")
async def get_chat_completion_status(
    task_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Get the status and result of a chat completion task
    """
    task = complete_chat_task.AsyncResult(task_id)
    
    if task.ready():
        if task.successful():
            result = task.get()
            return JSONResponse({
                "task_id": task_id,
                "status": "completed",
                "response": result
            })
        else:
            return JSONResponse({
                "task_id": task_id,
                "status": "failed",
                "error": str(task.info)
            })
    else:
        return JSONResponse({
            "task_id": task_id,
            "status": "processing"
        })

@router.post("/create_reporte")
async def create_reporte_endpoint(
    consultation_id: str = Form(...),
    current_user_id: str = Depends(get_current_user)
):
    """
    Create a summary report from all resources in a consultation
    """
    # Validate that the consultation exists and belongs to the current user
    consultation = db.consultations.find_one({
        "consultation_id": consultation_id,
        "user_id": current_user_id
    })
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found or not authorized")
    
    # Check if there are resources to create a report from
    resources = consultation.get("resources", [])
    if not resources:
        raise HTTPException(status_code=400, detail="No resources found for this consultation. Add transcriptions or chat conversations first.")
    
    try:
        # Process the report creation asynchronously using Celery
        print(f"Creating report for consultation: {consultation_id}")
        task = create_report_task.delay(consultation_id)
        print(f"Report creation task started: {task.id}")
        
        return JSONResponse({
            "message": "Report creation started",
            "task_id": task.id,
            "status": "processing",
            "consultation_id": consultation_id
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating report: {str(e)}")

@router.get("/create_reporte/{task_id}")
async def get_report_creation_status(
    task_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Get the status and result of a report creation task
    """
    task = create_report_task.AsyncResult(task_id)
    
    if task.ready():
        if task.successful():
            result = task.get()
            return JSONResponse({
                "task_id": task_id,
                "status": "completed",
                "report": result,
                "message": "Report created and saved to consultation"
            })
        else:
            return JSONResponse({
                "task_id": task_id,
                "status": "failed",
                "error": str(task.info)
            })
    else:
        return JSONResponse({
            "task_id": task_id,
            "status": "processing"
        })
