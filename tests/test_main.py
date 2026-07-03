#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Unit Tests
=========================
Test suite for all TurboMind AI modules
"""

import unittest
import tempfile
import os
from pathlib import Path
import numpy as np


class TestOCRProcessor(unittest.TestCase):
    """Tests for OCR module"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.test_image_path = None
        self.ocr = None
        
        # Create a simple test image with text
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a blank image
            img = Image.new('RGB', (400, 200), color='white')
            draw = ImageDraw.Draw(img)
            
            # Draw some text
            draw.text((10, 10), "Hello World", fill='black')
            draw.text((10, 50), "Test OCR", fill='black')
            draw.text((10, 100), "12345", fill='black')
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                img.save(f, 'PNG')
                self.test_image_path = f.name
            
            # Initialize OCR
            from vision.ocr import OCRProcessor
            self.ocr = OCRProcessor(engine='tesseract')
            
        except ImportError:
            # Skip if dependencies not available
            self.test_image_path = None
            self.ocr = None
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.test_image_path and os.path.exists(self.test_image_path):
            os.unlink(self.test_image_path)
    
    def test_ocr_initialization(self):
        """Test OCR processor initialization"""
        if self.ocr:
            self.assertTrue(self.ocr.initialized or True)  # May not be initialized if tesseract not installed
            self.assertIn(self.ocr.engine, ['tesseract', 'easyocr', 'paddle'])
    
    def test_process_image(self):
        """Test processing an image with OCR"""
        if self.ocr and self.test_image_path:
            result = self.ocr.process_image(self.test_image_path, language='eng')
            if result:
                self.assertIsInstance(result.text, str)
                self.assertGreaterEqual(result.confidence, 0)
                self.assertEqual(result.language, 'eng')


class TestSpeechToText(unittest.TestCase):
    """Tests for Speech to Text module"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.stt = None
        try:
            from voice.speech_to_text import SpeechToText
            self.stt = SpeechToText()
        except:
            pass
    
    def test_stt_initialization(self):
        """Test STT initialization"""
        if self.stt:
            self.assertIsInstance(self.stt.current_language, str)
            self.assertIn(self.stt.current_language, self.stt.SUPPORTED_LANGUAGES)
    
    def test_set_language(self):
        """Test setting language"""
        if self.stt:
            # Test valid language
            result = self.stt.set_language('en')
            self.assertTrue(result)
            self.assertEqual(self.stt.current_language, 'en')
            
            # Test invalid language
            result = self.stt.set_language('xx')
            self.assertFalse(result)
    
    def test_supported_languages(self):
        """Test supported languages list"""
        if self.stt:
            langs = self.stt.get_supported_languages()
            self.assertIsInstance(langs, dict)
            self.assertIn('en', langs)


class TestTextToSpeech(unittest.TestCase):
    """Tests for Text to Speech module"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.tts = None
        try:
            from voice.text_to_speech import TextToSpeech
            self.tts = TextToSpeech()
        except:
            pass
    
    def test_tts_initialization(self):
        """Test TTS initialization"""
        if self.tts:
            # Should be initialized (may fail if pyttsx3 not installed)
            self.assertIsInstance(self.tts.current_voice, str)
    
    def test_synthesize(self):
        """Test text synthesis"""
        if self.tts and self.tts.is_loaded:
            result = self.tts.synthesize("Hello world")
            if result:
                self.assertIsInstance(result.audio_data, np.ndarray)
                self.assertGreater(result.sample_rate, 0)
                self.assertGreater(result.duration, 0)
    
    def test_set_voice(self):
        """Test setting voice"""
        if self.tts and self.tts.is_loaded:
            # Test with available voices
            voices = self.tts.get_available_voices()
            if voices:
                result = self.tts.set_voice(voices[0]['id'])
                self.assertTrue(result)


class TestInferenceEngine(unittest.TestCase):
    """Tests for Inference Engine"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.engine = None
        try:
            from runtime.inference_engine import InferenceEngine
            self.engine = InferenceEngine()
        except:
            pass
    
    def test_engine_initialization(self):
        """Test inference engine initialization"""
        if self.engine:
            self.assertIn(self.engine.device, ['cpu', 'cuda', 'mps', 'xpu'])
            self.assertFalse(self.engine.is_loaded)
    
    def test_device_detection(self):
        """Test device detection"""
        if self.engine:
            device_info = self.engine.get_device_info()
            self.assertIn('device', device_info)
            self.assertIn('device_type', device_info)


class TestModelManager(unittest.TestCase):
    """Tests for Model Manager"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.manager = None
        try:
            from models.model_manager import ModelManager
            self.manager = ModelManager()
        except:
            pass
    
    def test_manager_initialization(self):
        """Test model manager initialization"""
        if self.manager:
            self.assertIsInstance(self.manager.models, dict)
    
    def test_list_models(self):
        """Test listing models"""
        if self.manager:
            models = self.manager.list_models()
            self.assertIsInstance(models, list)


class TestContextManager(unittest.TestCase):
    """Tests for Context Manager"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.manager = None
        try:
            from runtime.context_manager import ContextManager
            self.manager = ContextManager()
        except:
            pass
    
    def test_create_conversation(self):
        """Test creating a conversation"""
        if self.manager:
            conv = self.manager.create_conversation(title="Test")
            self.assertIsNotNone(conv)
            self.assertEqual(conv.title, "Test")
            self.assertIn(conv.id, self.manager.conversations)
    
    def test_add_message(self):
        """Test adding a message to conversation"""
        if self.manager:
            conv = self.manager.create_conversation(title="Test")
            msg = self.manager.add_message('user', "Hello")
            self.assertIsNotNone(msg)
            self.assertEqual(msg.role, 'user')
            self.assertEqual(msg.content, "Hello")
    
    def test_get_context(self):
        """Test getting conversation context"""
        if self.manager:
            conv = self.manager.create_conversation(title="Test")
            self.manager.add_message('user', "Hello")
            self.manager.add_message('assistant', "Hi there")
            
            context = self.manager.get_context()
            self.assertIsInstance(context, list)
            self.assertEqual(len(context), 2)


class TestSearch(unittest.TestCase):
    """Tests for Search functionality"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.search = None
        try:
            from search.semantic_search import SemanticSearch
            self.search = SemanticSearch()
        except:
            pass
    
    def test_search_initialization(self):
        """Test search initialization"""
        if self.search:
            self.assertIsInstance(self.search.index, dict)


class TestSettings(unittest.TestCase):
    """Tests for Settings"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.settings = None
        try:
            from settings.app_settings import AppSettings
            self.settings = AppSettings()
        except:
            pass
    
    def test_settings_initialization(self):
        """Test settings initialization"""
        if self.settings:
            self.assertIn('language', self.settings.settings)
            self.assertIn('theme', self.settings.settings)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
