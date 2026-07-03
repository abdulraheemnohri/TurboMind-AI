#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - OCR Processor
=============================
Optical Character Recognition for images using offline models
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np

# Try to import CV2
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️  OpenCV not installed. Some OCR features may not work.")

# Try to import PIL
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL not installed. Some OCR features may not work.")


@dataclass
class OCRResult:
    """Result of OCR processing"""
    text: str
    confidence: float = 0.0
    language: str = "eng"
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
    Works completely offline once models are downloaded.
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
        self.languages = ['eng', 'urd', 'ara', 'fra', 'spa', 'deu', 'hin']
        
        # Engine-specific components
        self.pytesseract = None
        self.easyocr = None
        self.paddleocr = None
        
        self._init_engine()
        print(f"🔍 OCR Processor initialized ({engine} engine)")
    
    def _init_engine(self) -> bool:
        """Initialize the selected OCR engine"""
        try:
            if self.engine == "tesseract":
                return self._init_tesseract()
            elif self.engine == "easyocr":
                return self._init_easyocr()
            elif self.engine == "paddle":
                return self._init_paddle()
            else:
                print(f"⚠️  Unknown OCR engine: {self.engine}")
                return False
            
        except Exception as e:
            print(f"❌ Error initializing OCR engine: {e}")
            self.initialized = False
            return False
    
    def _init_tesseract(self) -> bool:
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
            
            self.initialized = True
            return True
            
        except ImportError:
            print("⚠️  Tesseract not installed. Install with: pip install pytesseract")
            print("⚠️  Also install Tesseract engine: https://github.com/tesseract-ocr/tesseract")
            print("⚠️  For Urdu: install tesseract-ocr-urd package")
            self.initialized = False
            return False
    
    def _init_easyocr(self) -> bool:
        """Initialize EasyOCR"""
        try:
            import easyocr
            self.easyocr = easyocr
            print("✅ EasyOCR initialized")
            self.initialized = True
            return True
        except ImportError:
            print("⚠️  EasyOCR not installed. Install with: pip install easyocr")
            print("⚠️  Note: EasyOCR will download models on first use (requires internet)")
            self.initialized = False
            return False
    
    def _init_paddle(self) -> bool:
        """Initialize PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            self.paddleocr = PaddleOCR
            print("✅ PaddleOCR initialized")
            self.initialized = True
            return True
        except ImportError:
            print("⚠️  PaddleOCR not installed. Install with: pip install paddleocr")
            print("⚠️  Note: PaddleOCR requires paddlepaddle")
            self.initialized = False
            return False
    
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
        # Load image
        img = self._load_image(image_path)
        if img is None:
            return OCRResult(text="", confidence=0.0, language=language)
        
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
                    'bounding_box': (int(x), int(y), int(w), int(h)),
                    'line_number': i
                })
        
        return OCRResult(
            text=text.strip() if text else "",
            confidence=self._calculate_confidence(data.get('conf', [])),
            language=language,
            regions=regions,
            metadata={
                'engine': 'tesseract',
                'image_size': os.path.getsize(image_path) if os.path.exists(image_path) else 0,
                'page_number': kwargs.get('page', 1),
                'image_width': img.shape[1] if len(img.shape) > 1 else 0,
                'image_height': img.shape[0] if len(img.shape) > 0 else 0
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
            'deu': 'de',
            'hin': 'hi'
        }
        
        lang = lang_map.get(language, 'en')
        
        # Create reader
        reader = self.easyocr.Reader([lang])
        
        # Load image
        img = self._load_image(image_path)
        if img is None:
            return OCRResult(text="", confidence=0.0, language=language)
        
        # Run OCR
        results = reader.readtext(img, **kwargs)
        
        text = '
'.join([r[1] for r in results])
        confidence = sum([float(r[2]) for r in results]) / len(results) if results else 0.0
        
        regions = [
            {
                'text': r[1],
                'confidence': float(r[2]),
                'bounding_box': tuple(map(int, r[0]))
            }
            for r in results
        ]
        
        img_size = os.path.getsize(image_path) if os.path.exists(image_path) else 0
        
        return OCRResult(
            text=text,
            confidence=confidence,
            language=language,
            regions=regions,
            metadata={
                'engine': 'easyocr',
                'image_size': img_size,
                'language_used': lang
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
            'deu': 'de',
            'hin': 'hi'
        }
        
        lang = lang_map.get(language, 'en')
        
        # Create OCR instance
        ocr = self.paddleocr(use_angle_cls=True, lang=lang)
        
        # Load image
        img = self._load_image(image_path)
        if img is None:
            return OCRResult(text="", confidence=0.0, language=language)
        
        # Run OCR
        result = ocr.ocr(img, cls=True)
        
        text = ''
        regions = []
        confidence_total = 0
        count = 0
        
        for idx, detection in enumerate(result):
            if isinstance(detection, list):
                for line in detection:
                    if isinstance(line, list) and len(line) >= 2:
                        text_line = line[1][0] if isinstance(line[1], list) else str(line[1])
                        conf = float(line[1][1]) if isinstance(line[1], list) and len(line[1]) > 1 else 0.0
                        
                        text += text_line + '
'
                        confidence_total += conf
                        count += 1
                        
                        bbox = line[0] if isinstance(line[0], list) else [0, 0, 0, 0]
                        regions.append({
                            'text': text_line,
                            'confidence': conf,
                            'bounding_box': tuple(map(int, bbox))
                        })
        
        confidence = confidence_total / count if count > 0 else 0.0
        img_size = os.path.getsize(image_path) if os.path.exists(image_path) else 0
        
        return OCRResult(
            text=text.strip(),
            confidence=confidence,
            language=language,
            regions=regions,
            metadata={
                'engine': 'paddle',
                'image_size': img_size,
                'language_used': lang
            }
        )
    
    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load an image from file"""
        try:
            if CV2_AVAILABLE:
                img = cv2.imread(image_path)
                if img is not None:
                    return img
            
            if PIL_AVAILABLE:
                img = Image.open(image_path)
                return np.array(img)
            
            print(f"❌ Cannot load image: {image_path} (no CV2 or PIL)")
            return None
            
        except Exception as e:
            print(f"❌ Error loading image: {e}")
            return None
    
    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        if not CV2_AVAILABLE:
            return img
        
        # Convert to grayscale if needed
        if len(img.shape) == 3 and img.shape[2] == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif len(img.shape) == 3 and img.shape[2] == 4:
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        else:
            gray = img
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Apply morphological operations to remove noise
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        return processed
    
    def _calculate_confidence(self, confidences: List) -> float:
        """Calculate average confidence from confidence values"""
        if not confidences:
            return 0.0
        
        valid_confs = []
        for c in confidences:
            if c is not None:
                try:
                    valid_confs.append(float(c))
                except:
                    pass
        
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
        results = []
        
        try:
            # Try to use pdf2image
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(pdf_path, **kwargs)
                
                for i, image in enumerate(images):
                    # Save temp image
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                        temp_path = temp_file.name
                    
                    try:
                        image.save(temp_path, 'PNG')
                        
                        # Process image
                        result = self.process_image(temp_path, language, page=i+1)
                        if result:
                            results.append(result)
                    finally:
                        # Clean up
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                        
            except ImportError:
                # Try with PyMuPDF (fitz)
                try:
                    import fitz
                    doc = fitz.open(pdf_path)
                    
                    for i, page in enumerate(doc):
                        # Render page as image
                        pix = page.get_pixmap()
                        temp_path = f"{pdf_path}_page_{i}_temp.png"
                        pix.save(temp_path)
                        
                        try:
                            result = self.process_image(temp_path, language, page=i+1)
                            if result:
                                results.append(result)
                        finally:
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
                                
                except ImportError:
                    print("⚠️  Neither pdf2image nor PyMuPDF installed for PDF processing")
                    print("⚠️  Install with: pip install pdf2image or pip install pymupdf")
                    
        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
        
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
    
    def extract_text_from_regions(self, image_path: str, regions: List[Tuple], language: str = "eng") -> List[OCRResult]:
        """
        Extract text from specific regions of an image.
        
        Args:
            image_path: Path to the image
            regions: List of (x, y, width, height) tuples
            language: Language code
            
        Returns:
            List of OCRResult for each region
        """
        results = []
        
        img = self._load_image(image_path)
        if img is None:
            return results
        
        for i, (x, y, w, h) in enumerate(regions):
            # Crop region
            if CV2_AVAILABLE:
                region_img = img[y:y+h, x:x+w]
            else:
                # Simple slicing (may not work for all image types)
                region_img = img[y:y+h, x:x+w] if len(img.shape) == 2 else img[y:y+h, x:x+w, :]
            
            # Save temp image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                if CV2_AVAILABLE:
                    cv2.imwrite(temp_path, region_img)
                elif PIL_AVAILABLE:
                    Image.fromarray(region_img).save(temp_path)
                else:
                    continue
                
                result = self.process_image(temp_path, language)
                if result:
                    result.metadata['region_index'] = i
                    results.append(result)
            finally:
                try:
                    os.unlink(temp_path)
                except:
                    pass
        
        return results
    
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
            'deu': 'German',
            'hin': 'Hindi'
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
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check which OCR dependencies are available"""
        deps = {
            'pytesseract': False,
            'easyocr': False,
            'paddleocr': False,
            'opencv': CV2_AVAILABLE,
            'pil': PIL_AVAILABLE
        }
        
        try:
            import pytesseract
            deps['pytesseract'] = True
        except:
            pass
        
        try:
            import easyocr
            deps['easyocr'] = True
        except:
            pass
        
        try:
            from paddleocr import PaddleOCR
            deps['paddleocr'] = True
        except:
            pass
        
        return deps
