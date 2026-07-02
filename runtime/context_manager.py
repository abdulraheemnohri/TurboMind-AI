#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Context Manager
==============================
Manages conversation context and history for AI chat
"""

from typing import Dict, Any, List, Optional
import time
from dataclasses import dataclass, field
from collections import deque


@dataclass
class Message:
    """Represents a message in the conversation"""
    role: str  # 'user' or 'assistant' or 'system'
    content: str
    timestamp: float = field(default_factory=time.time)
    tokens: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """Represents a conversation session"""
    id: str
    title: str = "New Chat"
    messages: List[Message] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    context_size: int = 0
    model: str = "default"
    
    def add_message(self, role: str, content: str, **metadata) -> Message:
        """Add a message to the conversation"""
        msg = Message(
            role=role,
            content=content,
            tokens=len(content.split()),
            metadata=metadata
        )
        self.messages.append(msg)
        self.updated_at = time.time()
        self.context_size = sum(m.tokens for m in self.messages)
        return msg
    
    def get_context(self, max_tokens: int = 2048) -> List[Dict[str, Any]]:
        """Get conversation context for model input"""
        context = []
        current_tokens = 0
        
        # Iterate from newest to oldest
        for msg in reversed(self.messages):
            msg_tokens = msg.tokens
            if current_tokens + msg_tokens > max_tokens:
                break
            context.insert(0, {
                'role': msg.role,
                'content': msg.content
            })
            current_tokens += msg_tokens
        
        return context
    
    def clear(self) -> None:
        """Clear the conversation"""
        self.messages.clear()
        self.context_size = 0
        self.updated_at = time.time()


class ContextManager:
    """
    Manages multiple conversations and their contexts.
    Handles context compression, history, and session management.
    """
    
    def __init__(self, max_context_tokens: int = 4096, max_history: int = 50):
        """
        Initialize the context manager.
        
        Args:
            max_context_tokens: Maximum tokens to keep in context
            max_history: Maximum number of conversations to keep
        """
        self.max_context_tokens = max_context_tokens
        self.max_history = max_history
        self.conversations: Dict[str, Conversation] = {}
        self.current_conversation_id: Optional[str] = None
        self._conversation_counter = 0
        
        print(f"💬 Context Manager initialized (max context: {max_context_tokens} tokens)")
    
    def create_conversation(self, title: str = "New Chat", model: str = "default") -> Conversation:
        """Create a new conversation"""
        self._conversation_counter += 1
        conv_id = f"conv_{self._conversation_counter}_{int(time.time())}"
        
        conv = Conversation(
            id=conv_id,
            title=title,
            model=model
        )
        self.conversations[conv_id] = conv
        self.current_conversation_id = conv_id
        
        # Clean up old conversations if needed
        if len(self.conversations) > self.max_history:
            self._cleanup_old_conversations()
        
        print(f"🆕 New conversation created: {conv_id}")
        return conv
    
    def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        return self.conversations.get(conv_id)
    
    def get_current_conversation(self) -> Optional[Conversation]:
        """Get the current conversation"""
        if self.current_conversation_id:
            return self.conversations.get(self.current_conversation_id)
        return None
    
    def switch_conversation(self, conv_id: str) -> bool:
        """Switch to a different conversation"""
        if conv_id in self.conversations:
            self.current_conversation_id = conv_id
            return True
        return False
    
    def delete_conversation(self, conv_id: str) -> bool:
        """Delete a conversation"""
        if conv_id in self.conversations:
            del self.conversations[conv_id]
            if self.current_conversation_id == conv_id:
                self.current_conversation_id = None
            return True
        return False
    
    def add_message(self, role: str, content: str, **metadata) -> Optional[Message]:
        """Add a message to the current conversation"""
        conv = self.get_current_conversation()
        if conv:
            msg = conv.add_message(role, content, **metadata)
            return msg
        return None
    
    def get_context(self, max_tokens: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get context for the current conversation"""
        conv = self.get_current_conversation()
        if conv:
            max_t = max_tokens if max_tokens is not None else self.max_context_tokens
            return conv.get_context(max_t)
        return []
    
    def clear_current(self) -> None:
        """Clear the current conversation"""
        conv = self.get_current_conversation()
        if conv:
            conv.clear()
    
    def clear_all(self) -> None:
        """Clear all conversations"""
        self.conversations.clear()
        self.current_conversation_id = None
        self._conversation_counter = 0
    
    def _cleanup_old_conversations(self) -> None:
        """Remove old conversations to stay within max_history"""
        if len(self.conversations) <= self.max_history:
            return
        
        # Sort by updated_at and remove oldest
        sorted_convs = sorted(
            self.conversations.items(),
            key=lambda x: x[1].updated_at
        )
        
        # Remove oldest conversations
        for conv_id, _ in sorted_convs[:len(self.conversations) - self.max_history]:
            if conv_id != self.current_conversation_id:
                del self.conversations[conv_id]
    
    def compress_context(self, conversation_id: str, ratio: float = 0.5) -> bool:
        """
        Compress conversation context to save memory.
        
        Args:
            conversation_id: ID of conversation to compress
            ratio: Compression ratio (0-1)
            
        Returns:
            bool: True if compression successful
        """
        conv = self.get_conversation(conversation_id)
        if not conv:
            return False
        
        # TODO: Implement actual context compression
        # For now, just keep the most recent messages
        keep_count = int(len(conv.messages) * ratio)
        if keep_count < len(conv.messages):
            conv.messages = conv.messages[-keep_count:]
            conv.context_size = sum(m.tokens for m in conv.messages)
            conv.updated_at = time.time()
        
        return True
    
    def get_conversation_list(self) -> List[Dict[str, Any]]:
        """Get list of all conversations"""
        return [
            {
                'id': conv.id,
                'title': conv.title,
                'model': conv.model,
                'message_count': len(conv.messages),
                'context_size': conv.context_size,
                'updated_at': conv.updated_at
            }
            for conv in self.conversations.values()
        ]
    
    def export_conversation(self, conv_id: str) -> Dict[str, Any]:
        """Export a conversation for sharing/saving"""
        conv = self.get_conversation(conv_id)
        if not conv:
            return {}
        
        return {
            'id': conv.id,
            'title': conv.title,
            'model': conv.model,
            'created_at': conv.created_at,
            'updated_at': conv.updated_at,
            'messages': [
                {
                    'role': m.role,
                    'content': m.content,
                    'timestamp': m.timestamp,
                    'metadata': m.metadata
                }
                for m in conv.messages
            ]
        }
    
    def import_conversation(self, data: Dict[str, Any]) -> Optional[Conversation]:
        """Import a conversation from exported data"""
        conv = Conversation(
            id=data.get('id', f"imported_{int(time.time())}"),
            title=data.get('title', 'Imported Chat'),
            model=data.get('model', 'default'),
            created_at=data.get('created_at', time.time()),
            updated_at=data.get('updated_at', time.time())
        )
        
        for msg_data in data.get('messages', []):
            conv.messages.append(Message(
                role=msg_data.get('role', 'user'),
                content=msg_data.get('content', ''),
                timestamp=msg_data.get('timestamp', time.time()),
                tokens=len(msg_data.get('content', '').split()),
                metadata=msg_data.get('metadata', {})
            ))
        
        conv.context_size = sum(m.tokens for m in conv.messages)
        self.conversations[conv.id] = conv
        
        return conv
