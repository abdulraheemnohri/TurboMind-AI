#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Tokenizer
========================
Handles tokenization of text for AI models
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json


class Tokenizer:
    """
    Tokenizer for converting text to tokens and vice versa.
    Supports multiple tokenization strategies.
    """
    
    def __init__(self, vocab_path: Optional[str] = None):
        """
        Initialize the tokenizer.
        
        Args:
            vocab_path: Path to vocabulary file (optional)
        """
        self.vocab: Dict[str, int] = {}
        self.inverse_vocab: Dict[int, str] = {}
        self.vocab_size = 0
        self.special_tokens = {
            '<pad>': 0,
            '<unk>': 1,
            '<s>': 2,  # Start of sequence
            '</s>': 3,  # End of sequence
            '<cls>': 4,  # Classification token
            '<sep>': 5,  # Separator token
            '<mask>': 6  # Mask token
        }
        
        # Reverse special tokens
        self.inverse_special = {v: k for k, v in self.special_tokens.items()}
        
        # Load vocabulary if provided
        if vocab_path and Path(vocab_path).exists():
            self.load_vocab(vocab_path)
        else:
            # Initialize with special tokens
            self.vocab = self.special_tokens.copy()
            self.inverse_vocab = self.inverse_special.copy()
            self.vocab_size = len(self.special_tokens)
        
        print(f"🔤 Tokenizer initialized (vocab size: {self.vocab_size})")
    
    def load_vocab(self, vocab_path: str) -> bool:
        """Load vocabulary from file"""
        try:
            with open(vocab_path, 'r', encoding='utf-8') as f:
                vocab_data = json.load(f)
            
            # Load vocabulary
            if 'vocab' in vocab_data:
                for token, idx in vocab_data['vocab'].items():
                    self.vocab[token] = idx
                    self.inverse_vocab[idx] = token
            
            # Load special tokens
            if 'special_tokens' in vocab_data:
                for token, idx in vocab_data['special_tokens'].items():
                    self.special_tokens[token] = idx
                    self.inverse_special[idx] = token
            
            self.vocab_size = len(self.vocab)
            print(f"📂 Vocabulary loaded from {vocab_path} ({self.vocab_size} tokens)")
            return True
            
        except Exception as e:
            print(f"❌ Error loading vocabulary: {e}")
            return False
    
    def save_vocab(self, vocab_path: str) -> bool:
        """Save vocabulary to file"""
        try:
            vocab_data = {
                'vocab': {k: v for k, v in self.vocab.items() if k not in self.special_tokens},
                'special_tokens': self.special_tokens
            }
            
            with open(vocab_path, 'w', encoding='utf-8') as f:
                json.dump(vocab_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Vocabulary saved to {vocab_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving vocabulary: {e}")
            return False
    
    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """
        Encode text into token IDs.
        
        Args:
            text: Input text to encode
            add_special_tokens: Whether to add start/end tokens
            
        Returns:
            List of token IDs
        """
        if not text or not text.strip():
            return [self.special_tokens['<unk>']] if add_special_tokens else []
        
        # Simple whitespace tokenization (for demo)
        # In production, use proper tokenizer like HuggingFace Tokenizer
        tokens = self._simple_tokenize(text)
        
        # Convert tokens to IDs
        token_ids = []
        for token in tokens:
            if token in self.vocab:
                token_ids.append(self.vocab[token])
            else:
                # Unknown token
                token_ids.append(self.special_tokens['<unk>'])
        
        # Add special tokens
        if add_special_tokens:
            token_ids = [self.special_tokens['<s>']] + token_ids + [self.special_tokens['</s>']]
        
        return token_ids
    
    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """
        Decode token IDs back to text.
        
        Args:
            token_ids: List of token IDs
            skip_special_tokens: Whether to skip special tokens in output
            
        Returns:
            Decoded text
        """
        tokens = []
        for token_id in token_ids:
            if token_id in self.inverse_vocab:
                token = self.inverse_vocab[token_id]
                if not skip_special_tokens or token not in self.special_tokens:
                    tokens.append(token)
            else:
                tokens.append('<unk>')
        
        # Simple detokenization (for demo)
        return self._simple_detokenize(tokens)
    
    def _simple_tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization using whitespace and basic punctuation.
        For production, replace with proper tokenizer.
        """
        # Split on whitespace
        tokens = text.split()
        
        # Further split on punctuation
        final_tokens = []
        for token in tokens:
            # Split on common punctuation
            parts = re.split(r'([\.,\!\?\;\:\'\"\{\}\(\)\[\]\@\#\$\%\^\&\*\+\=\|\\/])', token)
            for part in parts:
                if part and part.strip():
                    final_tokens.append(part)
        
        return final_tokens
    
    def _simple_detokenize(self, tokens: List[str]) -> str:
        """
        Simple detokenization by joining with spaces.
        For production, use proper detokenizer.
        """
        # Handle special cases
        text = ' '.join(tokens)
        
        # Fix common issues
        text = text.replace(' ?', '?')
        text = text.replace(' !', '!')
        text = text.replace(' .', '.')
        text = text.replace(' ,', ',')
        text = text.replace(' ;', ';')
        text = text.replace(' :', ':')
        text = text.replace(' "', '"')
        text = text.replace(" '", "'")
        text = text.replace(' (', '(')
        text = text.replace(' )', ')')
        text = text.replace(' [', '[')
        text = text.replace(' ]', ']')
        text = text.replace(' {', '{')
        text = text.replace(' }', '}')
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        return text
    
    def tokenize(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Full tokenization with metadata.
        
        Args:
            text: Text to tokenize
            **kwargs: Additional options
            
        Returns:
            dict: Tokenization result with tokens and metadata
        """
        token_ids = self.encode(text, add_special_tokens=kwargs.get('add_special_tokens', True))
        tokens = []
        
        for token_id in token_ids:
            token = self.inverse_vocab.get(token_id, '<unk>')
            tokens.append(token)
        
        return {
            'input': text,
            'tokens': tokens,
            'token_ids': token_ids,
            'num_tokens': len(token_ids),
            'vocab_size': self.vocab_size
        }
    
    def num_tokens_from_string(self, text: str) -> int:
        """Get number of tokens in a string"""
        return len(self.encode(text, add_special_tokens=False))
    
    def num_tokens_from_tokens(self, token_ids: List[int]) -> int:
        """Get number of tokens from token IDs"""
        return len(token_ids)
    
    def add_token(self, token: str) -> int:
        """Add a new token to vocabulary"""
        if token not in self.vocab:
            new_id = self.vocab_size
            self.vocab[token] = new_id
            self.inverse_vocab[new_id] = token
            self.vocab_size += 1
            return new_id
        return self.vocab[token]
    
    def add_tokens(self, tokens: List[str]) -> Dict[str, int]:
        """Add multiple tokens to vocabulary"""
        added = {}
        for token in tokens:
            if token not in self.vocab:
                added[token] = self.add_token(token)
        return added
    
    def get_vocab_size(self) -> int:
        """Get vocabulary size"""
        return self.vocab_size
    
    def get_special_tokens(self) -> Dict[str, int]:
        """Get special tokens"""
        return self.special_tokens.copy()
