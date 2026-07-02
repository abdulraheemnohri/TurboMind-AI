#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Voice Screen
============================
Handles voice assistant UI
"""

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.metrics import dp
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDTextButton, MDFlatButton
from kivymd.uix.list import OneLineListItem, TwoLineListItem, ThreeLineListItem, MDList
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.card import MDCard
from kivymd.uix.filemanager import MDFileManager
from typing import Optional, Dict, Any, List
import os
from pathlib import Path
import time


class VoiceScreen(MDScreen):
    """Voice assistant screen for TurboMind AI"""
    
    conversation_list = ObjectProperty(None)
    status_label = ObjectProperty(None)
    input_field = ObjectProperty(None)
    listen_button = ObjectProperty(None)
    progress_bar = ObjectProperty(None)
    
    # Voice assistant components
    voice_assistant = None
    stt_engine = None
    tts_engine = None
    
    # Current state
    is_listening = BooleanProperty(False)
    is_speaking = BooleanProperty(False)
    current_language = StringProperty('en')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_runtime()
    
    def _init_runtime(self):
        """Initialize voice assistant components"""
        try:
            from voice.voice_assistant import VoiceAssistant
            from voice.speech_to_text import SpeechToText
            from voice.text_to_speech import TextToSpeech
            
            self.stt_engine = SpeechToText()
            self.tts_engine = TextToSpeech()
            self.voice_assistant = VoiceAssistant(self.stt_engine, self.tts_engine)
            
            # Set up callbacks
            self.voice_assistant.on_command(self._on_command_received)
            self.voice_assistant.on_response(self._on_response_received)
            self.voice_assistant.on_error(self._on_error)
            
            print("✅ Voice runtime initialized")
            self._update_ui()
        except Exception as e:
            print(f"⚠️  Error initializing voice runtime: {e}")
            Snackbar(text=f"Error: {str(e)}").open()
    
    def on_pre_enter(self, *args):
        """Called before entering the screen"""
        self._update_ui()
    
    def _update_ui(self):
        """Update UI with current state"""
        if not self.voice_assistant:
            return
        
        status = self.voice_assistant.get_status()
        
        if status['is_listening']:
            self.status_label.text = "🎤 Listening..."
            self.listen_button.text = "Stop Listening"
            self.listen_button.icon = "stop"
            self.listen_button.md_bg_color = (1, 0, 0, 1)  # Red
        else:
            self.status_label.text = "🤖 Ready"
            self.listen_button.text = "Start Listening"
            self.listen_button.icon = "mic"
            self.listen_button.md_bg_color = (0.21, 0.58, 0.94, 1)  # Primary color
        
        if status['is_speaking']:
            self.status_label.text = "🔊 Speaking..."
        
        # Update conversation display
        self._update_conversation()
    
    def _update_conversation(self):
        """Update the conversation display"""
        if not self.voice_assistant:
            return
        
        self.conversation_list.clear_widgets()
        
        conversation = self.voice_assistant.get_conversation()
        
        if not conversation:
            self.conversation_list.add_widget(MDLabel(
                text="No conversation yet. Start by speaking to TurboMind.",
                halign='center',
                theme_text_color='Secondary'
            ))
            return
        
        for item in conversation:
            if item['type'] == 'command':
                self.conversation_list.add_widget(TwoLineListItem(
                    text="You:",
                    secondary_text=item['text'],
                    theme_text_color='Primary',
                    bg_color=(0.1, 0.1, 0.1, 0.3)
                ))
            elif item['type'] == 'response':
                self.conversation_list.add_widget(TwoLineListItem(
                    text="TurboMind:",
                    secondary_text=item['text'],
                    theme_text_color='Secondary',
                    bg_color=(0.15, 0.15, 0.15, 0.2)
                ))
    
    def toggle_listening(self):
        """Toggle listening state"""
        if not self.voice_assistant:
            return
        
        if self.voice_assistant.is_active():
            self.stop_listening()
        else:
            self.start_listening()
    
    def start_listening(self):
        """Start listening"""
        if not self.voice_assistant:
            return
        
        self.is_listening = True
        self.status_label.text = "🎤 Listening..."
        self.listen_button.text = "Stop Listening"
        self.listen_button.icon = "stop"
        
        Clock.schedule_once(lambda dt: self._start_listening_background(), 0.1)
    
    def _start_listening_background(self):
        """Start listening in background"""
        try:
            # Start voice assistant
            self.voice_assistant.start()
            
            # Simulate receiving a command after a delay
            Clock.schedule_once(lambda dt: self._simulate_command(), 2)
            
        except Exception as e:
            self.status_label.text = f"❌ Error: {str(e)}"
            Snackbar(text=f"Error: {str(e)}").open()
            self.is_listening = False
            self._update_ui()
    
    def stop_listening(self):
        """Stop listening"""
        if not self.voice_assistant:
            return
        
        self.is_listening = False
        self.voice_assistant.stop()
        
        self.status_label.text = "🤖 Ready"
        self.listen_button.text = "Start Listening"
        self.listen_button.icon = "mic"
    
    def _simulate_command(self):
        """Simulate receiving a voice command for demo"""
        if not self.is_listening:
            return
        
        # Simulate different commands
        import random
        commands = [
            "Hello, how are you?",
            "What time is it?",
            "Tell me a joke",
            "What is the weather today?",
            "Calculate 5 plus 3",
            "Open the chat",
            "Help me with something"
        ]
        
        command = random.choice(commands)
        self._on_command_received({'command': command, 'intent': 'unknown'})
    
    def _on_command_received(self, command_data: Dict[str, Any]):
        """Handle received command"""
        Clock.schedule_once(lambda dt: self._process_command(command_data), 0.1)
    
    def _process_command(self, command_data: Dict[str, Any]):
        """Process the received command"""
        try:
            command_text = command_data.get('command', '')
            
            # Add to conversation display
            self.conversation_list.add_widget(TwoLineListItem(
                text="You:",
                secondary_text=command_text,
                theme_text_color='Primary',
                bg_color=(0.1, 0.1, 0.1, 0.3)
            ))
            
            # Scroll to bottom
            self._scroll_to_bottom()
            
            # Process command
            if command_text.lower() == "what time is it":
                response = self._get_time_response()
            elif command_text.lower() == "tell me a joke":
                response = self._get_joke_response()
            elif command_text.lower() == "hello" or command_text.lower() == "hi":
                response = self._get_greeting_response()
            else:
                response = self._get_generic_response(command_text)
            
            # Add response to conversation
            self.conversation_list.add_widget(TwoLineListItem(
                text="TurboMind:",
                secondary_text=response,
                theme_text_color='Secondary',
                bg_color=(0.15, 0.15, 0.15, 0.2)
            ))
            
            # Scroll to bottom
            self._scroll_to_bottom()
            
            # Speak the response
            self._speak_response(response)
            
        except Exception as e:
            print(f"❌ Error processing command: {e}")
            Snackbar(text=f"Error: {str(e)}").open()
    
    def _scroll_to_bottom(self):
        """Scroll conversation to bottom"""
        try:
            self.conversation_list.parent.scroll_y = 0
        except:
            pass
    
    def _speak_response(self, text: str):
        """Speak the response using TTS"""
        if not self.tts_engine:
            return
        
        self.is_speaking = True
        self.status_label.text = "🔊 Speaking..."
        
        Clock.schedule_once(lambda dt: self._speak_background(text), 0.1)
    
    def _speak_background(self, text: str):
        """Speak text in background"""
        try:
            # For demo, simulate speaking
            import time
            time.sleep(1)  # Simulate speech duration
            
            self.is_speaking = False
            self.status_label.text = "🤖 Ready"
            
        except Exception as e:
            self.status_label.text = f"❌ Error: {str(e)}"
            self.is_speaking = False
    
    def _on_response_received(self, response_data: Dict[str, Any]):
        """Handle received response"""
        pass  # Handled in _process_command
    
    def _on_error(self, error_message: str):
        """Handle error"""
        Snackbar(text=f"Error: {error_message}").open()
        self.status_label.text = f"❌ Error: {error_message}"
    
    def _get_time_response(self) -> str:
        """Get time response"""
        current_time = time.strftime("%I:%M %p")
        return f"The current time is {current_time}"
    
    def _get_joke_response(self) -> str:
        """Get joke response"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "What do you call a fake noodle? An impasta!",
            "How do you organize a space party? You planet!"
        ]
        import random
        return random.choice(jokes)
    
    def _get_greeting_response(self) -> str:
        """Get greeting response"""
        greetings = [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
            "Greetings! I'm at your service.",
            "Salam! Kaise ho?"
        ]
        import random
        return random.choice(greetings)
    
    def _get_generic_response(self, command: str) -> str:
        """Get generic response"""
        responses = [
            f"I heard you say: {command}",
            f"Interesting! You said: {command}",
            f"I understand you want: {command}"
        ]
        import random
        return random.choice(responses)
    
    def send_text_command(self):
        """Send command from text input"""
        if not self.input_field or not self.input_field.text:
            return
        
        command_text = self.input_field.text.strip()
        if not command_text:
            return
        
        # Clear input
        self.input_field.text = ""
        
        # Process as command
        self._on_command_received({'command': command_text, 'intent': 'unknown'})
    
    def clear_conversation(self):
        """Clear conversation history"""
        if not self.voice_assistant:
            return
        
        self.voice_assistant.clear_conversation()
        self.conversation_list.clear_widgets()
        
        self.conversation_list.add_widget(MDLabel(
            text="Conversation cleared. Start a new conversation.",
            halign='center',
            theme_text_color='Secondary'
        ))
        
        Snackbar(text="Conversation cleared").open()
    
    def set_language(self, language_code: str):
        """Set language for voice assistant"""
        if not self.voice_assistant:
            return
        
        if self.voice_assistant.set_language(language_code):
            self.current_language = language_code
            Snackbar(text=f"Language set to: {language_code}").open()
        else:
            Snackbar(text=f"Language not supported: {language_code}").open()
    
    def show_language_dialog(self):
        """Show language selection dialog"""
        if not self.voice_assistant:
            return
        
        languages = self.voice_assistant.stt_engine.get_supported_languages()
        
        dialog = MDDialog(
            title="Select Language",
            size_hint=(0.8, 0.6)
        )
        
        scroll = MDScrollView()
        list_view = MDList()
        
        for lang_code, lang_name in languages.items():
            list_view.add_widget(OneLineListItem(
                text=f"{lang_name} ({lang_code})",
                on_press=lambda x, code=lang_code: self._select_language(code, dialog)
            ))
        
        scroll.add_widget(list_view)
        dialog.add_widget(scroll)
        
        dialog.add_widget(MDFlatButton(
            text="CANCEL",
            on_press=dialog.dismiss
        ))
        
        dialog.open()
    
    def _select_language(self, language_code: str, dialog):
        """Select language and close dialog"""
        dialog.dismiss()
        self.set_language(language_code)
    
    def show_settings(self):
        """Show voice assistant settings"""
        if not self.voice_assistant:
            return
        
        dialog = MDDialog(
            title="Voice Assistant Settings",
            size_hint=(0.8, 0.5)
        )
        
        content = MDBoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10)
        )
        
        # Wake word detection
        wake_switch = MDTextButton(
            text="ON" if self.voice_assistant.wake_word_detection else "OFF",
            on_press=lambda x: self._toggle_wake_detection()
        )
        
        content.add_widget(MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40),
            children=[
                MDLabel(text="Wake Word Detection:", font_style='Body1'),
                wake_switch
            ]
        ))
        
        # Continuous listening
        cont_switch = MDTextButton(
            text="ON" if self.voice_assistant.continuous_listening else "OFF",
            on_press=lambda x: self._toggle_continuous_listening()
        )
        
        content.add_widget(MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40),
            children=[
                MDLabel(text="Continuous Listening:", font_style='Body1'),
                cont_switch
            ]
        ))
        
        # Language
        content.add_widget(MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40),
            children=[
                MDLabel(text="Language:", font_style='Body1'),
                MDTextButton(
                    text=self.current_language.upper(),
                    on_press=lambda x: self.show_language_dialog()
                )
            ]
        ))
        
        dialog.add_widget(content)
        dialog.add_widget(MDFlatButton(
            text="CLOSE",
            on_press=dialog.dismiss
        ))
        
        dialog.open()
    
    def _toggle_wake_detection(self):
        """Toggle wake word detection"""
        if not self.voice_assistant:
            return
        
        current = self.voice_assistant.wake_word_detection
        self.voice_assistant.set_wake_word_detection(not current)
        Snackbar(text=f"Wake word detection: {'ON' if not current else 'OFF'}").open()
    
    def _toggle_continuous_listening(self):
        """Toggle continuous listening"""
        if not self.voice_assistant:
            return
        
        current = self.voice_assistant.continuous_listening
        self.voice_assistant.set_continuous_listening(not current)
        Snackbar(text=f"Continuous listening: {'ON' if not current else 'OFF'}").open()
    
    def on_back_button(self):
        """Handle back button press"""
        # Stop listening if active
        if self.voice_assistant and self.voice_assistant.is_active():
            self.voice_assistant.stop()
        
        self.manager.current = 'home'
    

