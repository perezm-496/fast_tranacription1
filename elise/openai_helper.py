import openai
import os
import time
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def with_retry(func):
    def wrapper(*args, **kwargs):
        retries = 3
        delay = 2
        for i in range(retries):
            try:
                return func(*args, **kwargs)
            except openai.error.RateLimitError:
                time.sleep(delay)
                delay *= 2
        raise Exception("Max retries exceeded")
    return wrapper

@with_retry
def transcribe_audio(file_path: str):
    with open(file_path, "rb") as f:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    return transcript.text

@with_retry
def complete_chat(prompt: str):
    response = openai.responses.create(
        model="gpt-4-turbo",
        instructions="Complete the text as an expert writer.", # TODO: add instructions
        input=prompt
    )
    return response.output_text

@with_retry
def create_report(resources_text: str):
    """
    Create a summary report in Spanish from the given resources text
    """
    prompt = f"Summarize the given information. Write the summary in spanish. Use the information to create a report.\n\nInformation:\n{resources_text}"
    
    response = openai.responses.create(
        model="gpt-4-turbo",
        instructions="You are a medical professional assistant. Create a comprehensive summary in Spanish of the provided medical consultation information. Focus on key findings, patient symptoms, and important details.",
        input=prompt
    )
    return response.output_text
