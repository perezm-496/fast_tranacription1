#!/usr/bin/env python3
"""
Test script for AI endpoints
"""
import requests
import time
import os

# Base URL for your FastAPI application
BASE_URL = "http://localhost:8000"

def test_chat_completion():
    """Test the chat completion endpoint"""
    print("Testing chat completion...")
    
    print("Testing chat completion asynchronously...")
    # Test asynchronous endpoint
    response = requests.post(
        f"{BASE_URL}/api/ai/chat",
        data={"prompt": "What is the capital of France?"}
    )   
    
    if response.status_code == 200:
        result = response.json()
        task_id = result['task_id']
        print(f"✅ Chat task started with ID: {task_id}")
        
        # Poll for completion
        for _ in range(10):  # Try for 10 seconds
            status_response = requests.get(f"{BASE_URL}/api/ai/chat/{task_id}")
            if status_response.status_code == 200:
                status_result = status_response.json()
                if status_result['status'] == 'completed':
                    print(f"✅ Chat completion (async): {status_result['response']}")
                    break
                elif status_result['status'] == 'failed':
                    print(f"❌ Chat completion failed: {status_result['error']}")
                    break
            time.sleep(1)
        else:
            print("⏰ Chat completion timed out")
    else:
        print(f"❌ Chat task creation failed: {response.text}")

def test_audio_transcription():
    """Test the audio transcription endpoint"""
    print("\nTesting audio transcription...")
    
    # Create a test webm audio file path
    fp = "/home/mperez/test_audio.webm"
    test_audio_path = os.path.expanduser(fp)
    if not os.path.exists(test_audio_path):
        print(f"⚠️ No test audio file found at {test_audio_path}")
        print("Please create a test webm file to use this test")    
    
    print(f"Testing transcription with file: {test_audio_path}")
    # Test asynchronous endpoint
    response = requests.post(
        f"{BASE_URL}/api/ai/transcribe",
        files={"file": open(test_audio_path, "rb")}
    )
    print(f"Response: {response.json()}")
    print(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        task_id = result['task_id']
        print(f"✅ Transcription task started with ID: {task_id}")
        
        # Poll for completion every 5 seconds for up to 1 minute
        for _ in range(12):  # 12 * 5 seconds = 60 seconds
            status_response = requests.get(f"{BASE_URL}/api/ai/transcribe/{task_id}")
            if status_response.status_code == 200:
                status_result = status_response.json()
                if status_result['status'] == 'completed':
                    print(f"✅ Transcription completed: {status_result['transcription']}")
                    break
                elif status_result['status'] == 'failed':
                    print(f"❌ Transcription failed: {status_result['error']}")
                    break
            time.sleep(5)
        else:
            print("⏰ Transcription timed out after 1 minute")
    else:
        print(f"❌ Transcription task creation failed: {response.text}")
    

def main():
    """Main test function"""
    print("🤖 Testing AI Endpoints")
    print("=" * 50)
    
    try:
        test_chat_completion()
        test_audio_transcription()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("\nAvailable endpoints:")
        print(f"POST {BASE_URL}/api/ai/chat-sync - Synchronous chat completion")
        print(f"POST {BASE_URL}/api/ai/chat - Asynchronous chat completion")
        print(f"GET  {BASE_URL}/api/ai/chat/{{task_id}} - Check chat task status")
        print(f"POST {BASE_URL}/api/ai/transcribe-sync - Synchronous audio transcription")
        print(f"POST {BASE_URL}/api/ai/transcribe - Asynchronous audio transcription")
        print(f"GET  {BASE_URL}/api/ai/transcribe/{{task_id}} - Check transcription task status")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the FastAPI server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    main() 