import sys
import os
from unittest.mock import MagicMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from search_service import SearchService

def test_search_fix():
    print("Testing search_web with float max_results...")
    service = SearchService()
    
    # Mock ddgs to avoid actual network call and just check if it accepts the call
    # However, the error was in the casting before the call or inside the call.
    # The error was: TypeError: slice indices must be integers... inside ddgs.text
    # So we need to let it call ddgs.text, but we can mock ddgs.text to return empty list
    # IF the input is correct. But the error happens because ddgs.text receives a float.
    # My fix casts it to int BEFORE calling ddgs.text.
    
    # So if I mock ddgs.text, I can verify it was called with an int.
    service.ddgs = MagicMock()
    service.ddgs.text.return_value = []
    
    try:
        service.search_web("test query", max_results=5.0)
        print("SUCCESS: search_web accepted float max_results without crashing")
        
        # Verify it was called with int
        args, kwargs = service.ddgs.text.call_args
        print(f"Called with kwargs: {kwargs}")
        if isinstance(kwargs.get('max_results'), int):
             print("PASS: max_results was cast to int")
        else:
             print("FAIL: max_results was NOT cast to int")
             
    except Exception as e:
        print(f"FAIL: search_web crashed with error: {e}")

if __name__ == "__main__":
    test_search_fix()
