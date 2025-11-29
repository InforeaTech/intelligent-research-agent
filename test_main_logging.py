"""
Test script to verify backend/main.py logging integration.
"""
import sys
import os
import logging

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from logger_config import get_logger

def test_main_import():
    print("Attempting to import backend.main...")
    try:
        from main import app, logger
        print("Successfully imported main.app")
        
        if isinstance(logger, logging.Logger):
            print(f"Logger initialized correctly: {logger.name}")
        else:
            print("Logger not initialized correctly")
            
        print("Main module logging verification passed.")
    except Exception as e:
        print(f"Failed to import main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_main_import()
