#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Model Settings
==============================
Manages AI model configurations and preferences
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json


@dataclass
class ModelConfig:
    default_model: str = "llama-3-8b"
    models_directory: str = "models"
    auto_load_default: bool = True
    preload_models: List[str] = field(default_factory=lambda: ["llama-3-8b"])
    context_length: int = 4096
    max_new_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.1
    use_gpu: bool = True
    gpu_layers: int = 0
    max_vram_gb: int = 0
    max_ram_gb: int = 0
    num_threads: int = 4
    offload_k: bool = False
    offload_v: bool = False
    prefer_quantized: bool = True
    quantization_type: str = "Q4_K_M"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'default_model': self.default_model,
            'models_directory': self.models_directory,
            'auto_load_default': self.auto_load_default,
            'preload_models': self.preload_models,
            'context_length': self.context_length,
            'max_new_tokens': self.max_new_tokens,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'top_k': self.top_k,
            'repetition_penalty': self.repetition_penalty,
            'use_gpu': self.use_gpu,
            'gpu_layers': self.gpu_layers,
            'max_vram_gb': self.max_vram_gb,
            'max_ram_gb': self.max_ram_gb,
            'num_threads': self.num_threads,
            'offload_k': self.offload_k,
            'offload_v': self.offload_v,
            'prefer_quantized': self.prefer_quantized,
            'quantization_type': self.quantization_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelConfig':
        return cls(
            default_model=data.get('default_model', 'llama-3-8b'),
            models_directory=data.get('models_directory', 'models'),
            auto_load_default=data.get('auto_load_default', True),
            preload_models=data.get('preload_models', ['llama-3-8b']),
            context_length=data.get('context_length', 4096),
            max_new_tokens=data.get('max_new_tokens', 256),
            temperature=data.get('temperature', 0.7),
            top_p=data.get('top_p', 0.9),
            top_k=data.get('top_k', 50),
            repetition_penalty=data.get('repetition_penalty', 1.1),
            use_gpu=data.get('use_gpu', True),
            gpu_layers=data.get('gpu_layers', 0),
            max_vram_gb=data.get('max_vram_gb', 0),
            max_ram_gb=data.get('max_ram_gb', 0),
            num_threads=data.get('num_threads', 4),
            offload_k=data.get('offload_k', False),
            offload_v=data.get('offload_v', False),
            prefer_quantized=data.get('prefer_quantized', True),
            quantization_type=data.get('quantization_type', 'Q4_K_M')
        )


class ModelSettings:
    AVAILABLE_MODELS = {
        'llama-3-8b': {
            'name': 'Llama 3 8B',
            'description': 'Meta latest open-source model with 8B parameters',
            'type': 'GGUF',
            'context_length': 8192,
            'vram_required': 8,
            'ram_required': 16
        },
        'mistral-7b-v0.3': {
            'name': 'Mistral 7B v0.3',
            'description': 'Mistral AI high-performance 7B parameter model',
            'type': 'GGUF',
            'context_length': 32768,
            'vram_required': 4,
            'ram_required': 8
        },
        'phi-3-mini': {
            'name': 'Phi-3 Mini',
            'description': 'Microsoft ultra-lightweight 3.8B model',
            'type': 'GGUF',
            'context_length': 128000,
            'vram_required': 2,
            'ram_required': 4
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("config/models.json")
        self.config = ModelConfig()
        self._load_settings()
        print(" Model Settings initialized")
    
    def _load_settings(self) -> bool:
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.config = ModelConfig.from_dict(data)
                return True
            else:
                self._save_settings()
                return True
        except Exception as e:
            print(f" Error loading model settings: {e}")
            self.config = ModelConfig()
            return False
    
    def _save_settings(self) -> bool:
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=4)
            return True
        except Exception as e:
            print(f" Error saving model settings: {e}")
            return False
    
    def set_default_model(self, model_id: str) -> bool:
        if model_id in self.AVAILABLE_MODELS:
            self.config.default_model = model_id
            self._save_settings()
            return True
        return False
    
    def get_default_model(self) -> Dict[str, Any]:
        model_id = self.config.default_model
        if model_id in self.AVAILABLE_MODELS:
            return {'id': model_id, **self.AVAILABLE_MODELS[model_id]}
        return {}
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        return self.AVAILABLE_MODELS.copy()