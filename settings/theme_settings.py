#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Theme Settings
==============================
Manages theme and appearance settings
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import json


@dataclass
class ThemeConfig:
    theme_style: str = "Dark"
    primary_palette: str = "Blue"
    primary_hue: str = "500"
    accent_palette: str = "Cyan"
    accent_hue: str = "500"
    font_family: str = "PlusJakartaSans"
    font_size: float = 1.0
    corner_radius: int = 16
    elevation: int = 2
    card_radius: int = 16
    list_radius: int = 8
    surface_color: Tuple[float, float, float, float] = (0.1, 0.1, 0.1, 0.6)
    card_color: Tuple[float, float, float, float] = (0.15, 0.15, 0.15, 0.4)
    text_color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    secondary_text_color: Tuple[float, float, float, float] = (0.7, 0.7, 0.7, 1.0)
    shadow_color: Tuple[float, float, float, float] = (0.21, 0.58, 0.94, 0.15)
    shadow_elevation: int = 2
    animations_enabled: bool = True
    animation_speed: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'theme_style': self.theme_style,
            'primary_palette': self.primary_palette,
            'primary_hue': self.primary_hue,
            'accent_palette': self.accent_palette,
            'accent_hue': self.accent_hue,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'corner_radius': self.corner_radius,
            'elevation': self.elevation,
            'card_radius': self.card_radius,
            'list_radius': self.list_radius,
            'surface_color': list(self.surface_color),
            'card_color': list(self.card_color),
            'text_color': list(self.text_color),
            'secondary_text_color': list(self.secondary_text_color),
            'shadow_color': list(self.shadow_color),
            'shadow_elevation': self.shadow_elevation,
            'animations_enabled': self.animations_enabled,
            'animation_speed': self.animation_speed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemeConfig':
        return cls(
            theme_style=data.get('theme_style', 'Dark'),
            primary_palette=data.get('primary_palette', 'Blue'),
            primary_hue=data.get('primary_hue', '500'),
            accent_palette=data.get('accent_palette', 'Cyan'),
            accent_hue=data.get('accent_hue', '500'),
            font_family=data.get('font_family', 'PlusJakartaSans'),
            font_size=data.get('font_size', 1.0),
            corner_radius=data.get('corner_radius', 16),
            elevation=data.get('elevation', 2),
            card_radius=data.get('card_radius', 16),
            list_radius=data.get('list_radius', 8),
            surface_color=tuple(data.get('surface_color', (0.1, 0.1, 0.1, 0.6))),
            card_color=tuple(data.get('card_color', (0.15, 0.15, 0.15, 0.4))),
            text_color=tuple(data.get('text_color', (1.0, 1.0, 1.0, 1.0))),
            secondary_text_color=tuple(data.get('secondary_text_color', (0.7, 0.7, 0.7, 1.0))),
            shadow_color=tuple(data.get('shadow_color', (0.21, 0.58, 0.94, 0.15))),
            shadow_elevation=data.get('shadow_elevation', 2),
            animations_enabled=data.get('animations_enabled', True),
            animation_speed=data.get('animation_speed', 1.0)
        )


