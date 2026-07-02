#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Typography
========================
Typography tokens based on design documentation.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple
from enum import Enum


class FontWeight(Enum):
    """Font weight constants"""
    THIN = 100
    EXTRA_LIGHT = 200
    LIGHT = 300
    REGULAR = 400
    MEDIUM = 500
    SEMI_BOLD = 600
    BOLD = 700
    EXTRA_BOLD = 800
    BLACK = 900


class TextAlign(Enum):
    """Text alignment constants"""
    LEFT = 'left'
    CENTER = 'center'
    RIGHT = 'right'
    JUSTIFY = 'justify'


@dataclass
class TypographyToken:
    """Represents a typography token"""
    name: str
    font_family: str = "Plus Jakarta Sans"
    font_size: float = 16  # in sp (scaled pixels)
    font_weight: FontWeight = FontWeight.REGULAR
    line_height: float = 1.0
    letter_spacing: float = 0.0  # percentage
    text_transform: str = "none"  # none, uppercase, lowercase, capitalize
    color: str = "text_primary"  # color reference
    opacity: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'font_weight': self.font_weight.value,
            'line_height': self.line_height,
            'letter_spacing': self.letter_spacing,
            'text_transform': self.text_transform,
            'color': self.color,
            'opacity': self.opacity
        }
    
    def get_kivy_properties(self) -> Dict[str, Any]:
        """Get Kivy-compatible properties"""
        return {
            'font_name': self.font_family,
            'font_size': self.font_size,
            'bold': self.font_weight.value >= 700,
            'halign': 'center' if self.text_transform == 'uppercase' else 'left',
            'valign': 'middle'
        }


