#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Main Kivy Application
=====================================
Main KivyMD application for TurboMind AI
"""

from kivy.lang import Builder
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

# Import all screens from app.screens
from app.screens.home import HomeScreen
from app.screens.chat import ChatScreen
from app.screens.documents import DocumentsScreen
from app.screens.vision import VisionScreen
from app.screens.knowledge import KnowledgeScreen
from app.screens.models import ModelsScreen
from app.screens.voice import VoiceScreen
from app.screens.settings import SettingsScreen
from app.screens.search import SearchScreen


class TurboMindApp(MDApp):
    """Main TurboMind AI Application"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "TurboMind AI"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Cyan"
        
        # Initialize runtime components
        self._init_runtime()
        
        # Screen manager
        self.screen_manager = MDScreenManager()
    
    def _init_runtime(self):
        """Initialize runtime components"""
        try:
            from runtime.context_manager import ContextManager
            from runtime.generation_engine import GenerationEngine
            from runtime.inference_engine import InferenceEngine
            from runtime.memory_manager import MemoryManager
            from runtime.scheduler import Scheduler
            from runtime.tokenizer import Tokenizer
            from runtime.kv_cache import KVCacheManager
            
            # Create runtime instances
            self.context_manager = ContextManager()
            self.generation_engine = GenerationEngine()
            self.inference_engine = InferenceEngine()
            self.memory_manager = MemoryManager()
            self.scheduler = Scheduler()
            self.tokenizer = Tokenizer()
            self.kv_cache = KVCacheManager()
            
            print("Runtime components initialized")
            
        except Exception as e:
            print(f"Error initializing runtime: {e}")
            self.context_manager = None
            self.generation_engine = None
            self.inference_engine = None
            self.memory_manager = None
            self.scheduler = None
            self.tokenizer = None
            self.kv_cache = None
    
    def build(self):
        """Build the application"""
        print("Building TurboMind AI...")
        self.load_kv_files()
        
        # Register all screens
        self.screen_manager.add_widget(HomeScreen(name='home'))
        self.screen_manager.add_widget(ChatScreen(name='chat'))
        self.screen_manager.add_widget(DocumentsScreen(name='documents'))
        self.screen_manager.add_widget(VisionScreen(name='vision'))
        self.screen_manager.add_widget(KnowledgeScreen(name='knowledge'))
        self.screen_manager.add_widget(ModelsScreen(name='models'))
        self.screen_manager.add_widget(VoiceScreen(name='voice'))
        self.screen_manager.add_widget(SettingsScreen(name='settings'))
        self.screen_manager.add_widget(SearchScreen(name='search'))
        
        return self.screen_manager
    
    def load_kv_files(self):
        """Load all KV language files"""
        kv_files = [
            'app/screens/home.kv',
            'app/screens/chat.kv',
            'app/screens/documents.kv',
            'app/screens/vision.kv',
            'app/screens/knowledge.kv',
            'app/screens/models.kv',
            'app/screens/voice.kv',
            'app/screens/settings.kv',
            'app/screens/search.kv',
        ]
        
        for kv_file in kv_files:
            try:
                Builder.load_file(kv_file)
                print(f"Loaded: {kv_file}")
            except Exception as e:
                print(f"Could not load {kv_file}: {e}")
    
    def on_start(self):
        """Called when the app starts"""
        print("TurboMind AI started!")
        if platform == 'android':
            print("Running on Android")
        else:
            print("Running on desktop")
        
        if self.context_manager:
            self.context_manager.create_conversation(title="Welcome")


if __name__ == "__main__":
    TurboMindApp().run()
