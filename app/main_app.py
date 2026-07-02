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

# Import screens
from app.screens.chat import ChatScreen


class HomeScreen(MDScreen):
    """Home screen with AI Chat, Documents, Voice, etc. cards"""
    pass


class DocumentScreen(MDScreen):
    """Document AI screen"""
    pass


class VoiceScreen(MDScreen):
    """Voice Assistant screen"""
    pass


class ImageScreen(MDScreen):
    """Image AI screen"""
    pass


class KnowledgeScreen(MDScreen):
    """Knowledge Base screen"""
    pass


class SearchScreen(MDScreen):
    """Search screen"""
    pass


class SettingsScreen(MDScreen):
    """Settings screen"""
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
        self.screen_manager.add_widget(DocumentScreen(name='documents'))
        self.screen_manager.add_widget(VoiceScreen(name='voice'))
        self.screen_manager.add_widget(ImageScreen(name='images'))
        self.screen_manager.add_widget(KnowledgeScreen(name='knowledge'))
        self.screen_manager.add_widget(SearchScreen(name='search'))
        self.screen_manager.add_widget(SettingsScreen(name='settings'))
    
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
            
            print("✅ Runtime components initialized")
            
        except Exception as e:
            print(f"⚠️  Error initializing runtime: {e}")
            # Create dummy instances
            self.context_manager = None
            self.generation_engine = None
            self.inference_engine = None
            self.memory_manager = None
            self.scheduler = None
            self.tokenizer = None
            self.kv_cache = None
    
    def build(self):
        """Build the application"""
        print("🎨 Building TurboMind AI...")
        
        # Load KV language files
        self.load_kv_files()
        
        return self.screen_manager
    
    def load_kv_files(self):
        """Load all KV language files"""
        kv_files = [
            'app/screens/home.kv',
            'app/screens/chat.kv',
            'app/screens/documents.kv',
            'app/screens/voice.kv',
            'app/screens/images.kv',
            'app/screens/knowledge.kv',
            'app/screens/search.kv',
            'app/screens/settings.kv',
        ]
        
        for kv_file in kv_files:
            try:
                Builder.load_file(kv_file)
                print(f"✅ Loaded: {kv_file}")
            except Exception as e:
                print(f"⚠️  Could not load {kv_file}: {e}")
    
    def on_start(self):
        """Called when the app starts"""
        print("🚀 TurboMind AI started!")
        
        # Check platform
        if platform == 'android':
            print("📱 Running on Android")
        else:
            print("💻 Running on desktop")
        
        # Initialize first conversation
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
                md_bg_color: app.theme_cls.bg_normal
                
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
                    text: "Talk with AI"
                    halign: 'center'
                    font_style: 'Caption'
                    theme_text_color: "Secondary"
                
                MDRaisedButton:
                    text: "Open"
                    pos_hint: {'center_x': 0.5}
                    on_press: root.manager.current = 'chat'
            
            MDCard:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(10)
                elevation: 5
                radius: dp(15)
                md_bg_color: app.theme_cls.bg_normal
                
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
                    text: "Analyze PDFs, Docs"
                    halign: 'center'
                    font_style: 'Caption'
                    theme_text_color: "Secondary"
                
                MDRaisedButton:
                    text: "Open"
                    pos_hint: {'center_x': 0.5}
                    on_press: root.manager.current = 'documents'
            
            MDCard:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(10)
                elevation: 5
                radius: dp(15)
                md_bg_color: app.theme_cls.bg_normal
                
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
            
            MDCard:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(10)
                elevation: 5
                radius: dp(15)
                md_bg_color: app.theme_cls.bg_normal
                
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
                    text: "OCR & Vision"
                    halign: 'center'
                    font_style: 'Caption'
                    theme_text_color: "Secondary"
                
                MDRaisedButton:
                    text: "Open"
                    pos_hint: {'center_x': 0.5}
                    on_press: root.manager.current = 'images'
            
            MDCard:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(10)
                elevation: 5
                radius: dp(15)
                md_bg_color: app.theme_cls.bg_normal
                
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
            
            MDCard:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(10)
                elevation: 5
                radius: dp(15)
                md_bg_color: app.theme_cls.bg_normal
                
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
        
        MDBottomAppBar:
            MDTopAppBar:
                icon: "cog"
                type: "bottom"
                on_action_button: root.manager.current = 'settings'
''')
