"""Nexus AI - Voice Service.

This module provides speech-to-text (STT) capabilities using OpenAI Whisper.
Transcriptions are performed locally on the GPU for maximum privacy and performance.
"""

import os
import tempfile
from typing import Optional

try:
    import torch
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️ Whisper/Torch not installed — voice transcription disabled.")

class VoiceService:
    """Service for handling voice-related tasks like STT."""
    
    def __init__(self, model_name: str = "base"):
        """Initialize and load the Whisper model.
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large).
                        'base' is a good balance for RTX 4060.
        """
        if not WHISPER_AVAILABLE:
            print("⚠️ VoiceService: Whisper not available, STT disabled.")
            self.model = None
            self.device = "cpu"
            return
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🎙️ Loading Whisper model '{model_name}' on {self.device}...")
        self.model = whisper.load_model(model_name, device=self.device)
        print("✅ VoiceService ready!")

    def transcribe(self, audio_path: str) -> str:
        """Transcribe an audio file to text.
        
        Args:
            audio_path: Path to the audio file (wav, mp3, etc.).
            
        Returns:
            The transcribed text.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        # Perform transcription
        result = self.model.transcribe(audio_path, fp16=(self.device == "cuda"))
        return result.get("text", "").strip()

    def transcribe_from_bytes(self, audio_bytes: bytes, extension: str = ".wav") -> str:
        """Transcribe audio from raw bytes using a temporary file.
        
        Args:
            audio_bytes: The audio data.
            extension: The file extension (e.g., .wav, .webm).
            
        Returns:
            The transcribed text.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
            
        try:
            text = self.transcribe(tmp_path)
            return text
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

# Singleton instance
_voice_service = None

def get_voice_service():
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceService()
    return _voice_service
