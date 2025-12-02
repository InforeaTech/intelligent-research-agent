
import sys
import os
import httpx
from openai import OpenAI

def test_grok_fix():
    try:
        print("Attempting to initialize OpenAI with custom http_client...")
        client = OpenAI(
            api_key="mock_key",
            base_url="https://api.x.ai/v1",
            http_client=httpx.Client()
        )
        print("Client initialized successfully.")
        
        # We can't easily call generate_profile because it creates its own client inside.
        # But we can verify if this initialization throws the error.
        # Actually, the error happened during initialization in the previous traceback:
        # File "...\openai\_base_client.py", line 857, in __init__
        
        print("Success!")
    except Exception as e:
        print(f"Caught exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_grok_fix()
