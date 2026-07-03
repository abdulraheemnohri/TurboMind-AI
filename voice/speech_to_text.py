#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Speech to Text
==============================
Converts speech to text using offline VOSK models
"""

import os
import json
import time
import wave
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
import numpy as np


@dataclass
class SpeechResult:
    """Result of speech recognition"""
    text: str
    confidence: float = 0.0
    language: str = "en"
    duration: float = 0.0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'text': self.text,
            'confidence': self.confidence,
            'language': self.language,
            'duration': self.duration,
            'timestamp': self.timestamp
        }


@dataclass
class AudioConfig:
    """Audio configuration for speech recognition"""
    sample_rate: int = 16000
    channels: int = 1
    sample_width: int = 2  # bytes
    max_duration: float = 30.0  # seconds
    silence_threshold: float = 0.01
    phrase_time_limit: float = 10.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'sample_width': self.sample_width,
            'max_duration': self.max_duration,
            'silence_threshold': self.silence_threshold,
            'phrase_time_limit': self.phrase_time_limit
        }


class SpeechToText:
    """
    Converts speech to text using offline VOSK models.
    VOSK is a completely offline speech recognition toolkit.
    Supports multiple languages including Urdu, English, Hindi, etc.
    """
    
    # Supported languages with VOSK model names
    SUPPORTED_LANGUAGES = {
        'en': {'name': 'English', 'model': 'vosk-model-en-us-0.22'},  # Small English model
        'ur': {'name': 'Urdu', 'model': 'vosk-model-ur-0.22'},  # Urdu model
        'hi': {'name': 'Hindi', 'model': 'vosk-model-hi-0.22'},  # Hindi model
        'es': {'name': 'Spanish', 'model': 'vosk-model-es-0.22'},
        'fr': {'name': 'French', 'model': 'vosk-model-fr-0.22'},
        'de': {'name': 'German', 'model': 'vosk-model-de-0.22'},
        'it': {'name': 'Italian', 'model': 'vosk-model-it-0.22'},
        'pt': {'name': 'Portuguese', 'model': 'vosk-model-pt-0.22'},
        'ru': {'name': 'Russian', 'model': 'vosk-model-ru-0.22'},
        'zh': {'name': 'Chinese', 'model': 'vosk-model-cn-0.22'},
        'ja': {'name': 'Japanese', 'model': 'vosk-model-ja-0.22'},
        'ar': {'name': 'Arabic', 'model': 'vosk-model-ar-0.22'}
    }
    
    # Small models for better performance on mobile
    SMALL_MODELS = {
        'en': 'vosk-model-small-en-us-0.15',
        'ur': 'vosk-model-small-ur-0.15',
        'hi': 'vosk-model-small-hi-0.15',
    }
    
    def __init__(self, model_path: Optional[str] = None, use_small_model: bool = True):
        """
        Initialize the speech to text engine.
        
        Args:
            model_path: Path to VOSK model directory
            use_small_model: Whether to use small models (better for mobile)
        """
        self.model_path = Path(model_path) if model_path else None
        self.is_loaded = False
        self.current_language = 'en'
        self.use_small_model = use_small_model
        self.audio_config = AudioConfig()
        
        # VOSK components
        self.model = None
        self.recognizer = None
        
        # Try to initialize with default model
        if not model_path:
            self._try_default_model()
        else:
            self.load_model(str(model_path))
            
        print("🎤 Speech to Text initialized")
    
    def _try_default_model(self) -> None:
        """Try to find and load a default VOSK model"""
        # Check common model locations
        possible_paths = [
            'vosk-model-small-en-us-0.15',
            'vosk-model-en-us-0.22',
            '/data/vosk-model-small-en-us-0.15',
            '/sdcard/vosk-model-small-en-us-0.15'
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                self.load_model(path)
                return
        
        print("⚠️  No default VOSK model found. Please download a model.")
        print("⚠️  Download models from: https://alphacephei.com/vosk/models")
        print("⚠️  For English: vosk-model-small-en-us-0.15")
        print("⚠️  For Urdu: vosk-model-ur-0.22")
    
    def load_model(self, model_path: str) -> bool:
        """
        Load VOSK speech recognition model.
        
        Args:
            model_path: Path to VOSK model directory
            
        Returns:
            True if model loaded successfully
        """
        try:
            import vosk
            
            self.model_path = Path(model_path)
            
            if not self.model_path.exists():
                print(f"❌ Model directory not found: {model_path}")
                return False
            
            # Load the model
            self.model = vosk.Model(str(self.model_path))
            
            # Create recognizer
            self.recognizer = vosk.KaldiRecognizer(
                self.model,
                self.audio_config.sample_rate
            )
            self.recognizer.SetWords(True)
            
            self.is_loaded = True
            print(f"✅ VOSK model loaded from: {model_path}")
            return True
            
        except ImportError:
            print("⚠️  VOSK not installed. Install with: pip install vosk")
            print("⚠️  Falling back to simulated speech recognition")
            self.is_loaded = False
            return False
        except Exception as e:
            print(f"❌ Error loading VOSK model: {e}")
            self.is_loaded = False
            return False
    
    def unload_model(self) -> bool:
        """Unload VOSK model"""
        try:
            self.model = None
            self.recognizer = None
            self.is_loaded = False
            print("🗑️  VOSK model unloaded")
            return True
        except Exception as e:
            print(f"❌ Error unloading model: {e}")
            return False
    
    def set_language(self, language_code: str) -> bool:
        """
        Set the language for speech recognition.
        This will automatically load the appropriate model if available.
        
        Args:
            language_code: Language code (e.g., 'en', 'ur', 'hi')
            
        Returns:
            True if language is supported
        """
        if language_code in self.SUPPORTED_LANGUAGES:
            self.current_language = language_code
            
            # Try to load the model for this language
            if self.use_small_model and language_code in self.SMALL_MODELS:
                model_name = self.SMALL_MODELS[language_code]
            else:
                model_name = self.SUPPORTED_LANGUAGES[language_code]['model']
            
            # Check if model exists
            if Path(model_name).exists():
                self.load_model(model_name)
            else:
                print(f"⚠️  Model for {language_code} not found: {model_name}")
                print(f"⚠️  Please download from: https://alphacephei.com/vosk/models")
            
            print(f"🌍 Language set to: {self.SUPPORTED_LANGUAGES[language_code]['name']}")
            return True
        
        print(f"❌ Unsupported language: {language_code}")
        return False
    
    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """Get dictionary of supported languages with model info"""
        return self.SUPPORTED_LANGUAGES.copy()
    
    def recognize_speech(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Optional[SpeechResult]:
        """
        Recognize speech from audio data.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of audio data
            
        Returns:
            SpeechResult or None if recognition failed
        """
        if not self.is_loaded or not self.recognizer:
            print("❌ Model not loaded")
            return None
        
        try:
            import vosk
            
            start_time = time.time()
            
            # Convert numpy array to bytes
            if audio_data.dtype == np.int16:
                audio_bytes = audio_data.tobytes()
            else:
                # Convert to int16
                audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()
            
            # Accept the audio data
            if self.recognizer.AcceptWaveform(audio_bytes):
                result = json.loads(self.recognizer.Result())
                text = result.get('text', '')
                confidence = 1.0  # VOSK doesn't provide confidence by default
            else:
                result = json.loads(self.recognizer.PartialResult())
                text = result.get('partial', '')
                confidence = 0.8  # Partial result confidence
            
            duration = len(audio_data) / float(sample_rate)
            elapsed = time.time() - start_time
            
            if text and text.strip():
                result_obj = SpeechResult(
                    text=text.strip(),
                    confidence=confidence,
                    language=self.current_language,
                    duration=duration
                )
                print(f"🎤 Recognized: {text}")
                return result_obj
            else:
                print("❌ No speech detected")
                return None
                
        except Exception as e:
            print(f"❌ Recognition error: {e}")
            return None
    
    def recognize_from_file(self, audio_file_path: str) -> Optional[SpeechResult]:
        """
        Recognize speech from audio file.
        
        Args:
            audio_file_path: Path to audio file (WAV format)
            
        Returns:
            SpeechResult or None if recognition failed
        """
        try:
            with wave.open(audio_file_path, 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                
                # Read frames
                frames = wav_file.readframes(wav_file.getnframes())
                
                # Convert to numpy array
                if sample_width == 2:
                    audio_data = np.frombuffer(frames, dtype=np.int16)
                else:
                    audio_data = np.frombuffer(frames, dtype=np.int8) * 256
                
                # Convert stereo to mono if needed
                if n_channels > 1:
                    audio_data = audio_data.reshape(-1, n_channels)
                    audio_data = audio_data.mean(axis=1).astype(np.int16)
            
            return self.recognize_speech(audio_data, sample_rate)
            
        except Exception as e:
            print(f"❌ Error reading audio file: {e}")
            return None
    
    def start_listening(self, callback: Optional[Callable] = None, timeout: float = 30.0) -> bool:
        """
        Start listening to microphone input in real-time.
        
        Args:
            callback: Function to call with recognition results
            timeout: Maximum listening duration in seconds
            
        Returns:
            True if listening started successfully
        """
        if not self.is_loaded:
            print("❌ Model not loaded")
            return False
        
        try:
            import pyaudio
            
            print("🎤 Listening... (Press Ctrl+C to stop)")
            
            # Audio stream configuration
            chunk_size = 4096
            format = pyaudio.paInt16
            channels = 1
            rate = self.audio_config.sample_rate
            
            # Initialize PyAudio
            p = pyaudio.PyAudio()
            
            # Open stream
            stream = p.open(
                format=format,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=chunk_size
            )
            
            start_time = time.time()
            all_audio = bytearray()
            
            print("🎤 Start speaking...")
            
            try:
                while True:
                    if time.time() - start_time > timeout:
                        print("⏰ Listening timeout")
                        break
                    
                    # Read audio data
                    data = stream.read(chunk_size, exception_on_overflow=False)
                    all_audio.extend(data)
                    
                    # Process in real-time
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get('text', '')
                        if text and text.strip() and callback:
                            result_obj = SpeechResult(
                                text=text.strip(),
                                confidence=1.0,
                                language=self.current_language,
                                duration=0.0
                            )
                            callback(result_obj)
                        
                    # Check for partial results
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get('partial', '')
                    
            except KeyboardInterrupt:
                print("
🛑 Listening stopped by user")
            finally:
                # Clean up
                stream.stop_stream()
                stream.close()
                p.terminate()
                
                # Process all collected audio
                if all_audio and len(all_audio) > 0:
                    audio_np = np.frombuffer(all_audio, dtype=np.int16)
                    result = self.recognize_speech(audio_np, rate)
                    if result and callback:
                        callback(result)
                
            return True
            
        except ImportError:
            print("⚠️  PyAudio not installed. Install with: pip install pyaudio")
            print("⚠️  Cannot use microphone without PyAudio")
            return False
        except Exception as e:
            print(f"❌ Listening error: {e}")
            return False
    
    def stop_listening(self) -> bool:
        """Stop listening to microphone input"""
        print("🛑 Listening stopped")
        return True
    
    def process_audio_chunk(self, audio_chunk: np.ndarray, sample_rate: int = 16000) -> Optional[SpeechResult]:
        """
        Process a chunk of audio data for streaming recognition.
        
        Args:
            audio_chunk: Audio chunk as numpy array
            sample_rate: Sample rate of audio data
            
        Returns:
            SpeechResult or None if no speech detected
        """
        return self.recognize_speech(audio_chunk, sample_rate)
    
    def get_audio_config(self) -> AudioConfig:
        """Get current audio configuration"""
        return self.audio_config
    
    def set_audio_config(self, config: AudioConfig) -> None:
        """Set audio configuration"""
        self.audio_config = config
        print("⚙️  Audio configuration updated")
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.is_loaded
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            'model_path': str(self.model_path) if self.model_path else None,
            'is_loaded': self.is_loaded,
            'current_language': self.current_language,
            'sample_rate': self.audio_config.sample_rate,
            'use_small_model': self.use_small_model
        }
    
    def test_microphone(self) -> bool:
        """
        Test microphone functionality.
        
        Returns:
            True if microphone is working
        """
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024
            )
            
            # Read a small chunk
            data = stream.read(1024)
            
            # Clean up
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            print("🎤 Microphone test: OK")
            return True
            
        except ImportError:
            print("⚠️  PyAudio not installed. Cannot test microphone.")
            return False
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            return False
    
    def download_model(self, language_code: str = 'en', small: bool = True) -> bool:
        """
        Download VOSK model (requires internet - for setup only)
        
        Args:
            language_code: Language code
            small: Whether to download small model
            
        Returns:
            True if download successful
        """
        try:
            import vosk
            import urllib.request
            import zipfile
            import shutil
            
            print("⚠️  WARNING: This requires internet connection!")
            print("⚠️  This is only for initial setup. The app itself is offline.")
            
            if small and language_code in self.SMALL_MODELS:
                model_url = f"https://alphacephei.com/vosk/models/{self.SMALL_MODELS[language_code]}.zip"
                model_name = self.SMALL_MODELS[language_code]
            elif language_code in self.SUPPORTED_LANGUAGES:
                model_url = f"https://alphacephei.com/vosk/models/{self.SUPPORTED_LANGUAGES[language_code]['model']}.zip"
                model_name = self.SUPPORTED_LANGUAGES[language_code]['model']
            else:
                print(f"❌ Unsupported language: {language_code}")
                return False
            
            # Download model
            print(f"📥 Downloading model: {model_name}")
            temp_zip = f"{model_name}.zip"
            urllib.request.urlretrieve(model_url, temp_zip)
            
            # Extract
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall(model_name)
            
            # Clean up
            os.remove(temp_zip)
            
            print(f"✅ Model downloaded: {model_name}")
            
            # Load the model
            return self.load_model(model_name)
            
        except Exception as e:
            print(f"❌ Error downloading model: {e}")
            return False
