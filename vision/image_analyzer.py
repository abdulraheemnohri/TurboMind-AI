#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Image Analyzer
=============================
Analyzes images for content, objects, colors, etc.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np


@dataclass
class ImageAnalysis:
    """Complete analysis of an image"""
    file_path: str
    file_name: str
    file_size: int
    width: int
    height: int
    
    # Content analysis
    objects: List[Dict[str, Any]] = field(default_factory=list)
    text_regions: List[Dict[str, Any]] = field(default_factory=list)
    dominant_colors: List[Dict[str, Any]] = field(default_factory=list)
    color_palette: List[Tuple[float, float, float]] = field(default_factory=list)
    
    # Scene analysis
    scene_description: str = ""
    scene_categories: List[str] = field(default_factory=list)
    scene_confidence: float = 0.0
    
    # Technical analysis
    brightness: float = 0.0
    contrast: float = 0.0
    sharpness: float = 0.0
    blur_level: float = 0.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DetectedObject:
    """A detected object in an image"""
    label: str
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # (x, y, width, height)
    category: str = "object"


class ImageAnalyzer:
    """
    Analyzes images for various features.
    Supports object detection, scene recognition, color analysis, etc.
    """
    
    def __init__(self):
        """Initialize the image analyzer"""
        self.initialized = False
        self._init_models()
        print("🖼️  Image Analyzer initialized")
    
    def _init_models(self):
        """Initialize analysis models"""
        try:
            # Try to import CV2
            import cv2
            self.cv2 = cv2
            self.initialized = True
        except ImportError:
            print("⚠️  OpenCV not installed. Install with: pip install opencv-python")
            self.initialized = False
    
    def analyze(self, image_path: str, **kwargs) -> Optional[ImageAnalysis]:
        """
        Perform complete analysis of an image.
        
        Args:
            image_path: Path to the image file
            **kwargs: Analysis options
            
        Returns:
            ImageAnalysis with all analysis results
        """
        if not self.initialized:
            print("❌ Image analyzer not initialized")
            return None
        
        try:
            # Load image
            img = self._load_image(image_path)
            if img is None:
                return None
            
            # Get basic info
            height, width = img.shape[:2]
            file_size = Path(image_path).stat().st_size
            
            analysis = ImageAnalysis(
                file_path=image_path,
                file_name=Path(image_path).name,
                file_size=file_size,
                width=width,
                height=height
            )
            
            # Perform analyses
            analysis.dominant_colors = self._analyze_colors(img)
            analysis.color_palette = self._extract_color_palette(img)
            analysis.brightness = self._calculate_brightness(img)
            analysis.contrast = self._calculate_contrast(img)
            analysis.sharpness = self._calculate_sharpness(img)
            analysis.blur_level = self._calculate_blur(img)
            
            # Try object detection
            analysis.objects = self._detect_objects(img)
            
            # Try scene recognition
            analysis.scene_description, analysis.scene_categories, analysis.scene_confidence = \
                self._recognize_scene(img)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing image: {e}")
            return None
    
    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load an image file"""
        try:
            return self.cv2.imread(image_path)
        except:
            try:
                from PIL import Image
                img = Image.open(image_path)
                return np.array(img)
            except:
                return None
    
    def _analyze_colors(self, img: np.ndarray) -> List[Dict[str, Any]]:
        """Analyze dominant colors in the image"""
        # Resize for faster processing
        small_img = self.cv2.resize(img, (100, 100))
        
        # Convert to RGB if BGR
        if len(small_img.shape) == 3 and small_img.shape[2] == 3:
            rgb_img = self.cv2.cvtColor(small_img, self.cv2.COLOR_BGR2RGB)
        else:
            rgb_img = small_img
        
        # Reshape to list of pixels
        pixels = rgb_img.reshape(-1, 3)
        pixels = np.float32(pixels)
        
        # Use K-means clustering to find dominant colors
        criteria = (self.cv2.TERM_CRITERIA_EPS + self.cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        k = 5  # Number of dominant colors
        _, labels, centers = self.cv2.kmeans(pixels, k, None, criteria, 10, self.cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert centers to RGB values
        centers = np.uint8(centers)
        
        # Calculate percentage of each color
        color_counts = np.bincount(labels.flatten())
        total_pixels = len(pixels)
        
        dominant_colors = []
        for i, (color, count) in enumerate(zip(centers, color_counts)):
            hex_color = f"#{color[2]:02x}{color[1]:02x}{color[0]:02x}"
            percentage = (count / total_pixels) * 100
            
            dominant_colors.append({
                'rgb': (color[2]/255, color[1]/255, color[0]/255),
                'hex': hex_color,
                'percentage': percentage,
                'count': int(count)
            })
        
        # Sort by percentage
        dominant_colors.sort(key=lambda x: x['percentage'], reverse=True)
        
        return dominant_colors
    
    def _extract_color_palette(self, img: np.ndarray) -> List[Tuple[float, float, float]]:
        """Extract a color palette from the image"""
        dominant_colors = self._analyze_colors(img)
        return [tuple(c['rgb']) for c in dominant_colors]
    
    def _calculate_brightness(self, img: np.ndarray) -> float:
        """Calculate average brightness of the image"""
        if len(img.shape) == 3:
            # Convert to grayscale
            gray = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        return float(np.mean(gray)) / 255.0
    
    def _calculate_contrast(self, img: np.ndarray) -> float:
        """Calculate contrast of the image"""
        if len(img.shape) == 3:
            gray = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # Calculate standard deviation of pixel intensities
        return float(np.std(gray)) / 255.0
    
    def _calculate_sharpness(self, img: np.ndarray) -> float:
        """Calculate sharpness using Laplacian variance"""
        if len(img.shape) == 3:
            gray = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # Apply Laplacian filter
        laplacian = self.cv2.Laplacian(gray, self.cv2.CV_64F)
        variance = laplacian.var()
        
        # Normalize to 0-1 range
        max_variance = 1000  # Empirical maximum
        return min(1.0, variance / max_variance)
    
    def _calculate_blur(self, img: np.ndarray) -> float:
        """Calculate blur level using Laplacian variance"""
        # Blur is inverse of sharpness
        sharpness = self._calculate_sharpness(img)
        return 1.0 - sharpness
    
    def _detect_objects(self, img: np.ndarray) -> List[Dict[str, Any]]:
        """Detect objects in the image"""
        objects = []
        
        # Try to use a simple object detection (for demo)
        # In production, would use YOLO, SSD, or other models
        
        # For now, return some mock objects based on color analysis
        dominant_colors = self._analyze_colors(img)
        
        # Simple color-based object detection
        for color in dominant_colors[:3]:
            rgb = color['rgb']
            
            # Classify based on color
            if rgb[0] > 0.8 and rgb[1] > 0.8 and rgb[2] > 0.8:
                label = "White/Light Area"
            elif rgb[0] < 0.2 and rgb[1] < 0.2 and rgb[2] < 0.2:
                label = "Black/Dark Area"
            elif rgb[0] > 0.7 and rgb[1] < 0.3 and rgb[2] < 0.3:
                label = "Red Object"
            elif rgb[0] < 0.3 and rgb[1] > 0.7 and rgb[2] < 0.3:
                label = "Green Object"
            elif rgb[0] < 0.3 and rgb[1] < 0.3 and rgb[2] > 0.7:
                label = "Blue Object"
            else:
                label = "Colored Area"
            
            objects.append({
                'label': label,
                'confidence': color['percentage'] / 100,
                'bounding_box': (0, 0, img.shape[1], img.shape[0]),
                'category': 'color_region'
            })
        
        return objects
    
    def _recognize_scene(self, img: np.ndarray) -> Tuple[str, List[str], float]:
        """Recognize scene in the image"""
        # For demo, use simple brightness and color analysis
        brightness = self._calculate_brightness(img)
        contrast = self._calculate_contrast(img)
        dominant_colors = self._analyze_colors(img)
        
        description = ""
        categories = []
        confidence = 0.0
        
        # Analyze based on brightness
        if brightness > 0.8:
            description = "Bright scene"
            categories.append("bright")
            confidence += 0.3
        elif brightness < 0.3:
            description = "Dark scene"
            categories.append("dark")
            confidence += 0.3
        else:
            description = "Normally lit scene"
            categories.append("normal_light")
            confidence += 0.2
        
        # Analyze based on contrast
        if contrast > 0.3:
            description += ", high contrast"
            categories.append("high_contrast")
            confidence += 0.2
        elif contrast < 0.1:
            description += ", low contrast"
            categories.append("low_contrast")
            confidence += 0.2
        
        # Analyze based on dominant colors
        if dominant_colors:
            primary_color = dominant_colors[0]['rgb']
            if primary_color[0] > 0.6:
                description += ", warm tones"
                categories.append("warm_colors")
            elif primary_color[2] > 0.6:
                description += ", cool tones"
                categories.append("cool_colors")
        
        # Add some common scene categories
        categories.extend(["outdoor", "indoor", "portrait", "landscape"])
        
        return description, categories, min(confidence + 0.3, 1.0)
    
    def detect_text_regions(self, image_path: str, language: str = "eng") -> List[Dict[str, Any]]:
        """
        Detect text regions in an image using OCR.
        
        Args:
            image_path: Path to the image
            language: Language code
            
        Returns:
            List of text regions with bounding boxes
        """
        from .ocr import OCRProcessor
        
        ocr = OCRProcessor()
        result = ocr.process_image(image_path, language)
        
        if result:
            return [
                {
                    'text': region['text'],
                    'confidence': region['confidence'],
                    'bounding_box': region['bounding_box'],
                    'language': result.language
                }
                for region in result.regions
            ]
        return []
    
    def describe_image(self, image_path: str) -> Dict[str, Any]:
        """
        Generate a natural language description of the image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Dictionary with description and metadata
        """
        analysis = self.analyze(image_path)
        
        if not analysis:
            return {'description': '', 'metadata': {}}
        
        # Generate description
        description_parts = []
        
        # Add scene description
        if analysis.scene_description:
            description_parts.append(analysis.scene_description)
        
        # Add color information
        if analysis.dominant_colors:
            primary_color = analysis.dominant_colors[0]
            description_parts.append(f"Primary color: {primary_color['hex']} ({primary_color['percentage']:.0f}%)")
        
        # Add object information
        if analysis.objects:
            object_labels = [obj['label'] for obj in analysis.objects[:3]]
            description_parts.append(f"Contains: {', '.join(object_labels)}")
        
        # Add technical information
        description_parts.append(f"Image size: {analysis.width}x{analysis.height}")
        description_parts.append(f"Brightness: {analysis.brightness:.0%}, Contrast: {analysis.contrast:.0%}")
        
        return {
            'description': ' '.join(description_parts),
            'metadata': {
                'width': analysis.width,
                'height': analysis.height,
                'brightness': analysis.brightness,
                'contrast': analysis.contrast,
                'dominant_colors': [c['hex'] for c in analysis.dominant_colors[:3]]
            }
        }
    
    def extract_colors(self, image_path: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Extract the most dominant colors from an image.
        
        Args:
            image_path: Path to the image
            count: Number of colors to extract
            
        Returns:
            List of color information dictionaries
        """
        img = self._load_image(image_path)
        if img is None:
            return []
        
        dominant_colors = self._analyze_colors(img)
        return dominant_colors[:count]
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        Get basic information about an image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Dictionary with image metadata
        """
        try:
            img = self._load_image(image_path)
            if img is None:
                return {}
            
            height, width = img.shape[:2]
            channels = img.shape[2] if len(img.shape) > 2 else 1
            file_size = Path(image_path).stat().st_size
            
            return {
                'file_path': image_path,
                'file_name': Path(image_path).name,
                'file_size': file_size,
                'width': width,
                'height': height,
                'channels': channels,
                'aspect_ratio': width / height if height > 0 else 0
            }
        except Exception as e:
            print(f"❌ Error getting image info: {e}")
            return {}
