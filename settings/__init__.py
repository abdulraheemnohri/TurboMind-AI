# TurboMind AI - Settings Package
# =================================

"""
Settings Package for TurboMind AI.
Handles application settings, preferences, and configurations.

Features:
- Application Settings
- Privacy Controls
- Theme Configuration
- Language Preferences
- Model Settings
- Storage Management
"""

from .app_settings import AppSettings
from .privacy_settings import PrivacySettings
from .theme_settings import ThemeSettings
from .model_settings import ModelSettings

__all__ = [
    'AppSettings',
    'PrivacySettings',
    'ThemeSettings',
    'ModelSettings'
]
__version__ = '1.0.0'