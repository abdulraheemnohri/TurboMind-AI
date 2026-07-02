#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Summarizer
==========================
Generates summaries of documents and text
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import re


@dataclass
class Summary:
    """Represents a generated summary"""
    text: str
    type: str  # 'abstractive' or 'extractive'
    ratio: float  # Compression ratio (original_length / summary_length)
    original_length: int
    summary_length: int
    key_points: List[str]
    metadata: Dict[str, Any]


class Summarizer:
    """
    Generates summaries of text using various techniques.
    Supports both extractive and abstractive summarization.
    """
    
    def __init__(self):
        """Initialize the summarizer"""
        print("📝 Summarizer initialized")
    
    def summarize(
        self,
        text: str,
        ratio: float = 0.2,
        method: str = "extractive",
        **kwargs
    ) -> Summary:
        """
        Generate a summary of the given text.
        
        Args:
            text: Text to summarize
            ratio: Compression ratio (0-1, where 0.2 = 20% of original)
            method: Summarization method ('extractive' or 'abstractive')
            **kwargs: Additional options
            
        Returns:
            Summary object with generated summary
        """
        if not text or not text.strip():
            return Summary(
                text="",
                type=method,
                ratio=0,
                original_length=0,
                summary_length=0,
                key_points=[],
                metadata={}
            )
        
        original_length = len(text.split())
        
        if method == "extractive":
            summary_text, key_points = self._extractive_summarize(text, ratio)
        else:  # abstractive
            summary_text, key_points = self._abstractive_summarize(text, ratio, **kwargs)
        
        summary_length = len(summary_text.split())
        actual_ratio = original_length / summary_length if summary_length > 0 else 0
        
        return Summary(
            text=summary_text,
            type=method,
            ratio=actual_ratio,
            original_length=original_length,
            summary_length=summary_length,
            key_points=key_points,
            metadata={
                'method': method,
                'target_ratio': ratio
            }
        )
    
    def _extractive_summarize(self, text: str, ratio: float) -> tuple:
        """
        Extractive summarization: Select important sentences.
        
        Args:
            text: Text to summarize
            ratio: Target compression ratio
            
        Returns:
            tuple: (summary_text, key_points)
        """
        sentences = self._split_sentences(text)
        
        if not sentences:
            return "", []
        
        # Calculate how many sentences to keep
        target_count = max(1, int(len(sentences) * ratio))
        
        # Score sentences by importance
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = self._score_sentence(sentence, i, sentences)
            scored_sentences.append((sentence, score))
        
        # Sort by score and select top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        selected = scored_sentences[:target_count]
        
        # Extract key points (top 3 sentences)
        key_points = [s[0] for s in selected[:3]]
        
        # Create summary
        summary = ' '.join([s[0] for s in selected])
        
        return summary, key_points
    
    def _abstractive_summarize(self, text: str, ratio: float, **kwargs) -> tuple:
        """
        Abstractive summarization: Generate new summary text.
        For demo, uses simple techniques. In production, would use AI models.
        
        Args:
            text: Text to summarize
            ratio: Target compression ratio
            **kwargs: Additional options
            
        Returns:
            tuple: (summary_text, key_points)
        """
        # For demo, use extractive and then paraphrase
        extractive_summary, key_points = self._extractive_summarize(text, ratio * 1.5)
        
        # Simple paraphrasing (in production, use AI model)
        summary = self._simple_paraphrase(extractive_summary)
        
        return summary, key_points
    
    def _score_sentence(self, sentence: str, index: int, all_sentences: List[str]) -> float:
        """Score a sentence for extractive summarization"""
        score = 0
        
        # Length factor (medium sentences are better)
        words = len(sentence.split())
        if 10 < words < 30:
            score += 0.3
        elif 5 < words < 50:
            score += 0.2
        
        # Position factor (first and last sentences are important)
        total = len(all_sentences)
        if index < 2 or index >= total - 2:
            score += 0.4
        
        # Capitalization (proper nouns, start of sentences)
        if sentence[0].isupper():
            score += 0.1
        
        # Punctuation (complete sentences)
        if sentence.strip().endswith(('.', '!', '?')):
            score += 0.2
        
        # Keywords (common important words)
        keywords = ['importance', 'main', 'key', 'primary', 'result', 'conclusion',
                   'summary', 'findings', 'however', 'therefore', 'thus', 'finally']
        for keyword in keywords:
            if keyword in sentence.lower():
                score += 0.1
        
        return score
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'(?<![\w\.])[\.\!\?]+\s*', text)
        
        # Filter and clean
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _simple_paraphrase(self, text: str) -> str:
        """Simple paraphrasing (for demo only)"""
        # In a real implementation, this would use an AI model
        # For now, just return the text with minor modifications
        
        # Replace some common phrases
        replacements = {
            'The ': 'A ',
            'This ': 'That ',
            'These ': 'Those ',
            'It is ': 'This is ',
            'They are ': 'Those are '
        }
        
        result = text
        for old, new in replacements.items():
            result = result.replace(old, new)
        
        return result
    
    def bullet_point_summary(self, text: str, num_points: int = 5) -> List[str]:
        """
        Generate a bullet-point summary.
        
        Args:
            text: Text to summarize
            num_points: Number of bullet points
            
        Returns:
            List of bullet points
        """
        summary = self.summarize(text, ratio=0.3)
        sentences = self._split_sentences(summary.text)
        
        # Select top sentences
        points = sentences[:num_points]
        
        # Format as bullet points
        return [f"• {p}" for p in points if p]
    
    def executive_summary(self, text: str) -> Dict[str, str]:
        """
        Generate an executive summary with multiple sections.
        
        Args:
            text: Text to summarize
            
        Returns:
            Dictionary with summary sections
        """
        # Generate different summary ratios
        short = self.summarize(text, ratio=0.1)
        medium = self.summarize(text, ratio=0.25)
        long = self.summarize(text, ratio=0.4)
        
        return {
            'short': short.text,
            'medium': medium.text,
            'long': long.text,
            'key_points': '\n'.join(medium.key_points)
        }
    
    def summarize_document(self, document: 'ProcessedDocument') -> Summary:
        """
        Summarize a processed document.
        
        Args:
            document: ProcessedDocument to summarize
            
        Returns:
            Summary of the document
        """
        return self.summarize(document.content)
    
    def summarize_chunks(self, chunks: List[str]) -> List[Summary]:
        """
        Summarize multiple text chunks.
        
        Args:
            chunks: List of text chunks to summarize
            
        Returns:
            List of summaries for each chunk
        """
        return [self.summarize(chunk) for chunk in chunks]
