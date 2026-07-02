#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Chat Screen
==========================
Handles the AI chat interface
"""

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.list import OneLineListItem, MDList
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
from kivy.core.window import Window
from typing import Optional, Dict, Any
import time


class ChatMessage(MDBoxLayout):
    """Represents a single message in the chat"""
    pass


class ChatInput(MDBoxLayout):
    """Chat input area with text field and buttons"""
    text_input = ObjectProperty(None)
    
    def send_message(self) -> None:
        """Send the message"""
        text = self.text_input.text.strip()
        if text:
            self.parent.add_user_message(text)
            self.text_input.text = ''
            Window.softinput_mode = ''
    
    def on_enter(self, instance, value) -> None:
        """Handle enter key press"""
        if value and value.strip():
            self.send_message()


class ChatScreen(MDScreen):
    """AI Chat screen with conversation interface"""
    
    chat_history = ObjectProperty(None)  # MDList for messages
    chat_input = ObjectProperty(None)  # ChatInput widget
    scroll_view = ObjectProperty(None)  # MDScrollView
    
    # Generation state
    is_generating = BooleanProperty(False)
    current_generation = StringProperty('')
    
    # Context manager and generation engine references
    context_manager = None
    generation_engine = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages = []  # List of message data
        self.conversation_id = None
    
    def on_pre_enter(self, *args) -> None:
        """Called before entering the screen"""
        # Initialize conversation if not exists
        if self.conversation_id is None:
            self.start_new_conversation()
        
        # Scroll to bottom
        Clock.schedule_once(self.scroll_to_bottom, 0.1)
    
    def start_new_conversation(self) -> None:
        """Start a new conversation"""
        from runtime.context_manager import ContextManager
        from runtime.generation_engine import GenerationEngine
        
        # Initialize context manager if not exists
        if self.context_manager is None:
            self.context_manager = ContextManager()
        
        # Create new conversation
        conv = self.context_manager.create_conversation(title=f"Chat {len(self.context_manager.conversations)}")
        self.conversation_id = conv.id
        
        # Initialize generation engine if not exists
        if self.generation_engine is None:
            self.generation_engine = GenerationEngine()
        
        # Add system message
        self.add_system_message("I am TurboMind AI, your offline AI assistant. How can I help you today?")
    
    def add_user_message(self, text: str) -> None:
        """Add a user message to the chat"""
        if not text.strip():
            return
        
        # Add to context manager
        if self.context_manager and self.conversation_id:
            self.context_manager.current_conversation_id = self.conversation_id
            self.context_manager.add_message('user', text)
        
        # Add to UI
        self._add_message_to_ui('user', text)
        
        # Start AI response
        self.start_ai_response(text)
    
    def add_system_message(self, text: str) -> None:
        """Add a system message to the chat"""
        self._add_message_to_ui('system', text)
    
    def add_assistant_message(self, text: str, streaming: bool = False) -> None:
        """Add an assistant message to the chat"""
        # Add to context manager
        if self.context_manager and self.conversation_id:
            self.context_manager.add_message('assistant', text)
        
        # Add to UI
        self._add_message_to_ui('assistant', text)
    
    def _add_message_to_ui(self, role: str, text: str) -> None:
        """Add a message to the UI"""
        message_data = {
            'role': role,
            'text': text,
            'timestamp': time.time()
        }
        self.messages.append(message_data)
        
        # Create message widget
        message_widget = ChatMessage()
        message_widget.ids['message_text'].text = text
        message_widget.ids['message_text'].halign = 'left' if role == 'assistant' else 'right'
        message_widget.ids['message_text'].theme_text_color = 'Secondary' if role == 'assistant' else 'Primary'
        message_widget.ids['message_bubble'].md_bg_color = (0.9, 0.9, 0.9, 1) if role == 'assistant' else (0.2, 0.6, 1, 1)
        
        # Add to chat history
        self.chat_history.add_widget(message_widget)
        
        # Scroll to bottom
        Clock.schedule_once(self.scroll_to_bottom, 0.1)
    
    def start_ai_response(self, prompt: str) -> None:
        """Start generating AI response"""
        if self.is_generating:
            return
        
        self.is_generating = True
        self.current_generation = ''
        
        # Get context
        context = []
        if self.context_manager and self.conversation_id:
            self.context_manager.current_conversation_id = self.conversation_id
            context = self.context_manager.get_context()
        
        # Show typing indicator
        typing_item = OneLineListItem(
            text="TurboMind is typing...",
            theme_text_color="Secondary"
        )
        self.chat_history.add_widget(typing_item)
        Clock.schedule_once(self.scroll_to_bottom, 0.1)
        
        # Generate response in background
        Clock.schedule_once(lambda dt: self._generate_response_background(prompt, context, typing_item), 0.1)
    
    def _generate_response_background(self, prompt: str, context: list, typing_item: OneLineListItem) -> None:
        """Generate response in background thread"""
        try:
            # For demo, use generation engine
            if self.generation_engine:
                result = self.generation_engine.generate(prompt)
                response_text = result.text
            else:
                # Fallback mock response
                response_text = f"I received your message: {prompt[:50]}..."
            
            # Remove typing indicator
            self.chat_history.remove_widget(typing_item)
            
            # Add assistant message
            self.add_assistant_message(response_text)
            
        except Exception as e:
            Snackbar(text=f"Error: {str(e)}").open()
        finally:
            self.is_generating = False
    
    def stream_ai_response(self, prompt: str) -> None:
        """Stream AI response (word by word)"""
        if self.is_generating:
            return
        
        self.is_generating = True
        self.current_generation = ''
        
        # Show typing indicator
        typing_item = OneLineListItem(
            text="TurboMind is typing...",
            theme_text_color="Secondary"
        )
        self.chat_history.add_widget(typing_item)
        Clock.schedule_once(self.scroll_to_bottom, 0.1)
        
        # Stream response
        if self.generation_engine:
            for result in self.generation_engine.stream_generate(prompt):
                if result.finish_reason != 'streaming':
                    # Remove typing indicator
                    self.chat_history.remove_widget(typing_item)
                    # Add complete message
                    self.add_assistant_message(result.text)
                    break
                
                # Update typing indicator
                typing_item.text = result.text
        else:
            # Fallback
            self.chat_history.remove_widget(typing_item)
            self.add_assistant_message(f"I received: {prompt[:50]}...")
        
        self.is_generating = False
    
    def stop_generation(self) -> None:
        """Stop current generation"""
        self.is_generating = False
        Snackbar(text="Generation stopped").open()
    
    def clear_chat(self) -> None:
        """Clear the current chat"""
        self.chat_history.clear_widgets()
        self.messages.clear()
        
        # Clear context
        if self.context_manager and self.conversation_id:
            self.context_manager.clear_current()
        
        Snackbar(text="Chat cleared").open()
    
    def new_chat(self) -> None:
        """Start a new chat"""
        self.clear_chat()
        self.start_new_conversation()
    
    def scroll_to_bottom(self, *args) -> None:
        """Scroll chat to bottom"""
        if self.scroll_view:
            self.scroll_view.scroll_y = 0
    
    def copy_last_response(self) -> None:
        """Copy last assistant response to clipboard"""
        if self.messages:
            for msg in reversed(self.messages):
                if msg['role'] == 'assistant':
                    Window.copy_to_clipboard(msg['text'])
                    Snackbar(text="Response copied to clipboard").open()
                    return
        Snackbar(text="No response to copy").open()
    
    def show_conversation_list(self) -> None:
        """Show list of conversations"""
        if not self.context_manager:
            return
        
        conversations = self.context_manager.get_conversation_list()
        
        if not conversations:
            Snackbar(text="No other conversations").open()
            return
        
        # Create dialog with conversation list
        dialog = MDDialog(
            title="Conversations",
            size_hint=(0.8, 0.8)
        )
        
        content = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        list_view = MDList()
        
        for conv in conversations:
            item = OneLineListItem(
                text=conv['title'],
                secondary_text=f"{conv['message_count']} messages"
            )
            item.bind(on_press=lambda instance, c=conv: self._switch_conversation(c['id'], dialog))
            list_view.add_widget(item)
        
        content.add_widget(list_view)
        dialog.add_widget(content)
        dialog.open()
    
    def _switch_conversation(self, conv_id: str, dialog) -> None:
        """Switch to a different conversation"""
        dialog.dismiss()
        
        if self.context_manager:
            if self.context_manager.switch_conversation(conv_id):
                self.conversation_id = conv_id
                self.clear_chat()
                
                # Load conversation messages
                conv = self.context_manager.get_conversation(conv_id)
                if conv:
                    for msg in conv.messages:
                        self._add_message_to_ui(msg.role, msg.content)
                
                Snackbar(text=f"Switched to conversation {conv_id}").open()
            else:
                Snackbar(text="Failed to switch conversation").open()
    
    def export_chat(self) -> None:
        """Export current chat"""
        if not self.context_manager or not self.conversation_id:
            Snackbar(text="No conversation to export").open()
            return
        
        conv = self.context_manager.get_conversation(self.conversation_id)
        if conv:
            exported = self.context_manager.export_conversation(self.conversation_id)
            # In a real app, save to file or share
            Snackbar(text=f"Exported {len(exported.get('messages', []))} messages").open()
    
    def on_back_button(self) -> None:
        """Handle back button press"""
        self.manager.current = 'home'


# Load KV language for chat screen
Builder.load_string('''
<ChatMessage>:
    orientation: 'vertical'
    padding: dp(10)
    spacing: dp(5)
    size_hint_y: None
    height: self.minimum_height
    
    MDBoxLayout:
        id: message_bubble
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(5)
        radius: dp(15)
        md_bg_color: 0.9, 0.9, 0.9, 1
        size_hint_y: None
        height: self.minimum_height
        
        MDLabel:
            id: message_text
            text: ''
            halign: 'left'
            valign: 'top'
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.width - dp(20), None


<ChatInput>:
    orientation: 'horizontal'
    padding: dp(10)
    spacing: dp(10)
    size_hint_y: None
    height: dp(60)
    
    MDTextField:
        id: text_input
        hint_text: "Type a message..."
        multiline: False
        mode: "rectangle"
        size_hint_x: 0.85
        on_text_validate: root.on_enter(self, self.text)
        
    MDIconButton:
        icon: "send"
        theme_text_color: "Primary"
        on_press: root.send_message()
        size_hint_x: None
        width: dp(48)


<ChatScreen>:
    name: 'chat'
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        
        MDTopAppBar:
            title: "AI Chat"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: root.on_back_button()]]
            right_action_items: [["content-copy", lambda x: root.copy_last_response()], ["delete", lambda x: root.clear_chat()], ["refresh", lambda x: root.new_chat()]]
            
        ScrollView:
            id: scroll_view
            
            MDList:
                id: chat_history
                spacing: dp(10)
                padding: dp(10)
                
        ChatInput:
            id: chat_input
''')