class ThemeSettings:
    COLOR_PALETTES = {
        'Red': ['FFCDD2', 'E57373', 'EF5350', 'F44336'],
        'Pink': ['F8BBD9', 'F06292', 'E91E63', 'EC407A'],
        'Purple': ['E1BEE7', 'CE93D8', '9C27B0', 'AA47BC'],
        'DeepPurple': ['D1C4E9', 'B39DDB', '7E57C2', '65499C'],
        'Indigo': ['C5CAE9', '9FA8DA', '5C6BC0', '5677FC'],
        'Blue': ['BBDEFB', '90CAF9', '42A5F5', '2196F3'],
        'LightBlue': ['B3E5FC', '81D4FA', '29B6F6', '03A9F4'],
        'Cyan': ['B2EBF2', '80DEEA', '00BCD4', '00ACC1'],
        'Teal': ['B2DFDB', '80CBC4', '26A69A', '009688'],
        'Green': ['C8E6C9', 'A5D6A7', '66BB6A', '4CAF50'],
        'LightGreen': ['DCEDC8', 'C5E1A5', '9CCC65', '8BC34A'],
        'Lime': ['F0F4C3', 'E6EE9C', 'CDDC39', 'C0CA33'],
        'Yellow': ['FFF9C4', 'FFF59D', 'FFEE58', 'FFD600'],
        'Amber': ['FFECB3', 'FFE082', 'FFD54F', 'FFCA28'],
        'Orange': ['FFE0B2', 'FFCC80', 'FFB74D', 'FFAB40'],
        'DeepOrange': ['FFCCBC', 'FFAB91', 'FF7043', 'FF8A65'],
        'Brown': ['D7CCC8', 'BCAAA4', '8D6E63', '795548'],
        'Gray': ['F5F5F5', 'FAFAFA', 'E0E0E0', 'BDBDBD'],
        'BlueGray': ['ECEFF1', 'CFD8DC', '78909C', '607D8B']
    }
    
    THEME_STYLES = ['Dark', 'Light']
    
    FONT_FAMILIES = {
        'PlusJakartaSans': 'Plus Jakarta Sans', 'Roboto': 'Roboto',
        'OpenSans': 'Open Sans', 'Poppins': 'Poppins', 'Inter': 'Inter'
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("config/theme.json")
        self.config = ThemeConfig()
        self._load_settings()
        print(" Theme Settings initialized")
    
    def _load_settings(self) -> bool:
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.config = ThemeConfig.from_dict(data)
                return True
            else:
                self._save_settings()
                return True
        except Exception as e:
            print(f" Error loading theme: {e}")
            self.config = ThemeConfig()
            return False
    
    def _save_settings(self) -> bool:
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=4)
            return True
        except Exception as e:
            print(f" Error saving theme: {e}")
            return False
    
    def set_theme_style(self, style: str) -> bool:
        if style in self.THEME_STYLES:
            self.config.theme_style = style
            self._save_settings()
            return True
        return False
    
    def set_primary_color(self, palette: str, hue: str = "500") -> bool:
        if palette in self.COLOR_PALETTES:
            self.config.primary_palette = palette
            self.config.primary_hue = hue
            self._save_settings()
            return True
        return False
    
    def set_accent_color(self, palette: str, hue: str = "500") -> bool:
        if palette in self.COLOR_PALETTES:
            self.config.accent_palette = palette
            self.config.accent_hue = hue
            self._save_settings()
            return True
        return False
    
    def set_font_family(self, font_family: str) -> bool:
        if font_family in self.FONT_FAMILIES:
            self.config.font_family = font_family
            self._save_settings()
            return True
        return False
    
    def get_theme_config(self) -> ThemeConfig:
        return self.config
    
    def get_available_palettes(self) -> Dict[str, List[str]]:
        return self.COLOR_PALETTES.copy()
    
    def get_available_fonts(self) -> Dict[str, str]:
        return self.FONT_FAMILIES.copy()
    
    def apply_theme(self, app_instance=None):
        if app_instance:
            app_instance.theme_cls.theme_style = self.config.theme_style
            app_instance.theme_cls.primary_palette = self.config.primary_palette
            app_instance.theme_cls.accent_palette = self.config.accent_palette
    
    def reset_to_defaults(self) -> bool:
        try:
            self.config = ThemeConfig()
            self._save_settings()
            return True
        except Exception as e:
            print(f" Error resetting theme: {e}")
            return False
    
    def get_theme_summary(self) -> Dict[str, Any]:
        return {
            'theme_style': self.config.theme_style,
            'primary_palette': self.config.primary_palette,
            'accent_palette': self.config.accent_palette,
            'font_family': self.config.font_family,
            'animations_enabled': self.config.animations_enabled
        }