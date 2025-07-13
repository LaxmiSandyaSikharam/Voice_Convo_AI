from openai import OpenAI
import os
from fastapi import UploadFile
from tempfile import NamedTemporaryFile

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def transcribe_audio(file: UploadFile):
    with NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        content = await file.read()
        temp_audio.write(content)
        temp_audio.flush()

        with open(temp_audio.name, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
