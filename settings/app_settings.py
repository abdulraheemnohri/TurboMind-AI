#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Application Settings
===================================
Manages general application settings and preferences
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json
import os


@dataclass
class SettingsConfig:
    app_name: str = "TurboMind AI"
    app_version: str = "1.0.0"
    first_launch: bool = True
    language: str = "en"
    preferred_languages: List[str] = field(default_factory=lambda: ["en", "ur", "hi"])
    theme_style: str = "Dark"
    primary_color: str = "Blue"
    accent_color: str = "Cyan"
    max_context_length: int = 4096
    max_tokens: int = 256
    temperature: float = 0.7
    auto_cleanup: bool = True
    max_storage_gb: int = 16
    auto_check_updates: bool = True
    beta_features: bool = False
    debug_mode: bool = False
    show_fps: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'app_name': self.app_name,
            'app_version': self.app_version,
            'first_launch': self.first_launch,
            'language': self.language,
            'preferred_languages': self.preferred_languages,
            'theme_style': self.theme_style,
            'primary_color': self.primary_color,
            'accent_color': self.accent_color,
            'max_context_length': self.max_context_length,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'auto_cleanup': self.auto_cleanup,
            'max_storage_gb': self.max_storage_gb,
            'auto_check_updates': self.auto_check_updates,
            'beta_features': self.beta_features,
            'debug_mode': self.debug_mode,
            'show_fps': self.show_fps
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SettingsConfig':
        return cls(
            app_name=data.get('app_name', 'TurboMind AI'),
            app_version=data.get('app_version', '1.0.0'),
            first_launch=data.get('first_launch', True),
            language=data.get('language', 'en'),
            preferred_languages=data.get('preferred_languages', ['en', 'ur', 'hi']),
            theme_style=data.get('theme_style', 'Dark'),
            primary_color=data.get('primary_color', 'Blue'),
            accent_color=data.get('accent_color', 'Cyan'),
            max_context_length=data.get('max_context_length', 4096),
            max_tokens=data.get('max_tokens', 256),
            temperature=data.get('temperature', 0.7),
            auto_cleanup=data.get('auto_cleanup', True),
            max_storage_gb=data.get('max_storage_gb', 16),
            auto_check_updates=data.get('auto_check_updates', True),
            beta_features=data.get('beta_features', False),
            debug_mode=data.get('debug_mode', False),
            show_fps=data.get('show_fps', False)
        )


class AppSettings:
    DEFAULT_SETTINGS = {
        'app_name': 'TurboMind AI',
        'app_version': '1.0.0',
        'first_launch': True,
        'language': 'en',
        'preferred_languages': ['en', 'ur', 'hi'],
        'theme_style': 'Dark',
        'primary_color': 'Blue',
        'accent_color': 'Cyan',
        'max_context_length': 4096,
        'max_tokens': 256,
        'temperature': 0.7
    }
    
    SUPPORTED_LANGUAGES = {
        'en': 'English', 'ur': 'Urdu', 'hi': 'Hindi', 'es': 'Spanish',
        'fr': 'French', 'de': 'German', 'it': 'Italian', 'pt': 'Portuguese',
        'ru': 'Russian', 'zh': 'Chinese', 'ja': 'Japanese', 'ar': 'Arabic'
    }
    
    THEME_COLORS = {
        'Red': 'Red', 'Pink': 'Pink', 'Purple': 'Purple', 'DeepPurple': 'Deep Purple',
        'Indigo': 'Indigo', 'Blue': 'Blue', 'LightBlue': 'Light Blue', 'Cyan': 'Cyan',
        'Teal': 'Teal', 'Green': 'Green', 'LightGreen': 'Light Green', 'Lime': 'Lime',
        'Yellow': 'Yellow', 'Amber': 'Amber', 'Orange': 'Orange', 'DeepOrange': 'Deep Orange',
        'Brown': 'Brown', 'Gray': 'Gray', 'BlueGray': 'Blue Gray'
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("config/settings.json")
        self.config = SettingsConfig()
        self._load_settings()
        print(" Application Settings initialized")
    
    def _load_settings(self) -> bool:
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.config = SettingsConfig.from_dict(data)
                return True
            else:
                self._save_settings()
                return True
        except Exception as e:
            print(f" Error loading settings: {e}")
            self.config = SettingsConfig()
            return False
    
    def _save_settings(self) -> bool:
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=4)
            return True
        except Exception as e:
            print(f" Error saving settings: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        return getattr(self.config, key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        try:
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                self._save_settings()
                return True
            return False
        except Exception as e:
            print(f" Error updating setting: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        return self.config.to_dict()
    
    def reset_to_defaults(self) -> bool:
        try:
            self.config = SettingsConfig()
            self._save_settings()
            return True
        except Exception as e:
            print(f" Error resetting settings: {e}")
            return False
    
    def set_language(self, language_code: str) -> bool:
        if language_code in self.SUPPORTED_LANGUAGES:
            self.config.language = language_code
            self._save_settings()
            return True
        return False
    
    def get_supported_languages(self) -> Dict[str, str]:
        return self.SUPPORTED_LANGUAGES.copy()
    
    def set_theme(self, theme_style: str, primary_color: str, accent_color: str) -> bool:
        valid_styles = ['Dark', 'Light']
        if theme_style not in valid_styles:
            return False
        if primary_color not in self.THEME_COLORS:
            return False
        if accent_color not in self.THEME_COLORS:
            return False
        self.config.theme_style = theme_style
        self.config.primary_color = primary_color
        self.config.accent_color = accent_color
        self._save_settings()
        return True
    
    def get_theme_colors(self) -> Dict[str, str]:
        return self.THEME_COLORS.copy()
    
    def mark_first_launch_complete(self) -> bool:
        try:
            self.config.first_launch = False
            self._save_settings()
            return True
        except Exception as e:
            print(f" Error marking first launch: {e}")
            return False
    
    def is_first_launch(self) -> bool:
        return self.config.first_launch