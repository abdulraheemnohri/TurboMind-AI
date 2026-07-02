# TurboMind AI - Documents Package
# =================================

"""
Documents Package for TurboMind AI.
Handles document processing, analysis, and management.

Supported Formats:
- PDF
- DOCX
- TXT
- Markdown
- HTML
- CSV
- Excel
- PowerPoint

Features:
- Summarization
- Translation
- Question Answering
- Keyword Search
- Semantic Search
- Outline Generation
- Flashcards
- Notes
- Citation Extraction
"""

from .document_processor import DocumentProcessor
from .summarizer import Summarizer
from .translator import Translator
from .search_engine import DocumentSearchEngine
from .outliner import Outliner

__all__ = [
    'DocumentProcessor',
    'Summarizer',
    'Translator',
    'DocumentSearchEngine',
    'Outliner'
]
__version__ = '1.0.0'
