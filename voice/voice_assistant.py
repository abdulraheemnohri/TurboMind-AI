#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Voice Assistant
==============================
Handles voice-based AI assistance
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
import time
import threading
import queue


@dataclass
class VoiceCommand:
    """Represents a voice command"""
    command: str
    intent: str = ""
    entities: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'command': self.command,
            'intent': self.intent,
            'entities': self.entities,
            'confidence': self.confidence,
            'timestamp': self.timestamp
        }


@dataclass
class VoiceResponse:
    """Represents a voice assistant response"""
    text: str
    speech: Optional[str] = None
    action: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'text': self.text,
            'speech': self.speech,
            'action': self.action,
            'data': self.data,
            'timestamp': self.timestamp
        }


class VoiceAssistant:
    """
    Voice Assistant for TurboMind AI.
    Handles voice commands, conversations, and integrations.
    """
    
    # Command keywords
    WAKE_WORDS = ['hey turbo', 'ok turbo', 'turbo', 'hello turbo']
    
    # Supported commands
    COMMANDS = {
        'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon'],
        'help': ['help', 'what can you do', 'commands'],
        'search': ['search', 'find', 'look up'],
        'weather': ['weather', 'temperature', 'forecast'],
        'time': ['time', 'what time', 'current time'],
        'date': ['date', 'what day', 'today'],
        'joke': ['tell me a joke', 'joke', 'make me laugh'],
        'news': ['news', 'what is the news', 'latest news'],
        'calculate': ['calculate', 'math', 'what is'],
        'note': ['note', 'remember', 'write down'],
        'reminder': ['remind me', 'set reminder', 'reminder'],
        'open': ['open', 'launch', 'start'],
        'close': ['close', 'exit', 'quit'],
        'stop': ['stop', 'pause', 'cancel']
    }
    
    # Responses
    RESPONSES = {
        'greeting': [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
            "Greetings! I'm at your service.",
            "Salam! Kaise ho?"
        ],
        'help': [
            "I can help you with many things like answering questions, setting reminders, "
            "doing calculations, and much more. Just ask!",
            "Try asking me about the weather, time, or to tell you a joke. "
            "I can also help with calculations and notes."
        ],
        'unknown': [
            "I'm sorry, I didn't understand that. Can you try again?",
            "I'm not sure what you mean. Could you rephrase that?",
            "I didn't catch that. Could you say it differently?"
        ],
        'error': [
            "Sorry, I encountered an error. Please try again.",
            "Something went wrong. Let me try that again."
        ]
    }
    
    def __init__(self, stt_engine=None, tts_engine=None):
        """
        Initialize the voice assistant.
        
        Args:
            stt_engine: SpeechToText engine instance
            tts_engine: TextToSpeech engine instance
        """
        self.stt_engine = stt_engine
        self.tts_engine = tts_engine
        
        # State
        self.is_listening = False
        self.is_speaking = False
        self.is_active = False
        self.current_conversation: List[Dict[str, Any]] = []
        
        # Callbacks
        self.on_command_callback: Optional[Callable] = None
        self.on_response_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
        
        # Threading
        self.audio_queue = queue.Queue()
        self.listening_thread: Optional[threading.Thread] = None
        
        # Settings
        self.wake_word_detection = True
        self.continuous_listening = True
        self.language = 'en'
        
        print("🤖 Voice Assistant initialized")
    
    def start(self) -> bool:
        """Start the voice assistant"""
        try:
            if self.is_active:
                print("⚠️  Voice assistant is already running")
                return False
            
            # Ensure engines are loaded
            if self.stt_engine and not self.stt_engine.is_model_loaded():
                self.stt_engine.load_model()
            
            if self.tts_engine and not self.tts_engine.is_model_loaded():
                self.tts_engine.load_model()
            
            self.is_active = True
            self.is_listening = True
            
            # Start listening in background
            self._start_listening()
            
            print("✅ Voice assistant started")
            return True
            
        except Exception as e:
            print(f"❌ Error starting voice assistant: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the voice assistant"""
        try:
            self.is_active = False
            self.is_listening = False
            self._stop_listening()
            
            print("🛑 Voice assistant stopped")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping voice assistant: {e}")
            return False
    
    def _start_listening(self):
        """Start listening for commands"""
        if self.listening_thread and self.listening_thread.is_alive():
            return
        
        self.listening_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listening_thread.start()
    
    def _stop_listening(self):
        """Stop listening for commands"""
        if self.listening_thread:
            self.is_listening = False
            # In a real implementation, would properly stop the thread
            self.listening_thread = None
    
    def _listen_loop(self):
        """Main listening loop"""
        while self.is_listening:
            try:
                # In a real implementation, would continuously listen
                # For demo, simulate listening
                import time
                time.sleep(1)
                
                # Simulate detecting speech
                if self.wake_word_detection:
                    # Check for wake word
                    detected_text = "hey turbo"  # Simulated
                    if any(wake_word in detected_text.lower() for wake_word in self.WAKE_WORDS):
                        self._handle_wake_word()
                else:
                    # Direct command mode
                    detected_text = "what time is it"  # Simulated
                    self._process_command(detected_text)
                    
            except Exception as e:
                print(f"❌ Listening error: {e}")
                if self.on_error_callback:
                    self.on_error_callback(str(e))
    
    def _handle_wake_word(self):
        """Handle wake word detection"""
        print("🎤 Wake word detected!")
        
        # Respond to wake word
        self._speak("Yes, how can I help you?")
        
        # In continuous mode, wait for command
        if self.continuous_listening:
            # Simulate listening for command
            import time
            time.sleep(2)
            
            # Simulate receiving command
            command_text = "what is the weather today"  # Simulated
            self._process_command(command_text)
    
    def _process_command(self, text: str):
        """Process a voice command"""
        try:
            # Create command object
            command = self._extract_command(text)
            
            # Store in conversation
            self.current_conversation.append({
                'type': 'command',
                'text': text,
                'timestamp': time.time()
            })
            
            # Call callback if set
            if self.on_command_callback:
                self.on_command_callback(command)
            
            # Process command and get response
            response = self._get_response(command)
            
            # Speak response
            if response and response.speech:
                self._speak(response.speech)
            
            # Store response in conversation
            self.current_conversation.append({
                'type': 'response',
                'text': response.text,
                'timestamp': time.time()
            })
            
            # Call response callback if set
            if self.on_response_callback:
                self.on_response_callback(response)
                
        except Exception as e:
            print(f"❌ Error processing command: {e}")
            if self.on_error_callback:
                self.on_error_callback(str(e))
    
    def _extract_command(self, text: str) -> VoiceCommand:
        """Extract command information from text"""
        text_lower = text.lower()
        
        # Determine intent
        intent = "unknown"
        entities = {}
        
        for cmd_type, keywords in self.COMMANDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    intent = cmd_type
                    break
            if intent != "unknown":
                break
        
        # Extract entities based on intent
        if intent == "calculate":
            # Extract numbers from text
            import re
            numbers = re.findall(r'\d+', text)
            if numbers:
                entities['numbers'] = [int(n) for n in numbers]
        elif intent == "search":
            # Extract search query
            for keyword in self.COMMANDS['search']:
                if keyword in text_lower:
                    query = text.replace(keyword, "").strip()
                    if query:
                        entities['query'] = query
        elif intent == "reminder":
            # Extract time and message
            import re
            time_matches = re.findall(r'(\d+\s*(minute|hour|day)s?)', text_lower)
            if time_matches:
                entities['time'] = time_matches[0][0]
            
            # Extract message after reminder keywords
            for keyword in self.COMMANDS['reminder']:
                if keyword in text_lower:
                    message = text.replace(keyword, "").strip()
                    if message:
                        entities['message'] = message
        
        return VoiceCommand(
            command=text,
            intent=intent,
            entities=entities,
            confidence=0.95  # Simulated confidence
        )
    
    def _get_response(self, command: VoiceCommand) -> VoiceResponse:
        """Get response for a command"""
        intent = command.intent
        entities = command.entities
        
        # Generate response based on intent
        if intent == "greeting":
            response_text = self._get_random_response('greeting')
            return VoiceResponse(text=response_text, speech=response_text)
        
        elif intent == "help":
            response_text = self._get_random_response('help')
            return VoiceResponse(text=response_text, speech=response_text)
        
        elif intent == "time":
            current_time = time.strftime("%I:%M %p")
            response_text = f"The current time is {current_time}"
            return VoiceResponse(text=response_text, speech=response_text)
        
        elif intent == "date":
            current_date = time.strftime("%A, %B %d, %Y")
            response_text = f"Today is {current_date}"
            return VoiceResponse(text=response_text, speech=response_text)
        
        elif intent == "joke":
            jokes = [
                "Why don't scientists trust atoms? Because they make up everything!",
                "Why did the scarecrow win an award? Because he was outstanding in his field!",
                "What do you call a fake noodle? An impasta!",
                "How do you organize a space party? You planet!"
            ]
            import random
            response_text = random.choice(jokes)
            return VoiceResponse(text=response_text, speech=response_text)
        
        elif intent == "calculate":
            numbers = entities.get('numbers', [])
            if len(numbers) >= 2:
                result = numbers[0] + numbers[1]  # Simple addition for demo
                response_text = f"The result is {result}"
            else:
                response_text = "I couldn't find numbers to calculate."
            return VoiceResponse(text=response_text, speech=response_text)
        
        elif intent == "search":
            query = entities.get('query', '')
            if query:
                response_text = f"Searching for {query}"
                return VoiceResponse(
                    text=response_text,
                    speech=response_text,
                    action="search",
                    data={'query': query}
                )
            else:
                response_text = "What would you like me to search for?"
                return VoiceResponse(text=response_text, speech=response_text)
        
        elif intent == "reminder":
            message = entities.get('message', '')
            time_str = entities.get('time', 'soon')
            response_text = f"I'll remind you to {message} in {time_str}"
            return VoiceResponse(
                text=response_text,
                speech=response_text,
                action="reminder",
                data={'message': message, 'time': time_str}
            )
        
        elif intent == "open":
            # Extract app/feature name
            text_lower = command.command.lower()
            for keyword in self.COMMANDS['open']:
                if keyword in text_lower:
                    target = command.command.replace(keyword, "").strip()
                    response_text = f"Opening {target}"
                    return VoiceResponse(
                        text=response_text,
                        speech=response_text,
                        action="open",
                        data={'target': target}
                    )
        
        elif intent == "close":
            # Extract app/feature name
            text_lower = command.command.lower()
            for keyword in self.COMMANDS['close']:
                if keyword in text_lower:
                    target = command.command.replace(keyword, "").strip()
                    response_text = f"Closing {target}"
                    return VoiceResponse(
                        text=response_text,
                        speech=response_text,
                        action="close",
                        data={'target': target}
                    )
        
        elif intent == "stop":
            response_text = "Okay, stopping."
            return VoiceResponse(
                text=response_text,
                speech=response_text,
                action="stop"
            )
        
        else:
            response_text = self._get_random_response('unknown')
            return VoiceResponse(text=response_text, speech=response_text)
    
    def _get_random_response(self, category: str) -> str:
        """Get a random response from a category"""
        responses = self.RESPONSES.get(category, self.RESPONSES['unknown'])
        import random
        return random.choice(responses)
    
    def _speak(self, text: str):
        """Speak text using TTS"""
        if self.tts_engine and self.is_active:
            self.is_speaking = True
            self.tts_engine.speak(text, play=True)
            self.is_speaking = False
    
    def listen(self, callback: Optional[Callable] = None):
        """
        Start listening for a single command.
        
        Args:
            callback: Function to call with the recognized text
        """
        if not self.is_active:
            print("❌ Voice assistant is not active")
            return
        
        self.on_command_callback = callback
        
        # Simulate listening
        import time
        time.sleep(2)
        
        # Simulate recognized text
        if callback:
            callback("what time is it")
    
    def respond(self, text: str):
        """
        Respond to a command with text.
        
        Args:
            text: Text to respond with
        """
        if self.is_active:
            self._speak(text)
    
    def set_language(self, language_code: str) -> bool:
        """
        Set the language for voice assistant.
        
        Args:
            language_code: Language code
            
        Returns:
            True if language is supported
        """
        if self.stt_engine:
            if not self.stt_engine.set_language(language_code):
                return False
        
        if self.tts_engine:
            if not self.tts_engine.set_language(language_code):
                return False
        
        self.language = language_code
        print(f"🌍 Voice assistant language set to: {language_code}")
        return True
    
    def get_conversation(self) -> List[Dict[str, Any]]:
        """Get current conversation history"""
        return self.current_conversation.copy()
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.current_conversation.clear()
        print("🧹 Conversation cleared")
    
    def set_continuous_listening(self, enabled: bool):
        """Enable or disable continuous listening"""
        self.continuous_listening = enabled
        print(f"🔄 Continuous listening: {'ON' if enabled else 'OFF'}")
    
    def set_wake_word_detection(self, enabled: bool):
        """Enable or disable wake word detection"""
        self.wake_word_detection = enabled
        print(f"🎤 Wake word detection: {'ON' if enabled else 'OFF'}")
    
    def is_active(self) -> bool:
        """Check if voice assistant is active"""
        return self.is_active
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of voice assistant"""
        return {
            'is_active': self.is_active,
            'is_listening': self.is_listening,
            'is_speaking': self.is_speaking,
            'language': self.language,
            'wake_word_detection': self.wake_word_detection,
            'continuous_listening': self.continuous_listening,
            'conversation_length': len(self.current_conversation)
        }
    
    def on_command(self, callback: Callable):
        """Set callback for when a command is received"""
        self.on_command_callback = callback
    
    def on_response(self, callback: Callable):
        """Set callback for when a response is generated"""
        self.on_response_callback = callback
    
    def on_error(self, callback: Callable):
        """Set callback for when an error occurs"""
        self.on_error_callback = callback