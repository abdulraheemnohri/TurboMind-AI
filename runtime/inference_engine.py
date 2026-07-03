#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Inference Engine
===============================
Handles AI model inference and execution using PyTorch and Transformers
"""

import os
import json
import time
import torch
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union


class InferenceEngine:
    """
    Core inference engine for running AI models on-device.
    Supports quantized models for efficient execution on mobile devices.
    Works completely offline once models are downloaded.
    """
    
    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize the inference engine.
        
        Args:
            model_path: Path to the model file or directory
            device: Device to use ('cpu', 'cuda', 'mps', 'xpu')
        """
        self.model = None
        self.tokenizer = None
        self.device = self._get_best_device() if device is None else device
        self.model_path = Path(model_path) if model_path else None
        self.is_loaded = False
        self.model_info = {}
        self.model_type = None  # 'causal', 'seq2seq', 'encoder', etc.
        self.quantized = False
        
        # Initialize device
        self._setup_device()
        
        print(f"🔧 Inference Engine initialized on device: {self.device}")
    
    def _setup_device(self) -> None:
        """Setup the computation device"""
        if self.device == 'cuda' and torch.cuda.is_available():
            self.device = 'cuda'
        elif self.device == 'mps' and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            self.device = 'mps'
        elif self.device == 'xpu' and hasattr(torch, 'xpu') and torch.xpu.is_available():
            self.device = 'xpu'
        else:
            self.device = 'cpu'
    
    def _get_best_device(self) -> str:
        """Detect the best available device (CPU, GPU, NPU)"""
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"
        elif hasattr(torch, 'xpu') and torch.xpu.is_available():
            return "xpu"
        else:
            return "cpu"
    
    def load_model(
        self,
        model_path: Union[str, Path],
        model_type: str = "auto",
        quantized: bool = False,
        trust_remote_code: bool = False,
        **kwargs
    ) -> bool:
        """
        Load a model from file or directory.
        
        Args:
            model_path: Path to the model file or directory
            model_type: Type of model ('causal', 'seq2seq', 'encoder', 'auto')
            quantized: Whether the model is quantized
            trust_remote_code: Trust remote code when loading
            **kwargs: Additional loading options
            
        Returns:
            bool: True if model loaded successfully
        """
        try:
            model_path = Path(model_path)
            
            if not model_path.exists():
                print(f"❌ Model path not found: {model_path}")
                return False
            
            self.model_path = model_path
            self.quantized = quantized
            
            print(f"📂 Loading model from: {model_path}")
            
            # Try to load with Transformers
            try:
                from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer
                
                # Detect model type
                if model_type == "auto":
                    # Try to detect from config.json
                    config_path = model_path / "config.json"
                    if config_path.exists():
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                        model_type = config.get('model_type', 'causal')
                    else:
                        model_type = 'causal'
                
                # Load tokenizer
                tokenizer_path = model_path
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        str(tokenizer_path),
                        trust_remote_code=trust_remote_code
                    )
                    print("✅ Tokenizer loaded")
                except Exception as e:
                    print(f"⚠️  Could not load tokenizer: {e}")
                    # Try to create a basic tokenizer
                    self.tokenizer = self._create_basic_tokenizer()
                
                # Load model based on type
                if model_type in ['causal', 'decoder']:
                    self.model = AutoModelForCausalLM.from_pretrained(
                        str(model_path),
                        device_map=self.device,
                        torch_dtype=self._get_torch_dtype(),
                        trust_remote_code=trust_remote_code,
                        quantized=quantized,
                        **kwargs
                    )
                    self.model_type = 'causal'
                elif model_type in ['seq2seq', 'encoder-decoder']:
                    self.model = AutoModelForSeq2SeqLM.from_pretrained(
                        str(model_path),
                        device_map=self.device,
                        torch_dtype=self._get_torch_dtype(),
                        trust_remote_code=trust_remote_code,
                        **kwargs
                    )
                    self.model_type = 'seq2seq'
                else:
                    # Try auto detection
                    try:
                        self.model = AutoModelForCausalLM.from_pretrained(
                            str(model_path),
                            device_map=self.device,
                            torch_dtype=self._get_torch_dtype(),
                            trust_remote_code=trust_remote_code,
                            **kwargs
                        )
                        self.model_type = 'causal'
                    except:
                        self.model = AutoModelForSeq2SeqLM.from_pretrained(
                            str(model_path),
                            device_map=self.device,
                            torch_dtype=self._get_torch_dtype(),
                            trust_remote_code=trust_remote_code,
                            **kwargs
                        )
                        self.model_type = 'seq2seq'
                
                # Move model to device
                self.model.to(self.device)
                self.model.eval()
                
                self.is_loaded = True
                
                # Get model info
                self.model_info = {
                    'path': str(model_path),
                    'size': self._get_model_size(model_path),
                    'device': self.device,
                    'type': self.model_type,
                    'quantized': quantized,
                    'loaded_at': time.time()
                }
                
                print(f"✅ Model loaded successfully on {self.device}")
                print(f"   Type: {self.model_type}")
                print(f"   Quantized: {quantized}")
                return True
                
            except ImportError:
                print("⚠️  Transformers not installed. Install with: pip install transformers")
                return False
                
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_torch_dtype(self) -> torch.dtype:
        """Get the appropriate torch dtype based on device"""
        if self.device == 'cuda':
            if torch.cuda.is_bf16_supported():
                return torch.bfloat16
            elif torch.cuda.is_fp16_supported():
                return torch.float16
        return torch.float32
    
    def _get_model_size(self, model_path: Path) -> int:
        """Calculate model size in MB"""
        total_size = 0
        for f in model_path.rglob('*'):
            if f.is_file():
                total_size += f.stat().st_size
        return total_size // (1024 * 1024)  # MB
    
    def _create_basic_tokenizer(self):
        """Create a basic tokenizer if AutoTokenizer fails"""
        from transformers import PreTrainedTokenizerFast
        
        # Create a simple wordpiece tokenizer
        vocab = {"[PAD]": 0, "[UNK]": 1, "[CLS]": 2, "[SEP]": 3, "[MASK]": 4}
        merges = []
        
        class BasicTokenizer(PreTrainedTokenizerFast):
            def __init__(self):
                super().__init__(
                    vocab=vocab,
                    merges=merges,
                    unk_token="[UNK]",
                    pad_token="[PAD]",
                    cls_token="[CLS]",
                    sep_token="[SEP]",
                    mask_token="[MASK]"
                )
        
        return BasicTokenizer()
    
    def unload_model(self) -> None:
        """Unload the current model to free memory"""
        if self.model is not None:
            del self.model
            self.model = None
        
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        
        if self.device == 'cuda' and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.is_loaded = False
        self.model_info = {}
        print("🗑️  Model unloaded")
    
    def infer(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        repetition_penalty: float = 1.1,
        num_beams: int = 1,
        do_sample: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run inference on a prompt.
        
        Args:
            prompt: Input text prompt
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Temperature for sampling (0-1)
            top_p: Top-p (nucleus) sampling
            top_k: Top-k sampling
            repetition_penalty: Penalty for repetition
            num_beams: Number of beams for beam search
            do_sample: Whether to sample or use greedy decoding
            **kwargs: Additional generation parameters
            
        Returns:
            dict: Inference results with generated text and metadata
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        if not self.tokenizer:
            raise RuntimeError("Tokenizer not loaded.")
        
        start_time = time.time()
        
        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate output
            if self.model_type == 'causal':
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    repetition_penalty=repetition_penalty,
                    num_beams=num_beams,
                    do_sample=do_sample,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    **kwargs
                )
            else:  # seq2seq
                outputs = self.model.generate(
                    **inputs,
                    max_length=len(inputs['input_ids'][0]) + max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    repetition_penalty=repetition_penalty,
                    num_beams=num_beams,
                    do_sample=do_sample,
                    **kwargs
                )
            
            # Decode output
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Clean up the output (remove prompt if it's included)
            if self.model_type == 'causal' and generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):]
            
            elapsed = time.time() - start_time
            
            # Get memory usage
            memory_info = self._get_memory_usage()
            
            result = {
                'text': generated_text.strip(),
                'prompt': prompt,
                'input_tokens': len(inputs['input_ids'][0]),
                'output_tokens': len(outputs[0]),
                'total_tokens': len(inputs['input_ids'][0]) + len(outputs[0]),
                'inference_time': elapsed,
                'model': str(self.model_path) if self.model_path else 'unknown',
                'model_type': self.model_type,
                'device': self.device,
                'temperature': temperature,
                'memory_usage_mb': memory_info.get('used', 0)
            }
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'prompt': prompt,
                'inference_time': time.time() - start_time
            }
    
    def stream_infer(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Run streaming inference for real-time responses.
        
        Args:
            prompt: Input text prompt
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Temperature for sampling
            **kwargs: Additional generation parameters
            
        Returns:
            list: Stream of inference results
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        results = []
        
        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Streaming generation
            if self.model_type == 'causal':
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    **kwargs
                )
                
                # For streaming, we'll return the full output
                # In a real implementation, this would yield tokens one by one
                generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                if generated_text.startswith(prompt):
                    generated_text = generated_text[len(prompt):]
                
                results.append({
                    'text': generated_text.strip(),
                    'done': True
                })
            else:
                # For now, just return single result
                result = self.infer(prompt, max_new_tokens, temperature, **kwargs)
                results.append(result)
            
            return results
            
        except Exception as e:
            return [{'error': str(e), 'done': True}]
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run chat-style inference with conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Temperature for sampling
            **kwargs: Additional generation parameters
            
        Returns:
            dict: Inference results with assistant's response
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Format messages for the model
        # This is a simple implementation - real models may need different formatting
        prompt = self._format_chat_prompt(messages)
        
        # Run inference
        result = self.infer(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            **kwargs
        )
        
        # Return in chat format
        return {
            'role': 'assistant',
            'content': result.get('text', ''),
            'usage': {
                'prompt_tokens': result.get('input_tokens', 0),
                'completion_tokens': result.get('output_tokens', 0),
                'total_tokens': result.get('total_tokens', 0)
            },
            'model': result.get('model', 'unknown')
        }
    
    def _format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages into a prompt for the model"""
        prompt = ""
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                prompt += f"System: {content}
"
            elif role == 'user':
                prompt += f"User: {content}
"
            elif role == 'assistant':
                prompt += f"Assistant: {content}
"
        
        prompt += "Assistant: "
        return prompt
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return self.model_info.copy()
    
    def estimate_memory_usage(self) -> Dict[str, float]:
        """Estimate memory usage of the loaded model"""
        return self._get_memory_usage()
    
    def _get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        try:
            import psutil
            import torch
            
            # Get process memory
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            
            # Get GPU memory if available
            gpu_memory = 0
            if self.device == 'cuda' and torch.cuda.is_available():
                gpu_memory = torch.cuda.memory_allocated(self.device) / (1024 * 1024)
            
            return {
                'total_mb': mem_info.rss / (1024 * 1024),
                'available_mb': psutil.virtual_memory().available / (1024 * 1024),
                'used_mb': mem_info.rss / (1024 * 1024),
                'gpu_used_mb': gpu_memory,
                'gpu_total_mb': torch.cuda.get_device_properties(self.device).total_memory / (1024 * 1024) if self.device == 'cuda' else 0
            }
        except:
            return {
                'total_mb': 0,
                'available_mb': 0,
                'used_mb': 0,
                'gpu_used_mb': 0,
                'gpu_total_mb': 0
            }
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get information about the current device"""
        info = {
            'device': self.device,
            'device_type': 'cpu'
        }
        
        if self.device == 'cuda':
            info.update({
                'device_type': 'gpu',
                'device_name': torch.cuda.get_device_name(self.device),
                'device_count': torch.cuda.device_count(),
                'memory_total_mb': torch.cuda.get_device_properties(self.device).total_memory / (1024 * 1024),
                'memory_used_mb': torch.cuda.memory_allocated(self.device) / (1024 * 1024)
            })
        elif self.device == 'mps':
            info['device_type'] = 'apple_metal'
        elif self.device == 'xpu':
            info['device_type'] = 'intel_xpu'
        
        return info
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.is_loaded
    
    def supports_quantization(self) -> bool:
        """Check if quantization is supported"""
        return self.quantized or self._check_quantization_support()
    
    def _check_quantization_support(self) -> bool:
        """Check if the current device supports quantization"""
        if self.device == 'cuda':
            return torch.cuda.is_available()
        return True  # CPU always supports quantization
    
    def get_tokenizer_info(self) -> Dict[str, Any]:
        """Get information about the tokenizer"""
        if not self.tokenizer:
            return {}
        
        return {
            'vocab_size': self.tokenizer.vocab_size,
            'max_length': getattr(self.tokenizer, 'model_max_length', 0),
            'pad_token': self.tokenizer.pad_token,
            'eos_token': self.tokenizer.eos_token,
            'unk_token': self.tokenizer.unk_token
        }
