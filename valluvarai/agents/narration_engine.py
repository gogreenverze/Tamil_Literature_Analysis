"""
Narration Engine - Generates audio narration for stories.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import requests
    import gtts
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

class NarrationEngine:
    """
    Generates audio narration for stories using text-to-speech technology.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        tts_provider: str = "gtts",
        output_dir: Optional[str] = None
    ):
        """
        Initialize the NarrationEngine.
        
        Args:
            api_key: API key for premium TTS services (ElevenLabs, etc.).
            tts_provider: The TTS provider to use ("gtts", "elevenlabs", etc.).
            output_dir: Directory to save audio files. If None, uses a temporary directory.
        """
        self.api_key = api_key
        self.tts_provider = tts_provider
        
        # Set up output directory
        if output_dir:
            self.output_dir = Path(output_dir)
            os.makedirs(self.output_dir, exist_ok=True)
        else:
            self.output_dir = Path(tempfile.mkdtemp())
    
    def generate_audio(self, text: str, language: str) -> Dict[str, Any]:
        """
        Generate audio narration for a story.
        
        Args:
            text: The text to convert to speech.
            language: The language of the text ("tamil" or "english").
            
        Returns:
            Dictionary with audio file information.
        """
        if not TTS_AVAILABLE:
            return {
                "success": False,
                "error": "TTS libraries not available. Install gtts or other TTS packages.",
                "file_path": None
            }
        
        if self.tts_provider == "gtts":
            return self._generate_with_gtts(text, language)
        elif self.tts_provider == "elevenlabs" and self.api_key:
            return self._generate_with_elevenlabs(text, language)
        else:
            # Fall back to gTTS if the specified provider is not available
            return self._generate_with_gtts(text, language)
    
    def _generate_with_gtts(self, text: str, language: str) -> Dict[str, Any]:
        """
        Generate audio using Google Text-to-Speech.
        
        Args:
            text: The text to convert to speech.
            language: The language of the text.
            
        Returns:
            Dictionary with audio file information.
        """
        try:
            # Set the language code
            lang_code = "ta" if language == "tamil" else "en"
            
            # Create a filename
            filename = f"{language}_narration_{hash(text) % 10000}.mp3"
            file_path = self.output_dir / filename
            
            # Generate the audio
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(str(file_path))
            
            return {
                "success": True,
                "file_path": str(file_path),
                "duration": self._estimate_duration(text, language),
                "provider": "gtts"
            }
            
        except Exception as e:
            print(f"Error generating audio with gTTS: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": None
            }
    
    def _generate_with_elevenlabs(self, text: str, language: str) -> Dict[str, Any]:
        """
        Generate audio using ElevenLabs API.
        
        Args:
            text: The text to convert to speech.
            language: The language of the text.
            
        Returns:
            Dictionary with audio file information.
        """
        try:
            # ElevenLabs API endpoint
            url = "https://api.elevenlabs.io/v1/text-to-speech"
            
            # Select voice based on language
            voice_id = "pNInz6obpgDQGcFmaJgB" if language == "english" else "AZnzlk1XvdvUeBnXmlld"  # Example voice IDs
            
            # Create a filename
            filename = f"{language}_narration_{hash(text) % 10000}.mp3"
            file_path = self.output_dir / filename
            
            # Prepare the request
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            # Make the request
            response = requests.post(f"{url}/{voice_id}", json=data, headers=headers)
            
            if response.status_code == 200:
                # Save the audio file
                with open(file_path, "wb") as f:
                    f.write(response.content)
                
                return {
                    "success": True,
                    "file_path": str(file_path),
                    "duration": self._estimate_duration(text, language),
                    "provider": "elevenlabs"
                }
            else:
                raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
            
        except Exception as e:
            print(f"Error generating audio with ElevenLabs: {e}")
            # Fall back to gTTS
            return self._generate_with_gtts(text, language)
    
    def _estimate_duration(self, text: str, language: str) -> float:
        """
        Estimate the duration of the audio in seconds.
        
        Args:
            text: The text to estimate duration for.
            language: The language of the text.
            
        Returns:
            Estimated duration in seconds.
        """
        # Count words
        word_count = len(text.split())
        
        # Estimate words per minute based on language
        wpm = 150 if language == "english" else 130  # Tamil might be slightly slower
        
        # Calculate duration in seconds
        duration = (word_count / wpm) * 60
        
        # Add some buffer
        return max(duration, 3.0)  # Minimum 3 seconds
