#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Model Downloader
===============================
Downloads AI models from various sources
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import time
import requests
import hashlib
import json
import os


@dataclass
class DownloadSource:
    """Represents a source for downloading models"""
    name: str
    url: str
    api_url: Optional[str] = None
    requires_api_key: bool = False
    model_prefix: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'url': self.url,
            'api_url': self.api_url,
            'requires_api_key': self.requires_api_key,
            'model_prefix': self.model_prefix
        }


@dataclass
class DownloadTask:
    """Represents a download task"""
    model_id: str
    model_name: str
    url: str
    output_path: str
    status: str = "pending"  # pending, downloading, completed, failed, cancelled
    progress: float = 0.0
    downloaded_bytes: int = 0
    total_bytes: int = 0
    speed: float = 0.0  # bytes per second
    start_time: float = field(default_factory=time.time)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'model_id': self.model_id,
            'model_name': self.model_name,
            'url': self.url,
            'output_path': self.output_path,
            'status': self.status,
            'progress': self.progress,
            'downloaded_bytes': self.downloaded_bytes,
            'total_bytes': self.total_bytes,
            'speed': self.speed,
            'start_time': self.start_time,
            'error': self.error
        }


@dataclass
class ModelRepository:
    """Represents a model repository"""
    name: str
    description: str
    url: str
    models: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'models': self.models
        }


