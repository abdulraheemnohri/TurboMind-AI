# TurboMind AI - Screens Package
# =================================

"""
Screens package for TurboMind AI application.
Contains all screen classes for the app.
"""

from .home import HomeScreen
from .chat import ChatScreen
from .documents import DocumentsScreen
from .vision import VisionScreen
from .knowledge import KnowledgeScreen
from .models import ModelsScreen
from .voice import VoiceScreen
from .settings import SettingsScreen
from .search import SearchScreen

__all__ = [
    'HomeScreen',
    'ChatScreen', 
    'DocumentsScreen',
    'VisionScreen',
    'KnowledgeScreen',
    'ModelsScreen',
    'VoiceScreen',
    'SettingsScreen',
    'SearchScreen'
]
__version__ = '1.0.0'
