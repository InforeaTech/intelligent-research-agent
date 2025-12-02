
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from content_service import ContentService

def test_grok():
    service = ContentService()
    try:
        print("Attempting to generate profile with Grok...")
        service.generate_profile({}, "mock_key", provider="grok")
        print("Success!")
    except Exception as e:
        print(f"Caught exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_grok()
