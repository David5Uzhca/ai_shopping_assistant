import os
import requests
import base64
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
DEFAULT_VOICE_ID = "ErXwobaYiN019PkySvjV" 

def generate_voice_audio(text: str, voice_id: str = DEFAULT_VOICE_ID) -> Optional[str]:
    if not ELEVENLABS_API_KEY:
        print("⚠️ No ELEVENLABS_API_KEY found.")
        return None

    # Limitar texto para evitar costos excesivos en pruebas
    if len(text) > 500:
        text = text[:497] + "..."

    print(f"[ELEVENLABS] 🎙️ Start generation. Text preview: '{text[:50]}...' (Voice: {voice_id})")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }

    # Configuración principal (Turbo v2.5 - Rápido y buena calidad)
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2_5", 
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
            # Eliminamos style y use_speaker_boost que pueden fallar en Turbo
        }
    }

    try:
        print(f"[ELEVENLABS] 📡 Sending POST request (Turbo v2.5)...")
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            print(f"[ELEVENLABS] ⚠️ Primary Error: {response.status_code} - {response.text}")
            print(f"[ELEVENLABS] 🔄 Switching to Fallback Model (Multilingual v2)...")
            
            # Fallback a Multilingual v2 (Más compatible)
            data["model_id"] = "eleven_multilingual_v2"
            data["voice_settings"] = {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "style": 0.0,
                "use_speaker_boost": True
            }
            response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            # Convertir binario a base64 para enviarlo fácil por JSON
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            print(f"[ELEVENLABS] ✅ Audio generated successfully! Size: {len(audio_base64)} chars (base64)")
            return audio_base64
        else:
            print(f"[ELEVENLABS] ❌ Fallback API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating audio: {str(e)}")
        return None