class TurboMindTypography:
    """
    Typography system for TurboMind AI.
    
    Primary Font: Plus Jakarta Sans (Modern, geometric, high legibility)
    """
    
    # Font family
    PRIMARY_FONT = "Plus Jakarta Sans"
    FALLBACK_FONTS = ["Roboto", "Noto Sans", "Arial", "sans-serif"]
    
    # ==================== DISPLAY ====================
    
    DISPLAY_LARGE = TypographyToken(
        name="Display Large",
        font_family=PRIMARY_FONT,
        font_size=32,
        font_weight=FontWeight.BOLD,
        line_height=1.0,
        letter_spacing=-0.01,
        text_transform="none",
        color="text_primary"
    )
    
    DISPLAY_MEDIUM = TypographyToken(
        name="Display Medium",
        font_family=PRIMARY_FONT,
        font_size=28,
        font_weight=FontWeight.BOLD,
        line_height=1.0,
        letter_spacing=0.0,
        text_transform="none",
        color="text_primary"
    )
    
    DISPLAY_SMALL = TypographyToken(
        name="Display Small",
        font_family=PRIMARY_FONT,
        font_size=24,
        font_weight=FontWeight.BOLD,
        line_height=1.0,
        letter_spacing=0.0,
        text_transform="none",
        color="text_primary"
    )
    
    # ==================== HEADLINES ====================
    
    HEADLINE_LARGE = TypographyToken(
        name="Headline Large",
        font_family=PRIMARY_FONT,
        font_size=24,
        font_weight=FontWeight.BOLD,
        line_height=1.2,
        letter_spacing=0.0,
        text_transform="none",
        color="text_primary"
    )
    
    HEADLINE_MEDIUM = TypographyToken(
        name="Headline Medium",
        font_family=PRIMARY_FONT,
        font_size=20,
        font_weight=FontWeight.BOLD,
        line_height=1.2,
        letter_spacing=0.0,
        text_transform="none",
        color="text_primary"
    )
    
    HEADLINE_SMALL = TypographyToken(
        name="Headline Small",
        font_family=PRIMARY_FONT,
        font_size=18,
        font_weight=FontWeight.BOLD,
        line_height=1.3,
        letter_spacing=0.0,
        text_transform="none",
        color="text_primary"
    )
    
    # ==================== BODY ====================
    
    BODY_LARGE = TypographyToken(
        name="Body Large",
        font_family=PRIMARY_FONT,
        font_size=18,
        font_weight=FontWeight.REGULAR,
        line_height=1.5,
        letter_spacing=0.0,
        text_transform="none",
        color="text_primary"
    )
    
    BODY_MEDIUM = TypographyToken(
        name="Body Medium",
        font_family=PRIMARY_FONT,
        font_size=16,
        font_weight=FontWeight.REGULAR,
        line_height=1.5,
        letter_spacing=0.0,
        text_transform="none",
        color="text_primary"
    )
    
    BODY_SMALL = TypographyToken(
        name="Body Small",
        font_family=PRIMARY_FONT,
        font_size=14,
        font_weight=FontWeight.REGULAR,
        line_height=1.5,
        letter_spacing=0.0,
        text_transform="none",
        color="text_secondary"
    )
    
    # ==================== LABELS ====================
    
    LABEL_LARGE = TypographyToken(
        name="Label Large",
        font_family=PRIMARY_FONT,
        font_size=14,
        font_weight=FontWeight.MEDIUM,
        line_height=1.4,
        letter_spacing=0.01,
        text_transform="none",
        color="text_primary"
    )
    
    LABEL_MEDIUM = TypographyToken(
        name="Label Medium",
        font_family=PRIMARY_FONT,
        font_size=12,
        font_weight=FontWeight.MEDIUM,
        line_height=1.4,
        letter_spacing=0.02,
        text_transform="uppercase",
        color="text_secondary"
    )
    
    LABEL_SMALL = TypographyToken(
        name="Label Small",
        font_family=PRIMARY_FONT,
        font_size=11,
        font_weight=FontWeight.MEDIUM,
        line_height=1.4,
        letter_spacing=0.1,
        text_transform="uppercase",
        color="text_secondary"
    )
    
    # ==================== BUTTONS ====================
    
    BUTTON_LARGE = TypographyToken(
        name="Button Large",
        font_family=PRIMARY_FONT,
        font_size=16,
        font_weight=FontWeight.MEDIUM,
        line_height=1.0,
        letter_spacing=0.02,
        text_transform="uppercase",
        color="on_primary"
    )
    
    BUTTON_MEDIUM = TypographyToken(
        name="Button Medium",
        font_family=PRIMARY_FONT,
        font_size=14,
        font_weight=FontWeight.MEDIUM,
        line_height=1.0,
        letter_spacing=0.02,
        text_transform="uppercase",
        color="on_primary"
    )
    
    BUTTON_SMALL = TypographyToken(
        name="Button Small",
        font_family=PRIMARY_FONT,
        font_size=12,
        font_weight=FontWeight.MEDIUM,
        line_height=1.0,
        letter_spacing=0.02,
        text_transform="uppercase",
        color="on_primary"
    )
    
    # ==================== UTILITY METHODS ====================
    
    @classmethod
    def get_token_by_name(cls, name: str) -> TypographyToken:
        """Get typography token by name"""
        for attr in dir(cls):
            if not attr.startswith('_') and isinstance(getattr(cls, attr), TypographyToken):
                if getattr(cls, attr).name.lower() == name.lower():
                    return getattr(cls, attr)
        raise ValueError(f"Typography token '{name}' not found")
    
    @classmethod
    def get_all_tokens(cls) -> Dict[str, TypographyToken]:
        """Get all typography tokens"""
        tokens = {}
        for attr in dir(cls):
            if not attr.startswith('_') and isinstance(getattr(cls, attr), TypographyToken):
                tokens[attr] = getattr(cls, attr)
        return tokens
    
    @classmethod
    def get_kivy_typography(cls) -> Dict[str, Dict[str, Any]]:
        """Get Kivy-compatible typography styles"""
        return {
            attr: token.get_kivy_properties()
            for attr, token in cls.get_all_tokens().items()
        }
    
    @classmethod
    def get_css_typography(cls) -> Dict[str, str]:
        """Get CSS-compatible typography styles"""
        css = {}
        for attr, token in cls.get_all_tokens().items():
            css[attr] = f"""
            font-family: {token.font_family};
            font-size: {token.font_size}px;
            font-weight: {token.font_weight.value};
            line-height: {token.line_height};
            letter-spacing: {token.letter_spacing}%;
            text-transform: {token.text_transform};
            """
        return css


# Create typography instance for easy access
typography = TurboMindTypography()
