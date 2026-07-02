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
from kivymd.uix.screen import MDScreen

# Import actual screens from app.screens
from app.screens.chat import ChatScreen
from app.screens.documents import DocumentsScreen
from app.screens.vision import VisionScreen
from app.screens.knowledge import KnowledgeScreen
from app.screens.models import ModelsScreen
from app.screens.voice import VoiceScreen
from app.screens.settings import SettingsScreen
from app.screens.search import SearchScreen


class HomeScreen(MDScreen):
    """Home screen with AI Chat, Documents, Voice, etc. cards"""
    pass


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
        
        # Register screens
        self.screen_manager.add_widget(HomeScreen(name='home'))
        self.screen_manager.add_widget(ChatScreen(name='chat'))
        self.screen_manager.add_widget(DocumentsScreen(name='documents'))
        self.screen_manager.add_widget(VisionScreen(name='vision'))
        self.screen_manager.add_widget(KnowledgeScreen(name='knowledge'))
        self.screen_manager.add_widget(ModelsScreen(name='models'))
        self.screen_manager.add_widget(VoiceScreen(name='voice'))
        self.screen_manager.add_widget(SettingsScreen(name='settings'))
        self.screen_manager.add_widget(SearchScreen(name='search'))
    
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
            
            print(" Runtime components initialized")
            
        except Exception as e:
            print(f" Error initializing runtime: {e}")
            self.context_manager = None
            self.generation_engine = None
            self.inference_engine = None
            self.memory_manager = None
            self.scheduler = None
            self.tokenizer = None
            self.kv_cache = None
    
    def build(self):
        """Build the application"""
        print(" Building TurboMind AI...")
        self.load_kv_files()
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
                print(f" Loaded: {kv_file}")
            except Exception as e:
                print(f" Could not load {kv_file}: {e}")
    
    def on_start(self):
        """Called when the app starts"""
        print(" TurboMind AI started!")
        if platform == 'android':
            print(" Running on Android")
        else:
            print(" Running on desktop")
        
        if self.context_manager:
            self.context_manager.create_conversation(title="Welcome")


