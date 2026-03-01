#!/usr/bin/env python3
"""Convenience entry point — run the app from the project root.

Usage:
    python run.py
"""

import sys
import os

# Add src/ to the path so the package can be imported directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from todo_app.__main__ import main

if __name__ == "__main__":
    main()
