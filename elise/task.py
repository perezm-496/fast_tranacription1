from celery import Celery
from .openai_helper import transcribe_audio, complete_chat, create_report
from .database import db
import tempfile
import os
from datetime import datetime, timedelta

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER"),
    backend=os.getenv("CELERY_BACKEND")
)

# Configure Celery Beat schedule
celery_app.conf.beat_schedule = {
    'cleanup-temp-files-daily': {
        'task': 'tasks.cleanup_temp_files',
        'schedule': 86400.0,  # 24 hours in seconds
    },
}

@celery_app.task(name="tasks.transcribe_audio_task")
def transcribe_audio_task(file_id: str, consultation_id: str):
    temp_file_path = None
    try:
        # Get the file from MongoDB
        temp_file_doc = db.temp_files.find_one({"file_id": file_id})
        if not temp_file_doc:
            raise Exception(f"File with ID {file_id} not found in database")
        
        # Create a temporary file to work with OpenAI API
        temp_dir = tempfile.gettempdir()
        file_extension = os.path.splitext(temp_file_doc["filename"])[1] if temp_file_doc["filename"] else '.webm'
        temp_file_path = os.path.join(temp_dir, f"audio_{file_id}{file_extension}")
        
        # Write the file data to temporary file
        with open(temp_file_path, "wb") as f:
            f.write(temp_file_doc["file_data"])
        
        # Transcribe the audio
        transcription = transcribe_audio(temp_file_path)
        
        # Get the upload time from the temp file document
        upload_time = temp_file_doc["created_at"]
        
        # Add the transcription to the consultation's resources list as a tuple
        transcription_tuple = ('transcript', upload_time, transcription)
        db.consultations.update_one(
            {"consultation_id": consultation_id},
            {"$push": {"resources": transcription_tuple}}
        )
        
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        # Delete the temp file from MongoDB after processing
        db.temp_files.delete_one({"file_id": file_id})
        
        return transcription
    except Exception as e:
        # Clean up the temporary file even if transcription fails
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise e

@celery_app.task(name="tasks.complete_chat_task")
def complete_chat_task(prompt: str, consultation_id: str):
    # Get the chat completion from OpenAI
    answer = complete_chat(prompt)
    
    # Add the chat Q&A to the consultation's resources list as a tuple
    chat_tuple = ('question', prompt, answer)
    db.consultations.update_one(
        {"consultation_id": consultation_id},
        {"$push": {"resources": chat_tuple}}
    )
    
    return answer

@celery_app.task(name="tasks.create_report_task")
def create_report_task(consultation_id: str):
    """
    Create a summary report from all resources in a consultation
    """
    try:
        # Get the consultation and its resources
        consultation = db.consultations.find_one({"consultation_id": consultation_id})
        if not consultation:
            raise Exception(f"Consultation with ID {consultation_id} not found")
        
        resources = consultation.get("resources", [])
        if not resources:
            raise Exception("No resources found for this consultation")
        
        # Concatenate all resources into a single text
        resources_text = ""
        for resource in resources:
            # MongoDB stores tuples as lists, so we check for list instead of tuple
            if isinstance(resource, (tuple, list)) and len(resource) >= 2:
                if resource[0] == 'transcript' and len(resource) == 3:
                    # Format: ('transcript', upload_time, transcription)
                    resources_text += f"Transcripción ({resource[1]}): {resource[2]}\n\n"
                elif resource[0] == 'question' and len(resource) == 3:
                    # Format: ('question', prompt, answer)
                    resources_text += f"Pregunta: {resource[1]}\nRespuesta: {resource[2]}\n\n"
        
        # Create the report using OpenAI
        print(f"Resources of {consultation_id} text: {resources_text}")
        report_text = create_report(resources_text)
        
        # Add the report to the consultation's resources list as a tuple
        report_tuple = ('report', datetime.utcnow(), report_text)
        
        # Update the consultation with the report in both report_txt field and resources array
        db.consultations.update_one(
            {"consultation_id": consultation_id},
            {
                "$set": {"report_txt": report_text},
                "$push": {"resources": report_tuple}
            }
        )
        
        return report_text
    except Exception as e:
        raise e

@celery_app.task(name="tasks.cleanup_temp_files")
def cleanup_temp_files():
    """Clean up temporary files older than 24 hours"""
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    result = db.temp_files.delete_many({"created_at": {"$lt": cutoff_time}})
    return f"Cleaned up {result.deleted_count} old temporary files"
