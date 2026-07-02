#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Generation Engine
================================
Handles text generation from AI models
"""

import time
import random
from typing import Dict, Any, List, Optional, Iterator, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum


class GenerationMode(Enum):
    """Generation modes"""
    GREEDY = "greedy"  # Always pick most probable token
    BEAM_SEARCH = "beam_search"  # Keep top k sequences
    SAMPLING = "sampling"  # Sample from distribution
    TOP_K = "top_k"  # Sample from top k tokens
    TOP_P = "top_p"  # Nucleus sampling


@dataclass
class GenerationConfig:
    """Configuration for text generation"""
    mode: GenerationMode = GenerationMode.SAMPLING
    max_tokens: int = 512
    temperature: float = 0.7
    top_k: int = 50
    top_p: float = 0.95
    repetition_penalty: float = 1.0
    num_beams: int = 1
    early_stopping: bool = True
    stop_sequences: List[str] = field(default_factory=lambda: ["</s>", "<|endoftext|>"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'mode': self.mode.value,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'top_k': self.top_k,
            'top_p': self.top_p,
            'repetition_penalty': self.repetition_penalty,
            'num_beams': self.num_beams,
            'early_stopping': self.early_stopping,
            'stop_sequences': self.stop_sequences
        }


@dataclass
class GenerationResult:
    """Result of text generation"""
    text: str
    token_ids: List[int]
    finish_reason: str  # 'stop', 'length', 'error'
    generated_tokens: int
    generation_time: float
    config: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


class GenerationEngine:
    """
    Handles text generation from AI models.
    Supports various generation modes and configurations.
    """
    
    def __init__(self, inference_engine=None):
        """
        Initialize the generation engine.
        
        Args:
            inference_engine: Optional inference engine for actual model calls
        """
        self.inference_engine = inference_engine
        self.default_config = GenerationConfig()
        self.history: List[GenerationResult] = []
        
        print("✍️  Generation Engine initialized")
    
    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> GenerationResult:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input prompt
            config: Generation configuration (optional)
            **kwargs: Additional configuration overrides
            
        Returns:
            GenerationResult with generated text and metadata
        """
        start_time = time.time()
        
        # Merge config with defaults and kwargs
        gen_config = self._merge_config(config, **kwargs)
        
        try:
            # For demo purposes, generate mock response
            # In production, this would call the inference engine
            if self.inference_engine:
                # Use inference engine
                result = self.inference_engine.infer(prompt)
                generated_text = result.get('text', '')
            else:
                # Generate mock response
                generated_text = self._generate_mock_response(prompt, gen_config)
            
            # Create result
            result = GenerationResult(
                text=generated_text,
                token_ids=[],  # Would be filled with actual token IDs
                finish_reason='stop',
                generated_tokens=len(generated_text.split()),
                generation_time=time.time() - start_time,
                config=gen_config.to_dict(),
                metadata={
                    'prompt_tokens': len(prompt.split()),
                    'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt
                }
            )
            
            # Save to history
            self.history.append(result)
            
            return result
            
        except Exception as e:
            return GenerationResult(
                text='',
                token_ids=[],
                finish_reason='error',
                generated_tokens=0,
                generation_time=time.time() - start_time,
                config=gen_config.to_dict(),
                metadata={'error': str(e)}
            )
    
    def stream_generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> Iterator[GenerationResult]:
        """
        Generate text with streaming (yield results as they're generated).
        
        Args:
            prompt: Input prompt
            config: Generation configuration
            **kwargs: Additional configuration
            
        Yields:
            GenerationResult chunks as they're generated
        """
        start_time = time.time()
        gen_config = self._merge_config(config, **kwargs)
        
        # For demo, generate word by word
        if self.inference_engine:
            # Use streaming from inference engine
            results = self.inference_engine.stream_infer(prompt)
            for result in results:
                yield GenerationResult(
                    text=result.get('text', ''),
                    token_ids=[],
                    finish_reason=result.get('finish_reason', 'stop'),
                    generated_tokens=len(result.get('text', '').split()),
                    generation_time=time.time() - start_time,
                    config=gen_config.to_dict()
                )
        else:
            # Mock streaming
            mock_text = self._generate_mock_response(prompt, gen_config)
            words = mock_text.split()
            
            for i in range(1, len(words) + 1):
                partial_text = ' '.join(words[:i])
                yield GenerationResult(
                    text=partial_text,
                    token_ids=[],
                    finish_reason='stop' if i == len(words) else 'streaming',
                    generated_tokens=i,
                    generation_time=time.time() - start_time,
                    config=gen_config.to_dict()
                )
                time.sleep(0.05)  # Simulate generation time
    
    async def async_stream_generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None,
        **kwargs
    ) -> AsyncIterator[GenerationResult]:
        """
        Async version of stream_generate.
        
        Args:
            prompt: Input prompt
            config: Generation configuration
            **kwargs: Additional configuration
            
        Yields:
            GenerationResult chunks as they're generated
        """
        for result in self.stream_generate(prompt, config, **kwargs):
            yield result
    
    def _generate_mock_response(self, prompt: str, config: GenerationConfig) -> str:
        """Generate a mock response for demo purposes"""
        # Simple mock responses based on prompt
        prompt_lower = prompt.lower()
        
        responses = [
            f"I understand you're asking about: {prompt[:50]}...",
            f"That's an interesting question! Based on what you've asked, here's my response...",
            f"Let me think about '{prompt[:30]}'...",
            f"Here's what I know about your query: {prompt[:40]}...",
            f"I can help you with that. {prompt[:35]} is a fascinating topic."
        ]
        
        return random.choice(responses)
    
    def _merge_config(
        self,
        config: Optional[GenerationConfig],
        **kwargs
    ) -> GenerationConfig:
        """Merge configuration with defaults and overrides"""
        # Start with defaults
        merged = GenerationConfig(
            mode=getattr(config, 'mode', self.default_config.mode) if config else self.default_config.mode,
            max_tokens=getattr(config, 'max_tokens', kwargs.get('max_tokens', self.default_config.max_tokens)),
            temperature=getattr(config, 'temperature', kwargs.get('temperature', self.default_config.temperature)),
            top_k=getattr(config, 'top_k', kwargs.get('top_k', self.default_config.top_k)),
            top_p=getattr(config, 'top_p', kwargs.get('top_p', self.default_config.top_p)),
            repetition_penalty=getattr(config, 'repetition_penalty', kwargs.get('repetition_penalty', self.default_config.repetition_penalty)),
            num_beams=getattr(config, 'num_beams', kwargs.get('num_beams', self.default_config.num_beams)),
            early_stopping=getattr(config, 'early_stopping', kwargs.get('early_stopping', self.default_config.early_stopping)),
            stop_sequences=getattr(config, 'stop_sequences', kwargs.get('stop_sequences', self.default_config.stop_sequences))
        )
        
        return merged
    
    def set_default_config(self, config: GenerationConfig) -> None:
        """Set default generation configuration"""
        self.default_config = config
    
    def get_history(self, limit: int = 10) -> List[GenerationResult]:
        """Get generation history"""
        return self.history[-limit:]
    
    def clear_history(self) -> None:
        """Clear generation history"""
        self.history.clear()
    
    def apply_repetition_penalty(
        self,
        token_ids: List[int],
        penalty: float
    ) -> List[float]:
        """
        Apply repetition penalty to token scores.
        
        Args:
            token_ids: List of previously generated token IDs
            penalty: Repetition penalty factor
            
        Returns:
            List of penalty factors for each token
        """
        # Count token frequencies
        token_counts = {}
        for token_id in token_ids:
            token_counts[token_id] = token_counts.get(token_id, 0) + 1
        
        # Calculate penalties
        penalties = []
        for token_id in token_counts:
            count = token_counts[token_id]
            penalties.append(1.0 / (1.0 + (count - 1) * penalty))
        
        return penalties
    
    def sample_from_distribution(
        self,
        scores: List[float],
        temperature: float = 1.0,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None
    ) -> int:
        """
        Sample a token from a probability distribution.
        
        Args:
            scores: Raw scores for each token
            temperature: Temperature for sampling
            top_k: Number of top tokens to consider
            top_p: Nucleus sampling probability
            
        Returns:
            Index of sampled token
        """
        # Apply temperature
        if temperature > 0:
            scores = [s / temperature for s in scores]
        
        # Softmax to get probabilities
        max_score = max(scores)
        exp_scores = [pow(2.71828, s - max_score) for s in scores]
        sum_exp = sum(exp_scores)
        probs = [e / sum_exp for e in exp_scores]
        
        # Apply top-k filtering
        if top_k is not None and top_k < len(probs):
            top_indices = sorted(range(len(probs)), key=lambda i: -probs[i])[:top_k]
            mask = [False] * len(probs)
            for idx in top_indices:
                mask[idx] = True
            probs = [p if mask[i] else 0 for i, p in enumerate(probs)]
            sum_p = sum(probs)
            if sum_p > 0:
                probs = [p / sum_p for p in probs]
        
        # Apply top-p (nucleus) filtering
        if top_p is not None and top_p < 1.0:
            sorted_probs = sorted(probs, reverse=True)
            cumulative = 0.0
            cutoff = None
            for i, p in enumerate(sorted_probs):
                cumulative += p
                if cumulative >= top_p:
                    cutoff = sorted_probs[i]
                    break
            
            if cutoff is not None:
                probs = [p if p >= cutoff else 0 for p in probs]
                sum_p = sum(probs)
                if sum_p > 0:
                    probs = [p / sum_p for p in probs]
        
        # Sample
        rand = random.random()
        cumulative = 0.0
        for i, p in enumerate(probs):
            cumulative += p
            if rand <= cumulative:
                return i
        
        return len(probs) - 1
