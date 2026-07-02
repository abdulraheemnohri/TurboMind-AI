# TurboMind AI - Voice Package
# ==============================

"""
Voice Package for TurboMind AI.
Handles speech recognition and text-to-speech functionality.

Features:
- Speech to Text (Offline)
- Text to Speech (Offline)
- Voice Assistant
- Audio Processing
- Language Support
"""

from .speech_to_text import SpeechToText
from .text_to_speech import TextToSpeech
from .voice_assistant import VoiceAssistant

__all__ = [
    'SpeechToText',
    'TextToSpeech', 
    'VoiceAssistant'
]
__version__ = '1.0.0'