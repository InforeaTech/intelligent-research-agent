import requests
import time
import sys

def test_services():
    print("Waiting for services to start...")
    # Simple retry logic
    max_retries = 10
    for i in range(max_retries):
        try:
            # Check Gateway
            requests.get("http://localhost:8000/docs", timeout=1)
            print("✓ Gateway is up!")
            break
        except:
            time.sleep(1)
            if i == max_retries - 1:
                print("✗ Gateway failed to start.")
                return

    # Test Audit Service
    try:
        res = requests.get("http://localhost:8003/logs")
        if res.status_code == 200:
            print("✓ Audit Service is reachable")
        else:
            print(f"✗ Audit Service returned {res.status_code}")
    except Exception as e:
        print(f"✗ Audit Service check failed: {e}")

    # Test Search Service (Mock/Dry run if possible, or just check docs)
    try:
        res = requests.get("http://localhost:8001/docs")
        if res.status_code == 200:
            print("✓ Search Service is reachable")
    except Exception as e:
        print(f"✗ Search Service check failed: {e}")

    # Test Content Service
    try:
        res = requests.get("http://localhost:8002/docs")
        if res.status_code == 200:
            print("✓ Content Service is reachable")
    except Exception as e:
        print(f"✗ Content Service check failed: {e}")

    print("\nMicroservices verification complete.")

if __name__ == "__main__":
    test_services()
