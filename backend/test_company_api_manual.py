from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from models import init_db
from auth import create_access_token

client = TestClient(app)

def test_company_endpoints():
    print("Initializing DB...")
    init_db()
    
    print("\nGenerating auth token...")
    token = create_access_token({"user_id": 1, "email": "test@example.com", "name": "Test User"})
    cookies = {"access_token": token}
    
    print("\nTesting POST /api/research/company...")
    payload = {
        "company_name": "TestCorp",
        "industry": "Tech",
        "focus_areas": ["Overview"],
        "api_key": "mock",
        "model_provider": "openai" 
    }
    
    response = client.post("/api/research/company", json=payload, cookies=cookies)
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return

    data = response.json()
    print(f"Success! ID: {data.get('id')}")
    print(f"Analysis Preview: {data.get('analysis')[:50]}...")
    
    if not data.get('id'):
        print("Error: No ID returned")
        return

    company_id = data['id']
    
    print(f"\nTesting GET /api/companies/{company_id}...")
    resp_get = client.get(f"/api/companies/{company_id}", cookies=cookies)
    print(f"Status Code: {resp_get.status_code}")
    if resp_get.status_code == 200:
        print("Data:", resp_get.json().get('name'))
        
    print(f"\nTesting GET /api/companies (List)...")
    resp_list = client.get("/api/companies", cookies=cookies)
    print(f"Status Code: {resp_list.status_code}")
    if resp_list.status_code == 200:
        print(f"Total: {resp_list.json().get('total')}")
        print(f"Items: {len(resp_list.json().get('companies'))}")

if __name__ == "__main__":
    try:
        test_company_endpoints()
    except Exception as e:
        print(f"Test Failed: {e}")
