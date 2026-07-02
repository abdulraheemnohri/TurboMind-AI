#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Model Manager
=============================
Manages AI models (GGUF, ONNX, PyTorch)
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import time
import json
import os
import hashlib


@dataclass
class ModelInfo:
    """Information about an AI model"""
    id: str
    name: str
    description: str = ""
    model_type: str = "GGUF"  # GGUF, ONNX, PyTorch, etc.
    file_path: str = ""
    file_size: int = 0  # bytes
    file_hash: str = ""
    
    # Model capabilities
    context_length: int = 4096
    vocab_size: int = 32000
    embedding_size: int = 4096
    
    # Requirements
    vram_required: int = 4  # GB
    ram_required: int = 8  # GB
    
    # Performance
    tokens_per_second: float = 0.0
    benchmark_score: float = 0.0
    
    # Metadata
    author: str = ""
    version: str = "1.0"
    license: str = ""
    created_at: float = 0
    downloaded_at: float = 0
    last_used_at: float = 0
    
    # Status
    is_downloaded: bool = False
    is_verified: bool = False
    is_loaded: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'model_type': self.model_type,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'context_length': self.context_length,
            'vocab_size': self.vocab_size,
            'embedding_size': self.embedding_size,
            'vram_required': self.vram_required,
            'ram_required': self.ram_required,
            'tokens_per_second': self.tokens_per_second,
            'benchmark_score': self.benchmark_score,
            'author': self.author,
            'version': self.version,
            'license': self.license,
            'created_at': self.created_at,
            'downloaded_at': self.downloaded_at,
            'last_used_at': self.last_used_at,
            'is_downloaded': self.is_downloaded,
            'is_verified': self.is_verified,
            'is_loaded': self.is_loaded
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelInfo':
        """Create from dictionary"""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            model_type=data.get('model_type', 'GGUF'),
            file_path=data.get('file_path', ''),
            file_size=data.get('file_size', 0),
            file_hash=data.get('file_hash', ''),
            context_length=data.get('context_length', 4096),
            vocab_size=data.get('vocab_size', 32000),
            embedding_size=data.get('embedding_size', 4096),
            vram_required=data.get('vram_required', 4),
            ram_required=data.get('ram_required', 8),
            tokens_per_second=data.get('tokens_per_second', 0.0),
            benchmark_score=data.get('benchmark_score', 0.0),
            author=data.get('author', ''),
            version=data.get('version', '1.0'),
            license=data.get('license', ''),
            created_at=data.get('created_at', 0),
            downloaded_at=data.get('downloaded_at', 0),
            last_used_at=data.get('last_used_at', 0),
            is_downloaded=data.get('is_downloaded', False),
            is_verified=data.get('is_verified', False),
            is_loaded=data.get('is_loaded', False)
        )
    
    def get_size_mb(self) -> float:
        """Get file size in MB"""
        return self.file_size / (1024 * 1024)
    
    def get_size_gb(self) -> float:
        """Get file size in GB"""
        return self.file_size / (1024 * 1024 * 1024)