# KV Language for Home Screen
Builder.load_string('''
<HomeScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(20)
        
        MDTopAppBar:
            title: "TurboMind AI"
            elevation: 4
            
        MDLabel:
            text: "Welcome to TurboMind AI"
            halign: 'center'
            font_style: 'H4'
            size_hint_y: None
            height: self.texture_size[1]
        
        MDLabel:
            text: "A 100% Offline AI Assistant"
            halign: 'center'
            font_style: 'Subtitle1'
            theme_text_color: "Secondary"
            size_hint_y: None
            height: self.texture_size[1]
        
        MDGridLayout:
            cols: 2
            spacing: dp(20)
            adaptive_height: True
            
            MDCard:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(10)
                elevation: 5
                radius: dp(15)
                md_bg_color: 0.1, 0.1, 0.1, 0.6
                
                MDIcon:
                    icon: "chat"
                    size: "64sp"
                    halign: 'center'
                    pos_hint: {'center_x': 0.5}
                    theme_text_color: "Primary"
                
                MDLabel:
                    text: "AI Chat"
                    halign: 'center'
                    font_style: 'H6'
                
                MDLabel:
                    text: "Talk with AI Assistant"
                    halign: 'center'
                    font_style: 'Caption'
                    theme_text_color: "Secondary"
                
                MDRaisedButton:
                    text: "Open"
                    pos_hint: {'center_x': 0.5}
                    on_press: root.manager.current = 'chat'
                    elevation: 2
            
            MDCard:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(10)
                elevation: 5
                radius: dp(15)
                md_bg_color: 0.1, 0.1, 0.1, 0.6
                
                MDIcon:
                    icon: "file-document"
                    size: "64sp"
                    halign: 'center'
                    pos_hint: {'center_x': 0.5}
                    theme_text_color: "Primary"
                
                MDLabel:
                    text: "Documents"
                    halign: 'center'
                    font_style: 'H6'
                
                MDLabel:
                    text: "Analyze PDFs, Docs, etc."
                    halign: 'center'
                    font_style: 'Caption'
                    theme_text_color: "Secondary"
                
                MDRaisedButton:
                    text: "Open"
                    pos_hint: {'center_x': 0.5}
                    on_press: root.manager.current = 'documents'
                    elevation: 2
            
            MDCard:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(10)
                elevation: 5
                radius: dp(15)
                md_bg_color: 0.1, 0.1, 0.1, 0.6
                
                MDIcon:
                    icon: "microphone"
                    size: "64sp"
                    halign: 'center'
                    pos_hint: {'center_x': 0.5}
                    theme_text_color: "Primary"
                
                MDLabel:
                    text: "Voice"
                    halign: 'center'
                    font_style: 'H6'
                
                MDLabel:
                    text: "Voice Assistant"
                    halign: 'center'
                    font_style: 'Caption'
                    theme_text_color: "Secondary"
                
                MDRaisedButton:
                    text: "Open"
                    pos_hint: {'center_x': 0.5}
                    on_press: root.manager.current = 'voice'
                    elevation: 2
            
            MDCard:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(10)
                elevation: 5
                radius: dp(15)
                md_bg_color: 0.1, 0.1, 0.1, 0.6
                
                MDIcon:
                    icon: "image"
                    size: "64sp"
                    halign: 'center'
                    pos_hint: {'center_x': 0.5}
                    theme_text_color: "Primary"
                
                MDLabel:
                    text: "Images"
                    halign: 'center'
                    font_style: 'H6'
                
                MDLabel:
                    text: "OCR & Vision AI"
                    halign: 'center'
                    font_style: 'Caption'
                    theme_text_color: "Secondary"
                
                MDRaisedButton:
                    text: "Open"
                    pos_hint: {'center_x': 0.5}
                    on_press: root.manager.current = 'vision'
                    elevation: 2
            
            MDCard:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(10)
                elevation: 5
                radius: dp(15)
                md_bg_color: 0.1, 0.1, 0.1, 0.6
                
                MDIcon:
                    icon: "brain"
                    size: "64sp"
                    halign: 'center'
                    pos_hint: {'center_x': 0.5}
                    theme_text_color: "Primary"
                
                MDLabel:
                    text: "Knowledge"
                    halign: 'center'
                    font_style: 'H6'
                
                MDLabel:
                    text: "Knowledge Base"
                    halign: 'center'
                    font_style: 'Caption'
                    theme_text_color: "Secondary"
                
                MDRaisedButton:
                    text: "Open"
                    pos_hint: {'center_x': 0.5}
                    on_press: root.manager.current = 'knowledge'
                    elevation: 2
            
            MDCard:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(10)
                elevation: 5
                radius: dp(15)
                md_bg_color: 0.1, 0.1, 0.1, 0.6
                
                MDIcon:
                    icon: "cpu-64-bit"
                    size: "64sp"
                    halign: 'center'
                    pos_hint: {'center_x': 0.5}
                    theme_text_color: "Primary"
                
                MDLabel:
                    text: "Models"
                    halign: 'center'
                    font_style: 'H6'
                
                MDLabel:
                    text: "Model Manager"
                    halign: 'center'
                    font_style: 'Caption'
                    theme_text_color: "Secondary"
                
                MDRaisedButton:
                    text: "Open"
                    pos_hint: {'center_x': 0.5}
                    on_press: root.manager.current = 'models'
                    elevation: 2
            
            MDCard:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(10)
                elevation: 5
                radius: dp(15)
                md_bg_color: 0.1, 0.1, 0.1, 0.6
                
                MDIcon:
                    icon: "magnify"
                    size: "64sp"
                    halign: 'center'
                    pos_hint: {'center_x': 0.5}
                    theme_text_color: "Primary"
                
                MDLabel:
                    text: "Search"
                    halign: 'center'
                    font_style: 'H6'
                
                MDLabel:
                    text: "Semantic Search"
                    halign: 'center'
                    font_style: 'Caption'
                    theme_text_color: "Secondary"
                
                MDRaisedButton:
                    text: "Open"
                    pos_hint: {'center_x': 0.5}
                    on_press: root.manager.current = 'search'
                    elevation: 2
        
        MDBottomAppBar:
            MDTopAppBar:
                icon: "cog"
                type: "bottom"
                on_action_button: root.manager.current = 'settings'
''')
