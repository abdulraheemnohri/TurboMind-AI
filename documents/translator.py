#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Translator
=========================
Offline translation for 40+ languages
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import json
import os
from pathlib import Path


@dataclass
class Translation:
    """Represents a translation result"""
    text: str
    source_language: str
    target_language: str
    detected_language: Optional[str] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = None


class Translator:
    """
    Offline translator supporting multiple languages.
    For demo, uses a simple dictionary-based approach.
    In production, would integrate with offline translation models.
    """
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'ur': 'Urdu',
        'ar': 'Arabic',
        'fr': 'French',
        'es': 'Spanish',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'hi': 'Hindi',
        'bn': 'Bengali',
        'pa': 'Punjabi',
        'tr': 'Turkish',
        'fa': 'Persian',
        'nl': 'Dutch',
        'sv': 'Swedish',
        'fi': 'Finnish',
        'da': 'Danish',
        'no': 'Norwegian',
        'pl': 'Polish',
        'id': 'Indonesian',
        'ms': 'Malay',
        'th': 'Thai',
        'vi': 'Vietnamese',
        'ko': 'Korean',
        'he': 'Hebrew',
        'el': 'Greek',
        'hu': 'Hungarian',
        'cs': 'Czech',
        'ro': 'Romanian',
        'uk': 'Ukrainian',
        'sw': 'Swahili',
        'af': 'Afrikaans',
        'zu': 'Zulu',
        'xh': 'Xhosa',
    }
    
    # Language detection keywords
    LANGUAGE_DETECTION = {
        'en': ['the', 'and', 'of', 'to', 'in', 'is', 'it', 'that', 'for'],
        'ur': ['اور', 'کیا', 'ہے', 'میں', 'کو', 'پس', 'تک', 'یہ', 'ہوں'],
        'ar': ['و', 'في', 'من', 'على', 'أن', 'لا', ' إلى', ' هو', 'ما'],
        'fr': ['le', 'la', 'de', 'et', 'à', 'les', 'des', 'en', 'un'],
        'es': ['el', 'la', 'de', 'y', 'en', 'que', 'los', 'las', 'del'],
        'de': ['der', 'die', 'das', 'und', 'in', 'den', 'von', 'zu', 'ist'],
        'it': ['il', 'di', 'e', 'in', 'la', 'che', 'non', 'un', 'una'],
        'pt': ['o', 'de', 'e', 'em', 'a', 'que', 'do', 'da', 'um'],
        'ru': ['и', 'в', 'не', 'на', 'я', 'что', 'то', 'он', 'с'],
        'zh': ['的', '了', '和', '是', '在', '我', '有', '不', '人'],
        'ja': ['の', 'は', 'が', 'を', 'に', 'も', 'と', 'で', 'だ'],
        'hi': ['और', 'है', 'में', 'का', 'की', 'हो', 'हों', 'होगा', 'था'],
    }
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the translator.
        
        Args:
            model_path: Path to translation model (optional)
        """
        self.model_path = model_path
        self.models: Dict[str, Any] = {}
        self._load_models()
        
        print(f"🌍 Translator initialized ({len(self.SUPPORTED_LANGUAGES)} languages)")
    
    def _load_models(self) -> None:
        """Load translation models"""
        # In production, load actual models
        # For demo, just initialize empty
        pass
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages (code -> name)"""
        return self.SUPPORTED_LANGUAGES.copy()
    
    def get_language_codes(self) -> List[str]:
        """Get list of language codes"""
        return list(self.SUPPORTED_LANGUAGES.keys())
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of a text.
        
        Args:
            text: Text to detect language for
            
        Returns:
            tuple: (language_code, confidence)
        """
        if not text or not text.strip():
            return 'en', 0.0
        
        # Convert to lowercase for detection
        text_lower = text.lower()
        
        # Count matches for each language
        scores = {}
        for lang, keywords in self.LANGUAGE_DETECTION.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            scores[lang] = count
        
        # Get best match
        if scores:
            best_lang = max(scores.keys(), key=lambda k: scores[k])
            total = sum(scores.values())
            confidence = scores[best_lang] / total if total > 0 else 0.0
            return best_lang, confidence
        
        return 'en', 0.0
    
    def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        **kwargs
    ) -> Translation:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (optional, auto-detected)
            **kwargs: Additional options
            
        Returns:
            Translation object with result
        """
        if not text or not text.strip():
            return Translation(
                text="",
                source_language=source_language or 'en',
                target_language=target_language,
                detected_language=source_language,
                confidence=0.0
            )
        
        # Auto-detect source language if not provided
        if source_language is None:
            source_language, confidence = self.detect_language(text)
        else:
            confidence = 1.0
        
        # Perform translation
        translated_text = self._translate_text(text, source_language, target_language)
        
        return Translation(
            text=translated_text,
            source_language=source_language,
            target_language=target_language,
            detected_language=source_language,
            confidence=confidence
        )
    
    def _translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Internal method to translate text.
        For demo, uses simple replacements.
        In production, would use actual translation models.
        """
        # If source and target are the same, return original
        if source_lang == target_lang:
            return text
        
        # For demo: simple word replacements
        # In a real app, this would use a translation model
        
        # Example: English to Urdu (very basic)
        if source_lang == 'en' and target_lang == 'ur':
            replacements = {
                'Hello': 'ہیلو',
                'hello': 'ہیلو',
                'How are you': 'آپ کیسے ہیں',
                'I am': 'میں ہوں',
                'good': 'اچھا',
                'thank you': 'شکریہ',
                'thanks': 'شکریہ',
                'yes': 'ہاں',
                'no': 'ناہیں',
                'please': 'براہ کرم',
                'what': 'کیا',
                'is': 'ہے',
                'your': 'آپ کا',
                'name': 'نام',
            }
            
            result = text
            for old, new in replacements.items():
                result = result.replace(old, new)
            
            return result
        
        # Example: Urdu to English
        if source_lang == 'ur' and target_lang == 'en':
            replacements = {
                'ہیلو': 'Hello',
                'آپ کیسے ہیں': 'How are you',
                'میں ہوں': 'I am',
                'اچھا': 'good',
                'شکریہ': 'Thank you',
                'ہاں': 'Yes',
                'ناہیں': 'No',
                'براہ کرم': 'Please',
                'کیا': 'What',
                'ہے': 'is',
                'آپ کا': 'Your',
                'نام': 'name',
            }
            
            result = text
            for old, new in replacements.items():
                result = result.replace(old, new)
            
            return result
        
        # For other languages, return a placeholder
        return f"[Translated from {source_lang} to {target_lang}]: {text}"
    
    def batch_translate(
        self,
        texts: List[str],
        target_language: str,
        source_language: Optional[str] = None,
        **kwargs
    ) -> List[Translation]:
        """
        Translate multiple texts.
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language code (optional)
            **kwargs: Additional options
            
        Returns:
            List of Translation objects
        """
        return [
            self.translate(text, target_language, source_language, **kwargs)
            for text in texts
        ]
    
    def translate_document(self, document: 'ProcessedDocument', target_language: str) -> 'ProcessedDocument':
        """
        Translate an entire document.
        
        Args:
            document: ProcessedDocument to translate
            target_language: Target language code
            
        Returns:
            New ProcessedDocument with translated content
        """
        from documents.document_processor import ProcessedDocument, DocumentMetadata, DocumentChunk
        
        # Translate content
        translation = self.translate(document.content, target_language)
        
        # Create new metadata
        new_metadata = DocumentMetadata(
            file_path=document.metadata.file_path,
            file_name=document.metadata.file_name,
            file_type=document.metadata.file_type,
            file_size=document.metadata.file_size,
            page_count=document.metadata.page_count,
            word_count=len(translation.text.split()),
            char_count=len(translation.text),
            created_at=document.metadata.created_at,
            modified_at=document.metadata.modified_at,
            title=document.metadata.title,
            author=document.metadata.author,
            language=target_language
        )
        
        # Create new chunks
        new_chunks = []
        for i, chunk in enumerate(document.chunks):
            chunk_translation = self.translate(chunk.text, target_language)
            new_chunks.append(DocumentChunk(
                text=chunk_translation.text,
                chunk_id=chunk.chunk_id,
                start_page=chunk.start_page,
                end_page=chunk.end_page,
                metadata=chunk.metadata
            ))
        
        # Create new document
        return ProcessedDocument(
            metadata=new_metadata,
            content=translation.text,
            chunks=new_chunks
        )
    
    def get_language_name(self, code: str) -> str:
        """Get language name from code"""
        return self.SUPPORTED_LANGUAGES.get(code, code)
    
    def is_supported(self, language: str) -> bool:
        """Check if a language is supported"""
        return language.lower() in [code.lower() for code in self.SUPPORTED_LANGUAGES.keys()]
    
    def detect_and_translate(
        self,
        text: str,
        target_language: str
    ) -> Translation:
        """
        Auto-detect source language and translate.
        
        Args:
            text: Text to translate
            target_language: Target language code
            
        Returns:
            Translation with auto-detected source language
        """
        return self.translate(text, target_language, source_language=None)
