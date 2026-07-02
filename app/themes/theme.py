#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Theme Manager
============================
Main theme management system
"""

from kivy.properties import DictProperty, StringProperty, BooleanProperty, ListProperty
from kivy.utils import get_color_from_hex
from typing import Dict, Any, Optional, Tuple
from enum import Enum

from .colors import TurboMindColors, ColorToken
from .typography import TurboMindTypography, TypographyToken, FontWeight


class ThemeStyle(Enum):
    """Theme style options"""
    DARK = "Dark"
    LIGHT = "Light"
    AMOLED = "AMOLED"


class ThemeManager:
    """
    Main theme manager for TurboMind AI.
    Handles color schemes, typography, and styling.
    
    Brand Personality: Powerful, Secure, Precise, Transparent.
    Aesthetic: "Mission Control" - high-tech telemetry + modern glassmorphism.
    """
    
    # Theme properties
    theme_style = StringProperty(ThemeStyle.DARK.value)
    primary_palette = StringProperty("Blue")
    accent_palette = StringProperty("Cyan")
    
    # Color scheme
    colors = DictProperty({})
    
    # Typography
    typography = DictProperty({})
    
    # Shape
    corner_radius = DictProperty({
        'full': 999,
        'large': 32,
        'medium': 16,
        'small': 8,
        'none': 0
    })
    
    # Shadows
    shadows = DictProperty({})
    
    # Glassmorphism
    glassmorphism = DictProperty({})
    
    def __init__(self, **kwargs):
        """Initialize theme manager"""
        super().__init__(**kwargs)
        self._init_colors()
        self._init_typography()
        self._init_shadows()
        self._init_glassmorphism()
        
        print(f"🎨 Theme Manager initialized ({self.theme_style} mode)")
    
    def _init_colors(self):
        """Initialize color scheme"""
        self.update_colors()
    
    def _init_typography(self):
        """Initialize typography"""
        self.typography = TurboMindTypography.get_kivy_typography()
    
    def _init_shadows(self):
        """Initialize shadows"""
        shadows = TurboMindColors.get_shadows()
        self.shadows = {
            'dark': {
                'small': {'offset': shadows['dark']['small'][:2], 'blur': shadows['dark']['small'][2], 'color': shadows['dark']['small'][3]},
                'medium': {'offset': shadows['dark']['medium'][:2], 'blur': shadows['dark']['medium'][2], 'color': shadows['dark']['medium'][3]},
                'large': {'offset': shadows['dark']['large'][:2], 'blur': shadows['dark']['large'][2], 'color': shadows['dark']['large'][3]},
                'glow': {'offset': shadows['dark']['glow'][:2], 'blur': shadows['dark']['glow'][2], 'color': shadows['dark']['glow'][3]}
            },
            'light': {
                'small': {'offset': shadows['light']['small'][:2], 'blur': shadows['light']['small'][2], 'color': shadows['light']['small'][3]},
                'medium': {'offset': shadows['light']['medium'][:2], 'blur': shadows['light']['medium'][2], 'color': shadows['light']['medium'][3]},
                'large': {'offset': shadows['light']['large'][:2], 'blur': shadows['light']['large'][2], 'color': shadows['light']['large'][3]},
                'glow': {'offset': shadows['light']['glow'][:2], 'blur': shadows['light']['glow'][2], 'color': shadows['light']['glow'][3]}
            }
        }
    
    def _init_glassmorphism(self):
        """Initialize glassmorphism effects"""
        glass = TurboMindColors.get_glassmorphism_colors()
        self.glassmorphism = glass
    
    def update_colors(self):
        """Update color scheme based on theme style"""
        if self.theme_style == ThemeStyle.AMOLED.value:
            self.colors = self._get_amoled_colors()
        elif self.theme_style == ThemeStyle.DARK.value:
            self.colors = self._get_dark_colors()
        else:  # LIGHT
            self.colors = self._get_light_colors()
    
    def _get_amoled_colors(self) -> Dict[str, Any]:
        """Get AMOLED dark mode colors"""
        return {
            # Surface
            'surface': TurboMindColors.SURFACE_AMOLED.to_kivy_color(),
            'surface_variant': TurboMindColors.SURFACE_DEEP_CHARCOAL.to_kivy_color(),
            
            # Primary
            'primary': TurboMindColors.PRIMARY_BRAND_BLUE.to_kivy_color(),
            'primary_dark': TurboMindColors.PRIMARY_DARK.to_kivy_color(),
            'primary_light': TurboMindColors.PRIMARY_LIGHT.to_kivy_color(),
            'primary_container': (*TurboMindColors.PRIMARY_BRAND_BLUE.to_kivy_color()[:3], 0.2),
            'on_primary': (1, 1, 1, 1),
            
            # Secondary
            'secondary': TurboMindColors.SECONDARY_BRAND_CYAN.to_kivy_color(),
            'secondary_dark': TurboMindColors.SECONDARY_DARK.to_kivy_color(),
            'secondary_container': (*TurboMindColors.SECONDARY_BRAND_CYAN.to_kivy_color()[:3], 0.2),
            'on_secondary': (0, 0, 0, 1),
            
            # Tertiary
            'tertiary': TurboMindColors.TERTIARY_SUCCESS.to_kivy_color(),
            'tertiary_container': (*TurboMindColors.TERTIARY_SUCCESS.to_kivy_color()[:3], 0.2),
            'on_tertiary': (0, 0, 0, 1),
            
            # Text
            'text_primary': TurboMindColors.TEXT_HIGH_EMPHASIS.to_kivy_color(),
            'text_secondary': TurboMindColors.TEXT_MEDIUM_EMPHASIS.to_kivy_color(),
            'text_tertiary': TurboMindColors.TEXT_LOW_EMPHASIS.to_kivy_color(),
            'text_on_primary': (1, 1, 1, 1),
            'text_on_secondary': (0, 0, 0, 1),
            
            # Semantic
            'success': TurboMindColors.SUCCESS.to_kivy_color(),
            'warning': TurboMindColors.WARNING.to_kivy_color(),
            'error': TurboMindColors.ERROR.to_kivy_color(),
            'info': TurboMindColors.INFO.to_kivy_color(),
            
            # Container (Glassmorphism)
            'container': TurboMindColors.CONTAINER_DARK_RGBA,
            'container_high': (28/255, 27/255, 27/255, 0.9),
            'container_low': (28/255, 27/255, 27/255, 0.6),
            
            # Border
            'border': (*TurboMindColors.PRIMARY_BRAND_BLUE.to_kivy_color()[:3], 0.2),
            'border_strong': (*TurboMindColors.PRIMARY_BRAND_BLUE.to_kivy_color()[:3], 0.4),
            
            # Gradients
            'gradient_primary': TurboMindColors.get_gradients()['primary'],
            'gradient_success': TurboMindColors.get_gradients()['success'],
        }
    
    def _get_dark_colors(self) -> Dict[str, Any]:
        """Get standard dark mode colors"""
        return self._get_amoled_colors()  # Same as AMOLED for now
    
    def _get_light_colors(self) -> Dict[str, Any]:
        """Get light mode colors"""
        return {
            # Surface
            'surface': TurboMindColors.SURFACE_LIGHT.to_kivy_color(),
            'surface_variant': (240/255, 240/255, 245/255, 1),
            
            # Primary
            'primary': TurboMindColors.PRIMARY_LIGHT_MODE.to_kivy_color(),
            'primary_dark': (0, 70, 130, 1),
            'primary_light': (100, 160, 220, 1),
            'primary_container': (*TurboMindColors.PRIMARY_LIGHT_MODE.to_kivy_color()[:3], 0.1),
            'on_primary': (1, 1, 1, 1),
            
            # Secondary
            'secondary': TurboMindColors.SECONDARY_LIGHT_MODE.to_kivy_color(),
            'secondary_dark': (0, 80, 90, 1),
            'secondary_container': (*TurboMindColors.SECONDARY_LIGHT_MODE.to_kivy_color()[:3], 0.1),
            'on_secondary': (1, 1, 1, 1),
            
            # Tertiary
            'tertiary': TurboMindColors.SUCCESS.to_kivy_color(),
            'tertiary_container': (*TurboMindColors.SUCCESS.to_kivy_color()[:3], 0.1),
            'on_tertiary': (1, 1, 1, 1),
            
            # Text
            'text_primary': TurboMindColors.ON_SURFACE_LIGHT.to_kivy_color(),
            'text_secondary': (*TurboMindColors.ON_SURFACE_LIGHT.to_kivy_color()[:3], 0.7),
            'text_tertiary': (*TurboMindColors.ON_SURFACE_LIGHT.to_kivy_color()[:3], 0.5),
            'text_on_primary': (1, 1, 1, 1),
            'text_on_secondary': (1, 1, 1, 1),
            
            # Semantic
            'success': TurboMindColors.SUCCESS.to_kivy_color(),
            'warning': TurboMindColors.WARNING.to_kivy_color(),
            'error': TurboMindColors.ERROR.to_kivy_color(),
            'info': TurboMindColors.INFO.to_kivy_color(),
            
            # Container
            'container': TurboMindColors.CONTAINER_LIGHT.rgba,
            'container_high': (240/255, 240/255, 245/255, 0.9),
            'container_low': (240/255, 240/255, 245/255, 0.6),
            
            # Border
            'border': (0, 0, 0, 0.1),
            'border_strong': (0, 0, 0, 0.2),
            
            # Gradients
            'gradient_primary': TurboMindColors.get_gradients()['primary'],
            'gradient_success': TurboMindColors.get_gradients()['success'],
        }
    
    def set_theme_style(self, style: str):
        """Set theme style (Dark, Light, AMOLED)"""
        if style in [s.value for s in ThemeStyle]:
            self.theme_style = style
            self.update_colors()
            print(f"🎨 Theme changed to {style}")
    
    def toggle_theme(self):
        """Toggle between Dark and Light themes"""
        if self.theme_style == ThemeStyle.DARK.value:
            self.set_theme_style(ThemeStyle.LIGHT.value)
        else:
            self.set_theme_style(ThemeStyle.DARK.value)
    
    def get_color(self, name: str) -> Tuple[float, float, float, float]:
        """Get color by name"""
        return self.colors.get(name, (0, 0, 0, 1))
    
    def get_typography(self, name: str) -> Dict[str, Any]:
        """Get typography style by name"""
        return self.typography.get(name, {})
    
    def get_shadow(self, name: str, mode: Optional[str] = None) -> Dict[str, Any]:
        """Get shadow by name"""
        mode = mode or self.theme_style.lower()
        return self.shadows.get(mode, {}).get(name, {})
    
    def get_glassmorphism(self, mode: Optional[str] = None) -> Dict[str, Any]:
        """Get glassmorphism settings by mode"""
        mode = mode or self.theme_style.lower()
        return self.glassmorphism.get(mode, {})
    
    def get_corner_radius(self, name: str) -> int:
        """Get corner radius by name"""
        return self.corner_radius.get(name, 0)
    
    def get_hex_color(self, name: str) -> str:
        """Get color as hex string"""
        rgba = self.get_color(name)
        return f"#{int(rgba[0]*255):02x}{int(rgba[1]*255):02x}{int(rgba[2]*255):02x}"
    
    # ==================== COMPONENT STYLES ====================
    
    def get_chat_bubble_style(self, is_user: bool = True) -> Dict[str, Any]:
        """Get chat bubble style"""
        if is_user:
            return {
                'bg_color': self.get_color('primary'),
                'text_color': self.get_color('on_primary'),
                'radius': [self.get_corner_radius('large')] * 4,
                'radius_bottom_right': self.get_corner_radius('small'),
                'halign': 'right'
            }
        else:
            return {
                'bg_color': self.get_color('container'),
                'text_color': self.get_color('text_primary'),
                'radius': [self.get_corner_radius('large')] * 4,
                'radius_bottom_left': self.get_corner_radius('small'),
                'halign': 'left'
            }
    
    def get_card_style(self, variant: str = "default") -> Dict[str, Any]:
        """Get card style"""
        styles = {
            'default': {
                'bg_color': self.get_color('container'),
                'radius': self.get_corner_radius('large'),
                'elevation': 2,
                'border': (0, 0, 0, 0)
            },
            'glass': {
                'bg_color': self.get_color('container_low'),
                'radius': self.get_corner_radius('large'),
                'elevation': 0,
                'border': self.get_color('border')
            },
            'primary': {
                'bg_color': self.get_color('primary_container'),
                'radius': self.get_corner_radius('large'),
                'elevation': 2,
                'border': (0, 0, 0, 0)
            }
        }
        return styles.get(variant, styles['default'])
    
    def get_button_style(self, variant: str = "primary") -> Dict[str, Any]:
        """Get button style"""
        styles = {
            'primary': {
                'bg_color': self.get_color('primary'),
                'text_color': self.get_color('on_primary'),
                'radius': self.get_corner_radius('full')
            },
            'secondary': {
                'bg_color': self.get_color('secondary'),
                'text_color': self.get_color('on_secondary'),
                'radius': self.get_corner_radius('full')
            },
            'text': {
                'bg_color': (0, 0, 0, 0),
                'text_color': self.get_color('primary'),
                'radius': self.get_corner_radius('full')
            },
            'outlined': {
                'bg_color': (0, 0, 0, 0),
                'text_color': self.get_color('primary'),
                'radius': self.get_corner_radius('full'),
                'border': self.get_color('primary')
            }
        }
        return styles.get(variant, styles['primary'])
    
    def get_progress_bar_style(self) -> Dict[str, Any]:
        """Get progress bar style with gradient"""
        return {
            'bg_color': self.get_color('container_low'),
            'progress_color_start': self.get_color('primary'),
            'progress_color_end': self.get_color('secondary'),
            'radius': self.get_corner_radius('full')
        }
    
    def get_telemetry_card_style(self) -> Dict[str, Any]:
        """Get telemetry card style (for RAM/CPU graphs)"""
        return {
            'bg_color': self.get_color('container'),
            'radius': self.get_corner_radius('medium'),
            'elevation': 2,
            'border': self.get_color('border'),
            'graph_line_color': self.get_color('primary'),
            'graph_fill_color': (*self.get_color('primary')[:3], 0.2)
        }


# Global theme manager instance
theme_manager = ThemeManager()