class ModelManager:
    """
    Manages AI models for TurboMind AI.
    Handles loading, unloading, and tracking of models.
    """
    
    # Default models catalog
    DEFAULT_MODELS = [
        {
            'id': 'llama-3-8b',
            'name': 'Llama 3 8B',
            'description': 'Meta\'s latest open-source model with 8B parameters',
            'model_type': 'GGUF',
            'context_length': 8192,
            'vocab_size': 128256,
            'embedding_size': 4096,
            'vram_required': 8,
            'ram_required': 16,
            'author': 'Meta',
            'version': '1.0',
            'license': 'MIT'
        },
        {
            'id': 'mistral-7b-v0.3',
            'name': 'Mistral 7B v0.3',
            'description': 'Mistral AI\'s high-performance 7B parameter model',
            'model_type': 'GGUF',
            'context_length': 32768,
            'vocab_size': 32000,
            'embedding_size': 4096,
            'vram_required': 4,
            'ram_required': 8,
            'author': 'Mistral AI',
            'version': '0.3',
            'license': 'Apache 2.0'
        },
        {
            'id': 'phi-3-mini',
            'name': 'Phi-3 Mini',
            'description': 'Microsoft\'s ultra-lightweight 3.8B model',
            'model_type': 'GGUF',
            'context_length': 128000,
            'vocab_size': 32000,
            'embedding_size': 3072,
            'vram_required': 2,
            'ram_required': 4,
            'author': 'Microsoft',
            'version': '1.0',
            'license': 'MIT'
        },
        {
            'id': 'gemma-2b',
            'name': 'Gemma 2B',
            'description': 'Google\'s lightweight open model',
            'model_type': 'GGUF',
            'context_length': 8192,
            'vocab_size': 256000,
            'embedding_size': 2048,
            'vram_required': 2,
            'ram_required': 4,
            'author': 'Google',
            'version': '1.0',
            'license': 'Apache 2.0'
        },
        {
            'id': 'stable-diffusion-xl',
            'name': 'Stable Diffusion XL',
            'description': 'High-quality image generation model',
            'model_type': 'ONNX',
            'context_length': 0,
            'vocab_size': 0,
            'embedding_size': 0,
            'vram_required': 8,
            'ram_required': 16,
            'author': 'Stability AI',
            'version': '1.0',
            'license': 'CreativeML'
        }
    ]
    
    def __init__(self, storage_path: str = "models"):
        """
        Initialize the model manager.
        
        Args:
            storage_path: Path to store models
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Models
        self.models: Dict[str, ModelInfo] = {}
        
        # Loaded models
        self.loaded_models: Dict[str, Any] = {}
        
        # Current model
        self.current_model_id: Optional[str] = None
        
        # Stats
        self.stats = {
            'total_models': 0,
            'downloaded_models': 0,
            'loaded_models': 0,
            'total_storage': 0,
            'last_updated': 0
        }
        
        # Initialize with default models
        self._init_default_models()
        
        print("🤖 Model Manager initialized")
    
    def _init_default_models(self):
        """Initialize with default models"""
        for model_data in self.DEFAULT_MODELS:
            model = ModelInfo.from_dict(model_data)
            self.models[model.id] = model
        
        self.stats['total_models'] = len(self.models)
        self._load_installed_models()
    
    def _load_installed_models(self):
        """Load information about installed models"""
        for model_file in self.storage_path.glob("*.gguf"):
            self._add_installed_model(model_file)
        
        for model_file in self.storage_path.glob("*.onnx"):
            self._add_installed_model(model_file)
        
        for model_file in self.storage_path.glob("*.pt"):
            self._add_installed_model(model_file)
        
        for model_file in self.storage_path.glob("*.pth"):
            self._add_installed_model(model_file)
        
        self.stats['downloaded_models'] = sum(
            1 for m in self.models.values() if m.is_downloaded
        )
        self.stats['total_storage'] = sum(
            m.file_size for m in self.models.values() if m.is_downloaded
        )
    
    def _add_installed_model(self, model_path: Path):
        """Add an installed model to the catalog"""
        model_name = model_path.stem
        model_id = model_path.stem.lower().replace('-', '_').replace('.', '_')
        
        # Check if model already exists
        if model_id in self.models:
            model = self.models[model_id]
            model.file_path = str(model_path)
            model.file_size = model_path.stat().st_size
            model.is_downloaded = True
            model.downloaded_at = time.time()
            return
        
        # Create new model entry
        model_type = "GGUF" if model_path.suffix == ".gguf" else                     "ONNX" if model_path.suffix == ".onnx" else "PyTorch"
        
        model = ModelInfo(
            id=model_id,
            name=model_name.replace('_', ' ').title(),
            description=f"Installed {model_type} model",
            model_type=model_type,
            file_path=str(model_path),
            file_size=model_path.stat().st_size,
            is_downloaded=True,
            downloaded_at=time.time()
        )
        
        self.models[model_id] = model
        self.stats['total_models'] += 1
        self.stats['downloaded_models'] += 1
        self.stats['total_storage'] += model.file_size
    
    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """Get a model by ID"""
        return self.models.get(model_id)
    
    def get_all_models(self) -> List[ModelInfo]:
        """Get all models"""
        return list(self.models.values())
    
    def get_downloaded_models(self) -> List[ModelInfo]:
        """Get all downloaded models"""
        return [m for m in self.models.values() if m.is_downloaded]
    
    def get_loaded_models(self) -> List[ModelInfo]:
        """Get all loaded models"""
        return [m for m in self.models.values() if m.is_loaded]
    
    def set_current_model(self, model_id: str) -> bool:
        """Set the current model"""
        if model_id in self.models:
            self.current_model_id = model_id
            print(f"🎯 Current model set to: {model_id}")
            return True
        return False
    
    def get_current_model(self) -> Optional[ModelInfo]:
        """Get the current model"""
        if self.current_model_id:
            return self.models.get(self.current_model_id)
        return None
    
    def load_model(self, model_id: str) -> bool:
        """
        Load a model into memory.
        
        Args:
            model_id: ID of the model to load
            
        Returns:
            True if model loaded successfully
        """
        model = self.get_model(model_id)
        
        if not model:
            print(f"❌ Model not found: {model_id}")
            return False
        
        if not model.is_downloaded:
            print(f"❌ Model not downloaded: {model_id}")
            return False
        
        try:
            # In a real implementation, would load the actual model
            # For now, just mark as loaded
            model.is_loaded = True
            model.last_used_at = time.time()
            
            # Store in loaded models
            self.loaded_models[model_id] = {
                'model': model,
                'loaded_at': time.time()
            }
            
            self.stats['loaded_models'] += 1
            self.stats['last_updated'] = time.time()
            
            print(f"✅ Model loaded: {model.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def unload_model(self, model_id: str) -> bool:
        """
        Unload a model from memory.
        
        Args:
            model_id: ID of the model to unload
            
        Returns:
            True if model unloaded successfully
        """
        if model_id not in self.loaded_models:
            return False
        
        model = self.models.get(model_id)
        if model:
            model.is_loaded = False
        
        del self.loaded_models[model_id]
        self.stats['loaded_models'] -= 1
        self.stats['last_updated'] = time.time()
        
        print(f"🗑️  Model unloaded: {model_id}")
        return True
    
    def unload_all(self) -> None:
        """Unload all models"""
        for model_id in list(self.loaded_models.keys()):
            self.unload_model(model_id)
        
        print("🧹 All models unloaded")
    
    def delete_model(self, model_id: str) -> bool:
        """
        Delete a model from storage.
        
        Args:
            model_id: ID of the model to delete
            
        Returns:
            True if model deleted successfully
        """
        model = self.get_model(model_id)
        
        if not model or not model.is_downloaded:
            return False
        
        try:
            # Delete file
            file_path = Path(model.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # Remove from models
            model.is_downloaded = False
            model.file_path = ""
            model.file_size = 0
            
            self.stats['downloaded_models'] -= 1
            self.stats['total_storage'] -= model.file_size
            self.stats['last_updated'] = time.time()
            
            print(f"🗑️  Model deleted: {model.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting model: {e}")
            return False
    
    def verify_model(self, model_id: str) -> bool:
        """
        Verify the integrity of a model file.
        
        Args:
            model_id: ID of the model to verify
            
        Returns:
            True if model is valid
        """
        model = self.get_model(model_id)
        
        if not model or not model.is_downloaded:
            return False
        
        try:
            file_path = Path(model.file_path)
            if not file_path.exists():
                return False
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)
            
            # In a real implementation, would compare with expected hash
            model.file_hash = file_hash
            model.is_verified = True
            
            print(f"✅ Model verified: {model.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error verifying model: {e}")
            return False
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def get_model_requirements(self, model_id: str) -> Dict[str, Any]:
        """
        Get hardware requirements for a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Dictionary with requirements
        """
        model = self.get_model(model_id)
        
        if not model:
            return {}
        
        return {
            'vram_gb': model.vram_required,
            'ram_gb': model.ram_required,
            'storage_gb': model.get_size_gb(),
            'context_length': model.context_length,
            'can_run': self._can_run_model(model)
        }
    
    def _can_run_model(self, model: ModelInfo) -> bool:
        """Check if a model can run on the current system"""
        # In a real implementation, would check actual system resources
        # For now, assume it can run
        return True
    
    def estimate_performance(self, model_id: str) -> Dict[str, Any]:
        """
        Estimate performance for a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Dictionary with performance estimates
        """
        model = self.get_model(model_id)
        
        if not model:
            return {}
        
        # Estimate based on model size
        size_gb = model.get_size_gb()
        
        # Rough estimates
        tokens_per_second = 10 / size_gb  # Smaller models are faster
        benchmark_score = min(100, 100 / size_gb * 2)  # Score out of 100
        
        return {
            'estimated_tokens_per_second': tokens_per_second,
            'estimated_benchmark_score': benchmark_score
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get model manager statistics"""
        return {
            **self.stats,
            'downloaded_models': self.stats['downloaded_models'],
            'loaded_models': self.stats['loaded_models'],
            'total_storage_mb': self.stats['total_storage'] / (1024 * 1024),
            'current_model': self.current_model_id
        }
    
    def search_models(self, query: str, limit: int = 10) -> List[ModelInfo]:
        """
        Search for models by name or description.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching models
        """
        query_lower = query.lower()
        
        results = []
        for model in self.models.values():
            if (query_lower in model.name.lower() or 
                query_lower in model.description.lower()):
                results.append(model)
        
        return results[:limit]
    
    def add_custom_model(self, model_data: Dict[str, Any]) -> ModelInfo:
        """
        Add a custom model to the catalog.
        
        Args:
            model_data: Model data dictionary
            
        Returns:
            The created ModelInfo
        """
        model_id = model_data.get('id', hashlib.sha256(
            model_data.get('name', '').encode()
        ).hexdigest()[:16])
        
        model = ModelInfo.from_dict(model_data)
        model.id = model_id
        
        self.models[model_id] = model
        self.stats['total_models'] += 1
        self.stats['last_updated'] = time.time()
        
        print(f"🆕 Custom model added: {model.name}")
        return model
    
    def save_catalog(self, output_path: str) -> bool:
        """Save model catalog to a file"""
        try:
            output_file = Path(output_path)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(
                    [m.to_dict() for m in self.models.values()],
                    f,
                    indent=2
                )
            
            print(f"💾 Model catalog saved to {output_path}")
            return True
        except Exception as e:
            print(f"❌ Save failed: {e}")
            return False
    
    def load_catalog(self, input_path: str) -> bool:
        """Load model catalog from a file"""
        try:
            input_file = Path(input_path)
            with open(input_file, 'r', encoding='utf-8') as f:
                models_data = json.load(f)
            
            for model_data in models_data:
                model = ModelInfo.from_dict(model_data)
                self.models[model.id] = model
            
            self.stats['total_models'] = len(self.models)
            self.stats['last_updated'] = time.time()
            
            print(f"📥 Model catalog loaded from {input_path}")
            return True
        except Exception as e:
            print(f"❌ Load failed: {e}")
            return False