# TurboMind AI - Models Package
# ===============================

"""
Models Package for TurboMind AI.
Handles AI model management, downloading, and benchmarking.

Features:
- Model Management (GGUF, ONNX, PyTorch)
- Model Downloading
- Model Benchmarking
- Model Verification
- RAM Estimation
- Storage Management
"""

from .model_manager import ModelManager
from .model_downloader import ModelDownloader
from .benchmark import ModelBenchmark

__all__ = [
    'ModelManager',
    'ModelDownloader',
    'ModelBenchmark'
]
__version__ = '1.0.0'