# TurboMind AI - Screens Package
# =================================

"""
Screens package for TurboMind AI application.
Contains all screen classes for the app.
"""

from .chat import ChatScreen
from .documents import DocumentsScreen
from .vision import VisionScreen
from .knowledge import KnowledgeScreen

__all__ = ['ChatScreen', 'DocumentsScreen', 'VisionScreen', 'KnowledgeScreen']
__version__ = '1.0.0'