#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Main Entry Point
===============================
A 100% Offline Android AI Assistant
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """Main entry point for TurboMind AI"""
    print("=" * 60)
    print("TurboMind AI - 100% Offline AI Assistant")
    print("=" * 60)
    print()
    
    # Check if running on Android
    is_android = hasattr(sys, 'getandroidapilevel')
    
    if is_android:
        print("Running on Android device")
    else:
        print("Running on desktop/computer")
    
    print()
    print("Features:")
    print("  - AI Chat")
    print("  - Documents AI")
    print("  - Voice Assistant")
    print("  - Image Understanding")
    print("  - Knowledge Base")
    print("  - Semantic Search")
    print()
    
    # Import and start the Kivy app
    try:
        from app.main_app import TurboMindApp
        print("Starting Kivy UI...")
        TurboMindApp().run()
    except ImportError as e:
        print(f"Error: {e}")
        print()
        print("Please install dependencies:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()