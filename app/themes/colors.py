#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Color Palette
============================
Color tokens based on design documentation.
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Any
import colorsys


@dataclass
class ColorToken:
    """Represents a color token"""
    name: str
    hex_value: str
    rgba: Tuple[float, float, float, float] = field(default_factory=lambda: (0, 0, 0, 1))
    usage: str = ""
    
    def __post_init__(self):
        if not self.rgba or self.rgba == (0, 0, 0, 1):
            self.rgba = self._hex_to_rgba(self.hex_value)
    
    @staticmethod
    def _hex_to_rgba(hex_value: str) -> Tuple[float, float, float, float]:
        """Convert hex color to RGBA tuple (0-1 range)"""
        hex_value = hex_value.lstrip('#')
        
        if len(hex_value) == 6:
            r = int(hex_value[0:2], 16) / 255.0
            g = int(hex_value[2:4], 16) / 255.0
            b = int(hex_value[4:6], 16) / 255.0
            return (r, g, b, 1.0)
        elif len(hex_value) == 8:
            r = int(hex_value[0:2], 16) / 255.0
            g = int(hex_value[2:4], 16) / 255.0
            b = int(hex_value[4:6], 16) / 255.0
            a = int(hex_value[6:8], 16) / 255.0
            return (r, g, b, a)
        else:
            return (0, 0, 0, 1)
    
    def to_kivy_color(self) -> Tuple[float, float, float, float]:
        """Return color as Kivy-compatible RGBA tuple"""
        return self.rgba
    
    def to_hex(self) -> str:
        """Return hex value"""
        return self.hex_value
    
    def with_alpha(self, alpha: float) -> Tuple[float, float, float, float]:
        """Return color with specified alpha"""
        return (self.rgba[0], self.rgba[1], self.rgba[2], alpha)


