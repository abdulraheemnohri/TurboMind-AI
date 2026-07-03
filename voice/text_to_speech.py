#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Text to Speech
=============================
Converts text to speech using offline models (pyttsx3)
"""

import os
import time
import wave
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np


@dataclass
class TTSConfig:
    """Configuration for text to speech"""
    voice: str = "female"  # male, female, child, robot
    rate: int = 200  # words per minute
    volume: float = 1.0  # 0.0 to 1.0
    pitch: float = 1.0  # pitch variation
    language: str = "en"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'voice': self.voice,
            'rate': self.rate,
            'volume': self.volume,
            'pitch': self.pitch,
            'language': self.language
        }


@dataclass
class AudioOutput:
    """Audio output from text to speech"""
    audio_data: np.ndarray
    sample_rate: int
    duration: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'sample_rate': self.sample_rate,
            'duration': self.duration,
            'audio_size': len(self.audio_data)
        }
    
    def save_to_file(self, file_path: str) -> bool:
        """Save audio to WAV file"""
        try:
            with wave.open(file_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes (16-bit)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(self.audio_data.tobytes())
            return True
        except Exception as e:
            print(f"❌ Error saving audio: {e}")
            return False


class TextToSpeech:
    """
    Converts text to speech using offline models.
    Uses pyttsx3 for offline TTS (no internet required).
    Supports multiple voices and languages.
    """
    
    # Supported voices
    SUPPORTED_VOICES = {
        'male': 'Male Voice',
        'female': 'Female Voice',
        'child': 'Child Voice',
        'robot': 'Robot Voice'
    }
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'ur': 'Urdu',
        'hi': 'Hindi',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ar': 'Arabic'
    }
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the text to speech engine.
        
        Args:
            model_path: Path to offline TTS model (not used for pyttsx3)
        """
        self.model_path = Path(model_path) if model_path else None
        self.is_loaded = False
        self.current_voice = 'female'
        self.current_language = 'en'
        self.config = TTSConfig()
        self.engine = None
        self.voices = []
        
        # Try to initialize pyttsx3
        self._init_pyttsx3()
        print("🔊 Text to Speech initialized")
    
    def _init_pyttsx3(self) -> bool:
        """Initialize pyttsx3 engine"""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            
            # Get available voices
            self.voices = self.engine.getProperty('voices')
            
            # Set default voice
            if self.voices:
                # Try to find a female voice
                for voice in self.voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    self.engine.setProperty('voice', self.voices[0].id)
            
            self.is_loaded = True
            print("✅ pyttsx3 engine initialized")
            return True
            
        except ImportError:
            print("⚠️  pyttsx3 not installed. Install with: pip install pyttsx3")
            print("⚠️  Falling back to simulated TTS")
            self.is_loaded = False
            return False
        except Exception as e:
            print(f"❌ Error initializing pyttsx3: {e}")
            print("⚠️  Falling back to simulated TTS")
            self.is_loaded = False
            return False
    
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        Load text to speech model.
        For pyttsx3, this just initializes the engine.
        
        Args:
            model_path: Path to model file (not used for pyttsx3)
            
        Returns:
            True if model loaded successfully
        """
        if model_path:
            self.model_path = Path(model_path)
        
        return self._init_pyttsx3()
    
    def unload_model(self) -> bool:
        """Unload text to speech model"""
        try:
            if self.engine:
                self.engine.stop()
            self.is_loaded = False
            self.engine = None
            print("🗑️  Text to speech engine stopped")
            return True
        except Exception as e:
            print(f"❌ Error unloading TTS: {e}")
            return False
    
    def set_voice(self, voice: str) -> bool:
        """
        Set the voice for speech synthesis.
        
        Args:
            voice: Voice name (male, female, child, robot) or voice ID
            
        Returns:
            True if voice is supported
        """
        if not self.is_loaded or not self.engine:
            print("❌ TTS engine not loaded")
            return False
        
        try:
            if voice in self.SUPPORTED_VOICES:
                # Find matching voice
                for v in self.voices:
                    name_lower = v.name.lower()
                    if voice == 'male' and ('male' in name_lower or 'man' in name_lower):
                        self.engine.setProperty('voice', v.id)
                        self.current_voice = voice
                        self.config.voice = voice
                        print(f"🎭 Voice set to: {self.SUPPORTED_VOICES[voice]}")
                        return True
                    elif voice == 'female' and ('female' in name_lower or 'woman' in name_lower):
                        self.engine.setProperty('voice', v.id)
                        self.current_voice = voice
                        self.config.voice = voice
                        print(f"🎭 Voice set to: {self.SUPPORTED_VOICES[voice]}")
                        return True
                    elif voice == 'child' and 'child' in name_lower:
                        self.engine.setProperty('voice', v.id)
                        self.current_voice = voice
                        self.config.voice = voice
                        print(f"🎭 Voice set to: {self.SUPPORTED_VOICES[voice]}")
                        return True
                
                # If no specific voice found, use first available
                self.engine.setProperty('voice', self.voices[0].id)
                print(f"⚠️  Voice type '{voice}' not found, using default")
                return True
            else:
                # Assume it's a voice ID
                self.engine.setProperty('voice', voice)
                self.current_voice = voice
                print(f"🎭 Voice set to ID: {voice}")
                return True
                
        except Exception as e:
            print(f"❌ Error setting voice: {e}")
            return False
    
    def set_language(self, language_code: str) -> bool:
        """
        Set the language for speech synthesis.
        Note: Language support depends on installed voices.
        
        Args:
            language_code: Language code (e.g., 'en', 'ur', 'hi')
            
        Returns:
            True if language is supported
        """
        if language_code in self.SUPPORTED_LANGUAGES:
            self.current_language = language_code
            self.config.language = language_code
            print(f"🌍 TTS language set to: {self.SUPPORTED_LANGUAGES[language_code]}")
            return True
        
        print(f"❌ Unsupported language: {language_code}")
        return False
    
    def get_supported_voices(self) -> Dict[str, str]:
        """Get list of supported voice types"""
        return self.SUPPORTED_VOICES.copy()
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices from the engine"""
        if not self.voices:
            return []
        
        return [
            {
                'id': voice.id,
                'name': voice.name,
                'languages': voice.languages,
                'gender': getattr(voice, 'gender', 'unknown')
            }
            for voice in self.voices
        ]
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.SUPPORTED_LANGUAGES.copy()
    
    def synthesize(self, text: str) -> Optional[AudioOutput]:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            AudioOutput or None if synthesis failed
        """
        if not self.is_loaded or not self.engine:
            print("❌ TTS engine not loaded")
            return None
        
        if not text or not text.strip():
            print("❌ Empty text")
            return None
        
        try:
            start_time = time.time()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Set properties
                self.engine.setProperty('rate', self.config.rate)
                self.engine.setProperty('volume', self.config.volume)
                
                # Save to file
                self.engine.save_to_file(text, temp_path)
                self.engine.runAndWait()
                
                # Read the generated audio file
                with wave.open(temp_path, 'rb') as wav_file:
                    sample_rate = wav_file.getframerate()
                    n_frames = wav_file.getnframes()
                    audio_data = wav_file.readframes(n_frames)
                    
                    # Convert to numpy array
                    audio_np = np.frombuffer(audio_data, dtype=np.int16)
                    duration = n_frames / float(sample_rate)
                
                elapsed = time.time() - start_time
                
                output = AudioOutput(
                    audio_data=audio_np,
                    sample_rate=sample_rate,
                    duration=duration
                )
                
                print(f"🔊 Synthesized: {text[:50]}...")
                return output
                
            finally:
                # Clean up
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Synthesis error: {e}")
            # Fallback to simulated audio
            return self._generate_simulated_audio(text)
    
    def _generate_simulated_audio(self, text: str) -> AudioOutput:
        """Generate simulated audio when pyttsx3 fails"""
        sample_rate = 22050
        duration = len(text) * 0.1  # 100ms per character
        samples = int(duration * sample_rate)
        
        # Generate a simple tone
        t = np.linspace(0, duration, samples)
        frequency = 440  # A4 note
        audio_data = (np.sin(2 * np.pi * frequency * t) * 32767 * 0.5).astype(np.int16)
        
        return AudioOutput(
            audio_data=audio_data,
            sample_rate=sample_rate,
            duration=duration
        )
    
    def speak(self, text: str, play: bool = True) -> Optional[AudioOutput]:
        """
        Speak text aloud.
        
        Args:
            text: Text to speak
            play: Whether to play the audio immediately
            
        Returns:
            AudioOutput or None if failed
        """
        if not self.is_loaded or not self.engine:
            print("❌ TTS engine not loaded")
            return None
        
        try:
            if play:
                # Speak directly
                self.engine.say(text)
                self.engine.runAndWait()
            
            # Also return the audio output
            return self.synthesize(text)
            
        except Exception as e:
            print(f"❌ Error speaking text: {e}")
            return None
    
    def stop(self) -> bool:
        """Stop current speech"""
        if self.engine:
            try:
                self.engine.stop()
                return True
            except:
                pass
        return False
    
    def is_speaking(self) -> bool:
        """Check if TTS is currently speaking"""
        if self.engine:
            return self.engine._inLoop
        return False
    
    def set_rate(self, rate: int) -> bool:
        """Set speech rate (words per minute)"""
        if self.engine:
            self.engine.setProperty('rate', rate)
            self.config.rate = rate
            return True
        return False
    
    def set_volume(self, volume: float) -> bool:
        """Set volume (0.0 to 1.0)"""
        if 0.0 <= volume <= 1.0 and self.engine:
            self.engine.setProperty('volume', volume)
            self.config.volume = volume
            return True
        return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the TTS engine"""
        return {
            'engine': 'pyttsx3' if self.engine else 'none',
            'is_loaded': self.is_loaded,
            'current_voice': self.current_voice,
            'current_language': self.current_language,
            'available_voices': len(self.voices)
        }
