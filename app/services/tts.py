import os
import requests

def speak_text(text: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "tts-1",
        "voice": "nova",
        "input": text
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        # Make sure static/audio directory exists
        static_path = os.path.join("static", "audio")
        os.makedirs(static_path, exist_ok=True)

        # Save file
        file_path = os.path.join(static_path, "tts_output.mp3")
        with open(file_path, "wb") as f:
            f.write(response.content)

        # 🔍 Debug logging
        abs_path = os.path.abspath(file_path)
        print(f"✅ Audio saved at: {abs_path}")
        print(f"📁 Exists? {os.path.exists(abs_path)}")

        # Return static-accessible path
        return "/static/audio/tts_output.mp3"
    else:
        raise Exception(f"TTS API Error: {response.status_code} - {response.text}")