class TurboMindColors:
    """
    Color palette for TurboMind AI based on design documentation.
    
    Brand Personality: Powerful, Secure, Precise, Transparent.
    Aesthetic: "Mission Control" - high-tech telemetry + modern glassmorphism.
    """
    
    # ==================== DARK MODE (AMOLED) ====================
    
    # Surface Colors
    SURFACE_AMOLED = ColorToken(
        name="Surface (AMOLED)",
        hex_value="#000000",
        usage="Primary background - Pure Black for AMOLED"
    )
    
    SURFACE_DEEP_CHARCOAL = ColorToken(
        name="Surface (Deep Charcoal)",
        hex_value="#131313",
        usage="Alternative dark background"
    )
    
    # Primary Colors
    PRIMARY_BRAND_BLUE = ColorToken(
        name="Primary (Brand Blue)",
        hex_value="#2196F3",
        usage="Primary brand color - buttons, highlights"
    )
    
    PRIMARY_DARK = ColorToken(
        name="Primary Dark",
        hex_value="#1976D2",
        usage="Darker variant of primary"
    )
    
    PRIMARY_LIGHT = ColorToken(
        name="Primary Light",
        hex_value="#7986CB",
        usage="Lighter variant of primary"
    )
    
    # Secondary Colors
    SECONDARY_BRAND_CYAN = ColorToken(
        name="Secondary (Brand Cyan)",
        hex_value="#00BCD4",
        usage="Secondary brand color - accents, highlights"
    )
    
    SECONDARY_DARK = ColorToken(
        name="Secondary Dark",
        hex_value="#0097A7",
        usage="Darker variant of secondary"
    )
    
    # Tertiary Colors
    TERTIARY_SUCCESS = ColorToken(
        name="Tertiary (Success/Active)",
        hex_value="#4CAF50",
        usage="Success states, active indicators"
    )
    
    TERTIARY_WARNING = ColorToken(
        name="Warning",
        hex_value="#FF9800",
        usage="Warning states"
    )
    
    TERTIARY_ERROR = ColorToken(
        name="Error",
        hex_value="#F44336",
        usage="Error states"
    )
    
    # Container Colors (Glassmorphism)
    CONTAINER_DARK = ColorToken(
        name="Container Dark",
        hex_value="#1C1B1B",
        usage="Card/container background with blur"
    )
    
    CONTAINER_DARK_RGBA = (28/255, 27/255, 27/255, 0.8)
    
    # Text Colors
    TEXT_HIGH_EMPHASIS = ColorToken(
        name="Text High Emphasis",
        hex_value="#FFFFFF",
        rgba=(1, 1, 1, 0.95),
        usage="Primary text"
    )
    
    TEXT_MEDIUM_EMPHASIS = ColorToken(
        name="Text Medium Emphasis",
        hex_value="#FFFFFF",
        rgba=(1, 1, 1, 0.7),
        usage="Secondary text"
    )
    
    TEXT_LOW_EMPHASIS = ColorToken(
        name="Text Low Emphasis",
        hex_value="#FFFFFF",
        rgba=(1, 1, 1, 0.5),
        usage="Disabled/hint text"
    )
    
    # ==================== LIGHT MODE ====================
    
    SURFACE_LIGHT = ColorToken(
        name="Surface Light",
        hex_value="#FDFBFF",
        usage="Primary background - Light mode"
    )
    
    PRIMARY_LIGHT_MODE = ColorToken(
        name="Primary Light Mode",
        hex_value="#0061A4",
        usage="Primary color in light mode"
    )
    
    SECONDARY_LIGHT_MODE = ColorToken(
        name="Secondary Light Mode",
        hex_value="#006972",
        usage="Secondary color in light mode"
    )
    
    ON_SURFACE_LIGHT = ColorToken(
        name="On Surface Light",
        hex_value="#1C1B1F",
        usage="Text on light surfaces"
    )
    
    CONTAINER_LIGHT = ColorToken(
        name="Container Light",
        hex_value="#F0F0F5",
        rgba=(240/255, 240/255, 245/255, 0.9),
        usage="Card/container background in light mode"
    )
    
    # ==================== SEMANTIC COLORS ====================
    
    SUCCESS = ColorToken(
        name="Success",
        hex_value="#4CAF50",
        usage="Success states, confirmations"
    )
    
    WARNING = ColorToken(
        name="Warning",
        hex_value="#FF9800",
        usage="Warning states, alerts"
    )
    
    ERROR = ColorToken(
        name="Error",
        hex_value="#F44336",
        usage="Error states, failures"
    )
    
    INFO = ColorToken(
        name="Info",
        hex_value="#2196F3",
        usage="Information states"
    )
    
    # ==================== GLASMORPHISM EFFECTS ====================
    
    @staticmethod
    def get_glassmorphism_colors(backdrop_blur: float = 20) -> Dict[str, Any]:
        """Get glassmorphism effect colors"""
        return {
            'dark': {
                'background': TurboMindColors.CONTAINER_DARK_RGBA,
                'blur': backdrop_blur,
                'border': TurboMindColors.PRIMARY_BRAND_BLUE.with_alpha(0.2)
            },
            'light': {
                'background': TurboMindColors.CONTAINER_LIGHT.rgba,
                'blur': backdrop_blur,
                'border': TurboMindColors.PRIMARY_LIGHT_MODE.with_alpha(0.1)
            }
        }
    
    # ==================== SHADOWS ====================
    
    @staticmethod
    def get_shadows() -> Dict[str, Tuple]:
        """Get shadow definitions for different modes"""
        return {
            'dark': {
                'small': (0, 4, 8, 0.1, TurboMindColors.PRIMARY_BRAND_BLUE.rgba),
                'medium': (0, 4, 20, 0.15, TurboMindColors.PRIMARY_BRAND_BLUE.rgba),
                'large': (0, 8, 30, 0.2, TurboMindColors.PRIMARY_BRAND_BLUE.rgba),
                'glow': (0, 0, 20, 0.3, TurboMindColors.PRIMARY_BRAND_BLUE.rgba),
            },
            'light': {
                'small': (0, 2, 4, 0.05, (0, 0, 0, 0.1)),
                'medium': (0, 4, 8, 0.05, (0, 0, 0, 0.1)),
                'large': (0, 8, 30, 0.05, (0, 0, 0, 0.1)),
                'glow': (0, 0, 20, 0.1, (0, 0, 0, 0.1)),
            }
        }
    
    # ==================== GRADIENTS ====================
    
    @staticmethod
    def get_gradients() -> Dict[str, Tuple]:
        """Get gradient definitions"""
        return {
            'primary': (
                TurboMindColors.PRIMARY_BRAND_BLUE.rgba,
                TurboMindColors.SECONDARY_BRAND_CYAN.rgba
            ),
            'success': (
                TurboMindColors.SUCCESS.rgba,
                TurboMindColors.PRIMARY_BRAND_BLUE.rgba
            ),
            'progress': (
                TurboMindColors.PRIMARY_BRAND_BLUE.rgba,
                TurboMindColors.SECONDARY_BRAND_CYAN.rgba
            ),
        }
    
    # ==================== UTILITY METHODS ====================
    
    @classmethod
    def get_color_by_name(cls, name: str) -> ColorToken:
        """Get color token by name"""
        for attr in dir(cls):
            if not attr.startswith('_') and isinstance(getattr(cls, attr), ColorToken):
                if getattr(cls, attr).name.lower() == name.lower():
                    return getattr(cls, attr)
        raise ValueError(f"Color '{name}' not found")
    
    @classmethod
    def get_all_colors(cls) -> Dict[str, ColorToken]:
        """Get all color tokens"""
        colors = {}
        for attr in dir(cls):
            if not attr.startswith('_') and isinstance(getattr(cls, attr), ColorToken):
                colors[attr] = getattr(cls, attr)
        return colors
    
    @classmethod
    def to_kivy_palette(cls) -> Dict[str, Tuple]:
        """Convert to Kivy-compatible color palette"""
        return {
            attr: color.to_kivy_color()
            for attr, color in cls.get_all_colors().items()
        }


# Create color palette instance for easy access
color_palette = TurboMindColors()
