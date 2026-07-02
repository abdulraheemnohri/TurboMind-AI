# TurboMind AI - Vision Package
# ==============================

"""
Vision Package for TurboMind AI.
Handles image processing, OCR, and image generation.

Features:
- Optical Character Recognition (OCR)
- Image Analysis (Object Detection, Scene Description)
- Image Generation (Stable Diffusion XL)
- Image Understanding
- Document Scanning
- Color Detection
- Image Search
"""

from .ocr import OCRProcessor
from .image_analyzer import ImageAnalyzer
from .image_generator import ImageGenerator

__all__ = [
    'OCRProcessor',
    'ImageAnalyzer',
    'ImageGenerator'
]
__version__ = '1.0.0'
