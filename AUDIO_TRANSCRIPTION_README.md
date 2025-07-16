# Audio Transcription with MongoDB Storage

This document describes the enhanced audio transcription system that stores audio files in MongoDB and manages consultation resources.

## Overview

The audio transcription system has been enhanced to:
- Store uploaded audio files in MongoDB `temp_files` collection
- Pass file IDs to Celery tasks instead of file paths
- Add transcriptions to consultation `resources` list
- Automatically clean up temporary files

## Database Schema Changes

### New Models

#### TempFile Model
```python
class TempFile(BaseModel):
    file_id: str
    consultation_id: str
    user_id: str
    filename: str
    content_type: str
    file_data: bytes
    created_at: datetime
```

#### Updated Consultation Model
```python
class Consultation(BaseModel):
    consultation_id: str
    user_id: str
    patient_id: str
    date: datetime
    time: str
    description: str
    report_txt: str = ""
    resources: List[str] = []  # New field for storing transcriptions
```

## API Endpoints

### Transcribe Audio
- **URL**: `POST /api/ai/transcribe`
- **Authentication**: Required (Bearer token)
- **Parameters**:
  - `file`: Audio file upload
  - `consultation_id`: Form parameter (string)
- **Response**: JSON with task ID and status

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/ai/transcribe \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@audio_file.wav" \
  -F "consultation_id=consultation_123"
```

**Example Response:**
```json
{
  "message": "Audio transcription started",
  "task_id": "abc123-def456-ghi789",
  "status": "processing",
  "consultation_id": "consultation_123",
  "file_id": "file_uuid_456"
}
```

### Check Transcription Status
- **URL**: `GET /api/ai/transcribe/{task_id}`
- **Response**: JSON with task status and result

**Example Response (completed):**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "completed",
  "transcription": "Hello, this is the transcribed text.",
  "message": "Transcription completed and added to consultation resources"
}
```

## Workflow

1. **File Upload**: Audio file is uploaded via the API endpoint
2. **Validation**: Consultation ownership is verified
3. **MongoDB Storage**: File is stored in `temp_files` collection with metadata
4. **Task Creation**: Celery task is created with file ID and consultation ID
5. **Processing**: Task retrieves file from MongoDB, creates temporary file for OpenAI API
6. **Transcription**: OpenAI Whisper API transcribes the audio
7. **Storage**: Transcription is added to consultation's `resources` list
8. **Cleanup**: Temporary files are removed from filesystem and MongoDB

## Database Collections

### temp_files Collection
Stores uploaded audio files temporarily:
```javascript
{
  "_id": ObjectId,
  "file_id": "uuid-string",
  "consultation_id": "consultation_123",
  "user_id": "user_456",
  "filename": "audio.wav",
  "content_type": "audio/wav",
  "file_data": BinaryData,
  "created_at": ISODate
}
```

### consultations Collection
Updated to include resources list:
```javascript
{
  "_id": ObjectId,
  "consultation_id": "consultation_123",
  "user_id": "user_456",
  "patient_id": "patient_789",
  "date": ISODate,
  "time": "14:30",
  "description": "Consultation description",
  "report_txt": "Original report text",
  "resources": [
    "Transcription 1: Hello, this is the first transcription.",
    "Transcription 2: This is another transcription."
  ]
}
```

## Security Features

- **Authentication**: All endpoints require valid JWT tokens
- **Authorization**: Users can only transcribe audio for their own consultations
- **File Validation**: Audio files are validated before processing
- **Automatic Cleanup**: Temporary files are automatically removed after processing

## Celery Tasks

### transcribe_audio_task
- **Parameters**: `file_id` (string), `consultation_id` (string)
- **Function**: Retrieves file from MongoDB, transcribes, updates consultation
- **Cleanup**: Removes temporary files and MongoDB records

### cleanup_temp_files
- **Schedule**: Runs every 24 hours via Celery Beat
- **Function**: Removes temporary files older than 24 hours
- **Purpose**: Prevents database bloat from abandoned uploads

## Setup and Configuration

### Prerequisites
1. **MongoDB**: Running and accessible
2. **Redis**: Required for Celery task queue
3. **OpenAI API Key**: Set in environment variables

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=your_database_name
```

### Running the System

1. **Start Redis:**
   ```bash
   docker run -d -p 6379:6379 redis:alpine
   ```

2. **Start Celery Worker:**
   ```bash
   celery -A elise.task.celery_app worker --loglevel=info
   ```

3. **Start Celery Beat (for cleanup tasks):**
   ```bash
   celery -A elise.task.celery_app beat --loglevel=info
   ```

4. **Start FastAPI Server:**
   ```bash
   uvicorn elise.main:app --reload
   ```

## Error Handling

- **File Not Found**: Returns 404 if file ID doesn't exist in MongoDB
- **Consultation Not Found**: Returns 404 if consultation doesn't belong to user
- **Transcription Failure**: Proper error reporting and cleanup
- **Network Issues**: Retry logic for OpenAI API calls

## Performance Considerations

- **File Size**: Large audio files are stored in MongoDB (consider GridFS for very large files)
- **Memory Usage**: Files are temporarily written to disk for OpenAI API compatibility
- **Database Load**: Temporary files are automatically cleaned up to prevent bloat
- **Concurrent Processing**: Celery workers can handle multiple transcription requests

## Monitoring

- **Task Status**: Check task status via API endpoints
- **Database Size**: Monitor `temp_files` collection size
- **Cleanup Logs**: Celery Beat logs cleanup task results
- **Error Logs**: Failed transcriptions are logged with error details 