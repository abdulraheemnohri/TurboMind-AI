#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - OCR Processor
=============================
Optical Character Recognition for images
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np


@dataclass
class OCRResult:
    """Result of OCR processing"""
    text: str
    confidence: float = 0.0
    language: str = "en"
    regions: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OCRRegion:
    """A region of text in an image"""
    text: str
    bounding_box: Tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float = 0.0
    line_number: int = 0
    word_number: int = 0


class OCRProcessor:
    """
    Processes images to extract text using OCR.
    Supports multiple OCR engines (Tesseract, EasyOCR, PaddleOCR).
    """
    
    def __init__(self, engine: str = "tesseract"):
        """
        Initialize the OCR processor.
        
        Args:
            engine: OCR engine to use ('tesseract', 'easyocr', 'paddle')
        """
        self.engine = engine
        self.available_engines = ['tesseract', 'easyocr', 'paddle']
        self.initialized = False
        self.languages = ['eng', 'urd', 'ara', 'fra', 'spa', 'deu']
        
        self._init_engine()
        print(f"🔍 OCR Processor initialized ({engine} engine)")
    
    def _init_engine(self) -> bool:
        """Initialize the selected OCR engine"""
        try:
            if self.engine == "tesseract":
                self._init_tesseract()
            elif self.engine == "easyocr":
                self._init_easyocr()
            elif self.engine == "paddle":
                self._init_paddle()
            else:
                print(f"⚠️  Unknown OCR engine: {self.engine}")
                return False
            
            self.initialized = True
            return True
        except Exception as e:
            print(f"❌ Error initializing OCR engine: {e}")
            self.initialized = False
            return False
    
    def _init_tesseract(self):
        """Initialize Tesseract OCR"""
        try:
            import pytesseract
            self.pytesseract = pytesseract
            
            # Try to get Tesseract version
            try:
                version = pytesseract.get_tesseract_version()
                print(f"✅ Tesseract OCR initialized (v{version})")
            except:
                print("✅ Tesseract OCR initialized")
            
        except ImportError:
            print("⚠️  Tesseract not installed. Install with: pip install pytesseract")
            raise
    
    def _init_easyocr(self):
        """Initialize EasyOCR"""
        try:
            import easyocr
            self.easyocr = easyocr
            print("✅ EasyOCR initialized")
        except ImportError:
            print("⚠️  EasyOCR not installed. Install with: pip install easyocr")
            raise
    
    def _init_paddle(self):
        """Initialize PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            self.paddleocr = PaddleOCR
            print("✅ PaddleOCR initialized")
        except ImportError:
            print("⚠️  PaddleOCR not installed. Install with: pip install paddleocr")
            raise
    
    def process_image(self, image_path: str, language: str = "eng", **kwargs) -> Optional[OCRResult]:
        """
        Process an image file with OCR.
        
        Args:
            image_path: Path to the image file
            language: Language code (default: 'eng')
            **kwargs: Additional OCR options
            
        Returns:
            OCRResult with extracted text and metadata
        """
        if not self.initialized:
            print("❌ OCR engine not initialized")
            return None
        
        try:
            if self.engine == "tesseract":
                return self._process_with_tesseract(image_path, language, **kwargs)
            elif self.engine == "easyocr":
                return self._process_with_easyocr(image_path, language, **kwargs)
            elif self.engine == "paddle":
                return self._process_with_paddle(image_path, language, **kwargs)
        except Exception as e:
            print(f"❌ Error processing image: {e}")
            return None
    
    def _process_with_tesseract(self, image_path: str, language: str, **kwargs) -> OCRResult:
        """Process image with Tesseract"""
        import cv2
        from PIL import Image
        
        # Load image
        try:
            # Try with OpenCV
            img = cv2.imread(image_path)
            if img is None:
                # Try with PIL
                img = Image.open(image_path)
                img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except:
            # Try with PIL only
            img = Image.open(image_path)
            img = np.array(img)
        
        # Preprocess image
        img = self._preprocess_image(img)
        
        # Run OCR
        text = self.pytesseract.image_to_string(
            img,
            lang=language,
            config='--psm 6'  # Assume a single uniform block of text
        )
        
        # Get detailed data
        data = self.pytesseract.image_to_data(
            img,
            lang=language,
            output_type=self.pytesseract.Output.DICT
        )
        
        # Process regions
        regions = []
        for i, (text, conf, x, y, w, h) in enumerate(zip(
            data.get('text', []),
            data.get('conf', []),
            data.get('left', []),
            data.get('top', []),
            data.get('width', []),
            data.get('height', [])
        )):
            if text and text.strip():
                regions.append({
                    'text': text.strip(),
                    'confidence': float(conf) if conf else 0.0,
                    'bounding_box': (x, y, w, h),
                    'line_number': i
                })
        
        return OCRResult(
            text=text.strip(),
            confidence=self._calculate_confidence(data.get('conf', [])),
            language=language,
            regions=regions,
            metadata={
                'engine': 'tesseract',
                'image_size': os.path.getsize(image_path),
                'page_number': kwargs.get('page', 1)
            }
        )
    
    def _process_with_easyocr(self, image_path: str, language: str, **kwargs) -> OCRResult:
        """Process image with EasyOCR"""
        # Map language codes
        lang_map = {
            'eng': 'en',
            'urd': 'ur',
            'ara': 'ar',
            'fra': 'fr',
            'spa': 'es',
            'deu': 'de'
        }
        
        reader = self.easyocr.Reader([lang_map.get(language, 'en')])
        results = reader.readtext(image_path, **kwargs)
        
        text = '\n'.join([r[1] for r in results])
        confidence = sum([float(r[2]) for r in results]) / len(results) if results else 0.0
        
        regions = [
            {
                'text': r[1],
                'confidence': float(r[2]),
                'bounding_box': tuple(map(int, r[0]))
            }
            for r in results
        ]
        
        return OCRResult(
            text=text,
            confidence=confidence,
            language=language,
            regions=regions,
            metadata={
                'engine': 'easyocr',
                'image_size': os.path.getsize(image_path)
            }
        )
    
    def _process_with_paddle(self, image_path: str, language: str, **kwargs) -> OCRResult:
        """Process image with PaddleOCR"""
        # Map language codes
        lang_map = {
            'eng': 'en',
            'urd': 'ur',
            'ara': 'ar',
            'fra': 'fr',
            'spa': 'es',
            'deu': 'de'
        }
        
        ocr = self.paddleocr(use_angle_cls=True, lang=lang_map.get(language, 'en'))
        result = ocr.ocr(image_path, cls=True)
        
        text = ''
        regions = []
        confidence_total = 0
        count = 0
        
        for idx, detection in enumerate(result):
            for line in detection:
                if isinstance(line, list) and len(line) >= 2:
                    text_line = line[1][0] if isinstance(line[1], list) else str(line[1])
                    conf = float(line[1][1]) if isinstance(line[1], list) and len(line[1]) > 1 else 0.0
                    
                    text += text_line + '\n'
                    confidence_total += conf
                    count += 1
                    
                    regions.append({
                        'text': text_line,
                        'confidence': conf,
                        'bounding_box': tuple(map(int, line[0])) if isinstance(line[0], list) else (0, 0, 0, 0)
                    })
        
        confidence = confidence_total / count if count > 0 else 0.0
        
        return OCRResult(
            text=text.strip(),
            confidence=confidence,
            language=language,
            regions=regions,
            metadata={
                'engine': 'paddle',
                'image_size': os.path.getsize(image_path)
            }
        )
    
    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        import cv2
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply dilation and erosion to remove noise
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        return processed
    
    def _calculate_confidence(self, confidences: List) -> float:
        """Calculate average confidence from confidence values"""
        if not confidences:
            return 0.0
        
        valid_confs = [float(c) for c in confidences if c is not None and c > 0]
        return sum(valid_confs) / len(valid_confs) if valid_confs else 0.0
    
    def process_pdf(self, pdf_path: str, language: str = "eng", **kwargs) -> List[OCRResult]:
        """
        Process all pages of a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            language: Language code
            **kwargs: Additional options
            
        Returns:
            List of OCRResult for each page
        """
        from pdf2image import convert_from_path
        
        results = []
        
        # Convert PDF to images
        images = convert_from_path(pdf_path, **kwargs)
        
        for i, image in enumerate(images):
            # Save temp image
            temp_path = f"{pdf_path}_page_{i}.png"
            image.save(temp_path, 'PNG')
            
            # Process image
            result = self.process_image(temp_path, language)
            if result:
                result.metadata['page_number'] = i + 1
                results.append(result)
            
            # Clean up
            try:
                os.remove(temp_path)
            except:
                pass
        
        return results
    
    def process_screenshot(self, image_path: str, language: str = "eng") -> OCRResult:
        """
        Process a screenshot with optimized settings.
        
        Args:
            image_path: Path to the screenshot
            language: Language code
            
        Returns:
            OCRResult with extracted text
        """
        return self.process_image(
            image_path,
            language,
            config='--psm 6 --oem 3'
        )
    
    def process_document(self, image_path: str, language: str = "eng") -> OCRResult:
        """
        Process a document image with optimized settings.
        
        Args:
            image_path: Path to the document image
            language: Language code
            
        Returns:
            OCRResult with extracted text
        """
        return self.process_image(
            image_path,
            language,
            config='--psm 6 --oem 3'
        )
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.languages.copy()
    
    def get_language_name(self, code: str) -> str:
        """Get language name from code"""
        names = {
            'eng': 'English',
            'urd': 'Urdu',
            'ara': 'Arabic',
            'fra': 'French',
            'spa': 'Spanish',
            'deu': 'German'
        }
        return names.get(code, code)
    
    def set_engine(self, engine: str) -> bool:
        """Set the OCR engine"""
        if engine.lower() in self.available_engines:
            self.engine = engine.lower()
            return self._init_engine()
        return False
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about the current OCR engine"""
        return {
            'engine': self.engine,
            'initialized': self.initialized,
            'available_engines': self.available_engines,
            'languages': self.languages
        }
