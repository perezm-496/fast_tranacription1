# AI Endpoints Documentation

This document describes the AI endpoints that have been added to the FastAPI application for audio transcription and chat completion.

## Overview

The AI endpoints provide both synchronous and asynchronous processing for:
- Audio transcription using OpenAI's Whisper model
- Chat completion using OpenAI's GPT-4 model

## Endpoints

### Chat Completion

#### Synchronous Chat Completion
- **URL**: `POST /api/ai/chat-sync`
- **Description**: Send a prompt and get an immediate response
- **Parameters**: 
  - `prompt` (form data): The text prompt to send to GPT-4
- **Response**: JSON with the AI response

**Example:**
```bash
curl -X POST http://localhost:8000/api/ai/chat-sync \
  -F "prompt=What is the capital of France?"
```

**Response:**
```json
{
  "response": "The capital of France is Paris.",
  "status": "completed"
}
```

#### Asynchronous Chat Completion
- **URL**: `POST /api/ai/chat`
- **Description**: Send a prompt and get a task ID for tracking
- **Parameters**: 
  - `prompt` (form data): The text prompt to send to GPT-4
- **Response**: JSON with task ID and status

**Example:**
```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -F "prompt=Explain quantum physics in simple terms"
```

**Response:**
```json
{
  "message": "Chat completion started",
  "task_id": "abc123-def456-ghi789",
  "status": "processing"
}
```

#### Check Chat Task Status
- **URL**: `GET /api/ai/chat/{task_id}`
- **Description**: Check the status of an asynchronous chat completion task
- **Parameters**: 
  - `task_id` (path): The task ID returned from the chat endpoint
- **Response**: JSON with task status and result (if completed)

**Example:**
```bash
curl http://localhost:8000/api/ai/chat/abc123-def456-ghi789
```

**Response (completed):**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "completed",
  "response": "Quantum physics is a branch of physics that..."
}
```

**Response (processing):**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "processing"
}
```

### Audio Transcription

#### Synchronous Audio Transcription
- **URL**: `POST /api/ai/transcribe-sync`
- **Description**: Upload an audio file and get immediate transcription
- **Parameters**: 
  - `file` (file upload): Audio file to transcribe
- **Response**: JSON with the transcription text

**Example:**
```bash
curl -X POST http://localhost:8000/api/ai/transcribe-sync \
  -F "file=@audio_file.wav"
```

**Response:**
```json
{
  "transcription": "Hello, this is a test audio file.",
  "status": "completed"
}
```

#### Asynchronous Audio Transcription
- **URL**: `POST /api/ai/transcribe`
- **Description**: Upload an audio file and get a task ID for tracking
- **Parameters**: 
  - `file` (file upload): Audio file to transcribe
- **Response**: JSON with task ID and status

**Example:**
```bash
curl -X POST http://localhost:8000/api/ai/transcribe \
  -F "file=@audio_file.wav"
```

**Response:**
```json
{
  "message": "Audio transcription started",
  "task_id": "xyz789-abc123-def456",
  "status": "processing"
}
```

#### Check Transcription Task Status
- **URL**: `GET /api/ai/transcribe/{task_id}`
- **Description**: Check the status of an asynchronous transcription task
- **Parameters**: 
  - `task_id` (path): The task ID returned from the transcribe endpoint
- **Response**: JSON with task status and result (if completed)

**Example:**
```bash
curl http://localhost:8000/api/ai/transcribe/xyz789-abc123-def456
```

**Response (completed):**
```json
{
  "task_id": "xyz789-abc123-def456",
  "status": "completed",
  "transcription": "Hello, this is a test audio file."
}
```

## Setup Requirements

### Prerequisites
1. **Redis**: Required for Celery task queue
   ```bash
   # Start Redis (if using Docker)
   docker run -d -p 6379:6379 redis:alpine
   ```

2. **Celery Worker**: Required for asynchronous processing
   ```bash
   # Start the Celery worker
   celery -A celery_worker.celery_app worker --loglevel=info
   ```

3. **Environment Variables**: Make sure you have your OpenAI API key set
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

### Running the Application

1. **Start the FastAPI server:**
   ```bash
   uvicorn elise.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the Celery worker (in a separate terminal):**
   ```bash
   celery -A celery_worker.celery_app worker --loglevel=info
   ```

3. **Test the endpoints:**
   ```bash
   python test_ai_endpoints.py
   ```

## Error Handling

The endpoints include comprehensive error handling:

- **File validation**: Audio files are validated to ensure they are actually audio files
- **API rate limiting**: Built-in retry logic for OpenAI API rate limits
- **Task failure handling**: Proper error reporting for failed tasks
- **Resource cleanup**: Temporary files are automatically cleaned up

## Supported Audio Formats

The transcription endpoints support all audio formats that OpenAI's Whisper model supports, including:
- WAV
- MP3
- M4A
- FLAC
- And other common audio formats

## Rate Limiting and Retries

The OpenAI helper functions include automatic retry logic for rate limiting:
- Up to 3 retries with exponential backoff
- 2-second initial delay, doubling on each retry
- Automatic handling of OpenAI rate limit errors

## Security Considerations

- Audio files are stored temporarily and automatically cleaned up
- File uploads are validated for audio content type
- API keys are loaded from environment variables
- No sensitive data is logged or stored permanently

## Testing

Use the provided test script to verify the endpoints are working:

```bash
python test_ai_endpoints.py
```

This will test both synchronous and asynchronous endpoints and provide examples of how to use them. 