class ModelDownloader:
    """
    Downloads AI models from various sources.
    Supports HuggingFace, local files, and custom URLs.
    """
    
    # Default repositories
    REPOSITORIES = [
        {
            'name': 'HuggingFace',
            'description': 'HuggingFace model hub',
            'url': 'https://huggingface.co',
            'models': []
        },
        {
            'name': 'Local',
            'description': 'Local file system',
            'url': 'file://',
            'models': []
        }
    ]
    
    # Model catalog URLs
    CATALOG_URLS = {
        'huggingface': 'https://huggingface.co/api/models',
        'gguf': 'https://raw.githubusercontent.com/ggerganov/llama.cpp/master/examples/gguf-vocab.json'
    }
    
    def __init__(self, storage_path: str = "models", download_dir: str = "downloads"):
        """
        Initialize the model downloader.
        
        Args:
            storage_path: Path to store models
            download_dir: Path for temporary downloads
        """
        self.storage_path = Path(storage_path)
        self.download_dir = Path(download_dir)
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Download sources
        self.sources: Dict[str, DownloadSource] = {}
        
        # Download tasks
        self.tasks: Dict[str, DownloadTask] = {}
        
        # Repositories
        self.repositories: Dict[str, ModelRepository] = {}
        
        # Initialize
        self._init_sources()
        self._init_repositories()
        
        print("📥 Model Downloader initialized")
    
    def _init_sources(self):
        """Initialize download sources"""
        # HuggingFace
        self.sources['huggingface'] = DownloadSource(
            name="HuggingFace",
            url="https://huggingface.co",
            api_url="https://huggingface.co/api/models",
            requires_api_key=False
        )
        
        # Local
        self.sources['local'] = DownloadSource(
            name="Local",
            url="file://",
            requires_api_key=False
        )
        
        # Custom
        self.sources['custom'] = DownloadSource(
            name="Custom URL",
            url="",
            requires_api_key=False
        )
    
    def _init_repositories(self):
        """Initialize repositories"""
        for repo_data in self.REPOSITORIES:
            repo = ModelRepository(
                name=repo_data['name'],
                description=repo_data['description'],
                url=repo_data['url'],
                models=repo_data['models']
            )
            self.repositories[repo.name] = repo
    
    def download_model(
        self,
        model_id: str,
        url: str,
        output_name: Optional[str] = None,
        source: str = "custom"
    ) -> Optional[DownloadTask]:
        """
        Start downloading a model.
        
        Args:
            model_id: Unique ID for the model
            url: URL to download from
            output_name: Output file name (optional)
            source: Download source
            
        Returns:
            DownloadTask or None if failed
        """
        if source not in self.sources:
            print(f"❌ Unknown source: {source}")
            return None
        
        # Generate output path
        if output_name:
            output_path = str(self.storage_path / output_name)
        else:
            output_path = str(self.storage_path / f"{model_id}.gguf")
        
        # Create task
        task = DownloadTask(
            model_id=model_id,
            model_name=output_name or model_id,
            url=url,
            output_path=output_path,
            status="pending"
        )
        
        self.tasks[model_id] = task
        
        # Start download in background
        # In a real implementation, would use threading or async
        print(f"📥 Starting download: {model_id}")
        
        return task
    
    def _download_file(self, url: str, output_path: str, callback=None) -> bool:
        """
        Download a file from a URL.
        
        Args:
            url: URL to download
            output_path: Output file path
            callback: Optional callback for progress
            
        Returns:
            True if download successful
        """
        try:
            # Check if URL is local file
            if url.startswith('file://'):
                local_path = Path(url[7:])  # Remove 'file://' prefix
                if local_path.exists():
                    import shutil
                    shutil.copy(local_path, output_path)
                    return True
                return False
            
            # Download from HTTP
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if callback:
                            progress = downloaded / total_size * 100 if total_size > 0 else 0
                            callback(downloaded, total_size, progress)
            
            return True
            
        except Exception as e:
            print(f"❌ Download error: {e}")
            return False
    
    def get_download_progress(self, model_id: str) -> Optional[DownloadTask]:
        """Get download progress for a model"""
        return self.tasks.get(model_id)
    
    def cancel_download(self, model_id: str) -> bool:
        """Cancel a download"""
        if model_id in self.tasks:
            task = self.tasks[model_id]
            task.status = "cancelled"
            print(f"❌ Download cancelled: {model_id}")
            return True
        return False
    
    def get_available_models(self, source: str = "huggingface") -> List[Dict[str, Any]]:
        """
        Get list of available models from a source.
        
        Args:
            source: Download source
            
        Returns:
            List of model dictionaries
        """
        if source == "huggingface":
            return self._get_huggingface_models()
        elif source == "local":
            return self._get_local_models()
        else:
            return []
    
    def _get_huggingface_models(self) -> List[Dict[str, Any]]:
        """Get models from HuggingFace"""
        # In a real implementation, would fetch from API
        # For demo, return some popular models
        return [
            {
                'id': 'llama-3-8b',
                'name': 'Llama 3 8B',
                'description': 'Meta\'s latest open-source model',
                'downloads': 1000000,
                'likes': 50000,
                'size': '16 GB',
                'tags': ['text-generation', 'llama', 'meta']
            },
            {
                'id': 'mistral-7b-v0.3',
                'name': 'Mistral 7B v0.3',
                'description': 'Mistral AI\'s high-performance model',
                'downloads': 800000,
                'likes': 40000,
                'size': '14 GB',
                'tags': ['text-generation', 'mistral']
            },
            {
                'id': 'phi-3-mini',
                'name': 'Phi-3 Mini',
                'description': 'Microsoft\'s ultra-lightweight model',
                'downloads': 500000,
                'likes': 25000,
                'size': '4 GB',
                'tags': ['text-generation', 'phi', 'microsoft']
            },
            {
                'id': 'stable-diffusion-xl',
                'name': 'Stable Diffusion XL',
                'description': 'High-quality image generation',
                'downloads': 2000000,
                'likes': 100000,
                'size': '14 GB',
                'tags': ['image-generation', 'stable-diffusion']
            }
        ]
    
    def _get_local_models(self) -> List[Dict[str, Any]]:
        """Get models from local storage"""
        models = []
        
        for model_file in self.storage_path.glob("*.gguf"):
            models.append({
                'id': model_file.stem,
                'name': model_file.stem.replace('-', ' ').title(),
                'file_path': str(model_file),
                'size': f"{model_file.stat().st_size / (1024 * 1024):.2f} MB",
                'is_downloaded': True
            })
        
        for model_file in self.storage_path.glob("*.onnx"):
            models.append({
                'id': model_file.stem,
                'name': model_file.stem.replace('-', ' ').title(),
                'file_path': str(model_file),
                'size': f"{model_file.stat().st_size / (1024 * 1024):.2f} MB",
                'is_downloaded': True
            })
        
        return models
    
    def search_models(self, query: str, source: str = "huggingface") -> List[Dict[str, Any]]:
        """
        Search for models.
        
        Args:
            query: Search query
            source: Download source
            
        Returns:
            List of matching models
        """
        models = self.get_available_models(source)
        query_lower = query.lower()
        
        return [
            m for m in models
            if query_lower in m['name'].lower() or query_lower in m['description'].lower()
        ]
    
    def get_model_url(self, model_id: str, source: str = "huggingface") -> Optional[str]:
        """
        Get download URL for a model.
        
        Args:
            model_id: Model ID
            source: Download source
            
        Returns:
            Download URL or None
        """
        if source == "huggingface":
            return f"https://huggingface.co/{model_id}/resolve/main/model.gguf"
        elif source == "local":
            return f"file://{self.storage_path}/{model_id}.gguf"
        return None
    
    def verify_download(self, model_id: str, expected_hash: Optional[str] = None) -> bool:
        """
        Verify a downloaded model file.
        
        Args:
            model_id: Model ID
            expected_hash: Expected SHA256 hash
            
        Returns:
            True if file is valid
        """
        task = self.tasks.get(model_id)
        if not task or not Path(task.output_path).exists():
            return False
        
        # Calculate hash
        file_hash = self._calculate_file_hash(Path(task.output_path))
        
        if expected_hash:
            if file_hash != expected_hash:
                print(f"❌ Hash mismatch: {file_hash} != {expected_hash}")
                return False
        
        print(f"✅ Download verified: {model_id}")
        return True
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def get_download_stats(self) -> Dict[str, Any]:
        """Get download statistics"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == "completed")
        failed = sum(1 for t in self.tasks.values() if t.status == "failed")
        downloading = sum(1 for t in self.tasks.values() if t.status == "downloading")
        
        return {
            'total': total,
            'completed': completed,
            'failed': failed,
            'downloading': downloading,
            'pending': total - completed - failed - downloading
        }
    
    def clear_downloads(self) -> None:
        """Clear all download tasks"""
        self.tasks.clear()
        print("🧹 Download tasks cleared")
    
    def cleanup_downloads(self) -> None:
        """Clean up temporary download files"""
        for download_file in self.download_dir.glob("*"):
            try:
                download_file.unlink()
            except:
                pass
        
        print("🧹 Temporary downloads cleaned up")
    
    def add_source(self, name: str, url: str, api_url: Optional[str] = None, requires_api_key: bool = False) -> bool:
        """
        Add a custom download source.
        
        Args:
            name: Source name
            url: Base URL
            api_url: API URL (optional)
            requires_api_key: Whether API key is required
            
        Returns:
            True if source added
        """
        if name in self.sources:
            return False
        
        self.sources[name] = DownloadSource(
            name=name,
            url=url,
            api_url=api_url,
            requires_api_key=requires_api_key
        )
        
        print(f"🆕 Source added: {name}")
        return True
    
    def remove_source(self, name: str) -> bool:
        """Remove a download source"""
        if name in self.sources:
            del self.sources[name]
            print(f"🗑️  Source removed: {name}")
            return True
        return False
    
    def get_sources(self) -> Dict[str, DownloadSource]:
        """Get all download sources"""
        return self.sources.copy()