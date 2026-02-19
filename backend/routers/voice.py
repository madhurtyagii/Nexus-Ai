"""Nexus AI - Voice Router.

Endpoints for multimodal voice interaction.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import Dict, Any

from services.voice_service import get_voice_service
from models.user import User
from dependencies import get_current_user

router = APIRouter(prefix="/voice", tags=["Voice"])

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Transcribe an uploaded audio file to text.
    
    Accepts audio files (wav, webm, mp3) and returns the transcribed string.
    """
    try:
        # Read audio bytes
        audio_content = await file.read()
        
        # Get transcription
        voice_service = get_voice_service()
        # MediaRecorder in browser often sends webm
        extension = f".{file.filename.split('.')[-1]}" if "." in file.filename else ".webm"
        
        import anyio
        text = await anyio.to_thread.run_sync(
            voice_service.transcribe_from_bytes, 
            audio_content, 
            extension
        )
        
        return {
            "status": "success",
            "text": text,
            "filename": file.filename
        }
    except Exception as e:
        print(f"❌ Transcription error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to transcribe audio: {str(e)}"
        )