# Load KV language for voice screen
Builder.load_string('''
<VoiceScreen>:
    name: 'voice'
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        
        MDTopAppBar:
            title: "Voice Assistant"
            subtitle: "Speak to TurboMind"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: root.on_back_button()]]
            right_action_items: [["cog", lambda x: root.show_settings()]]
        
        # Status Card
        MDCard:
            orientation: 'vertical'
            padding: dp(15)
            spacing: dp(10)
            radius: dp(16)
            elevation: 1
            md_bg_color: 0.1, 0.1, 0.1, 0.6
            size_hint_y: None
            height: dp(100)
            
            MDBoxLayout:
                orientation: 'horizontal'
                spacing: dp(10)
                
                MDIcon:
                    icon: "mic"
                    size: "24sp"
                    theme_text_color: "Primary"
                
                MDLabel:
                    id: status_label
                    text: "🤖 Ready"
                    font_style: 'Body1'
                    halign: 'left'
            
            MDLabel:
                text: "Click the microphone to start listening"
                font_style: 'Caption'
                theme_text_color: "Secondary"
                halign: 'left'
            
            MDProgressBar:
                id: progress_bar
                value: 0
                size_hint_y: None
                height: dp(4)
        
        # Main Listen Button
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(10)
            spacing: dp(10)
            size_hint_y: None
            height: dp(120)
            
            MDRaisedButton:
                id: listen_button
                text: "Start Listening"
                icon: "mic"
                on_press: root.toggle_listening()
                size_hint: 1, None
                height: dp(80)
                elevation: 4
                font_size: "18sp"
                md_bg_color: 0.21, 0.58, 0.94, 1
        
        # Input Field
        MDBoxLayout:
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(10)
            size_hint_y: None
            height: dp(60)
            
            MDTextField:
                id: input_field
                hint_text: "Type a command..."
                mode: "rectangle"
                size_hint_x: 0.85
                on_text_validate: root.send_text_command()
            
            MDRaisedButton:
                text: "Send"
                icon: "send"
                on_press: root.send_text_command()
                size_hint_x: 0.15
                elevation: 2
        
        # Conversation Display
        MDLabel:
            text: "Conversation"
            font_style: 'H6'
            halign: 'left'
            padding: dp(10), dp(0)
            size_hint_y: None
            height: dp(40)
        
        ScrollView:
            bar_width: dp(5)
            bar_color: 33/255, 150/255, 243/255, 0.5
            bar_inactive_color: 33/255, 150/255, 243/255, 0.2
            scroll_type: ['bars', 'content']
            
            MDBoxLayout:
                id: conversation_list
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(10)
                size_hint_y: None
                height: max(self.minimum_height, root.height - dp(500))
                adaptive_height: True
        
        # Action Buttons
        MDBoxLayout:
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(10)
            size_hint_y: None
            height: dp(60)
            
            MDRaisedButton:
                text: "Clear"
                icon: "delete"
                on_press: root.clear_conversation()
                size_hint_x: 0.48
                elevation: 2
                
            MDRaisedButton:
                text: "Language"
                icon: "translate"
                on_press: root.show_language_dialog()
                size_hint_x: 0.48
                elevation: 2
''')
