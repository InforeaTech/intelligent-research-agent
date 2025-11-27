"""
Test script to verify the Research Agent improvements.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_secrets_manager():
    """Test that secrets manager can be imported and initialized."""
    try:
        from secrets_manager import SecretManager
        sm = SecretManager()
        print("✓ Secrets Manager: Import and initialization successful")
        
        # Test set and get
        sm.set_secret("TEST_KEY", "test_value")
        value = sm.get_secret("TEST_KEY")
        assert value == "test_value", "Secret retrieval failed"
        print("✓ Secrets Manager: Set and get operations working")
        
        return True
    except Exception as e:
        print(f"✗ Secrets Manager Error: {e}")
        return False

def test_research_agent():
    """Test that research agent can be imported and initialized."""
    try:
        from agent import ResearchAgent
        agent = ResearchAgent()
        print("✓ Research Agent: Import and initialization successful")
        return True
    except Exception as e:
        print(f"✗ Research Agent Error: {e}")
        return False

def test_database_logging():
    """Test that database logging works."""
    try:
        from database import DatabaseManager
        # Use a test db file
        test_db = "test_logs.db"
        if os.path.exists(test_db):
            os.remove(test_db)
            
        db = DatabaseManager(test_db)
        db.log_interaction(
            action_type="test_action", 
            user_input={"input": "test"}, 
            search_data={"data": "test"}, 
            model_input="prompt", 
            model_output="output", 
            final_output="final"
        )
        
        logs = db.get_logs(1)
        if len(logs) == 1 and logs[0]['action_type'] == "test_action":
            print("✓ Database: Log interaction successful")
            
            # Test Cache
            print("Testing Cache...")
            
            # 1. Exact Match
            cached = db.check_existing_log("test_action", {"input": "test"}, {"data": "test"})
            if cached == "final":
                print("✓ Cache: Exact hit successful")
            else:
                print(f"✗ Cache: Exact miss. Got: {cached}")

            # 2. Fuzzy Match (Simulate Deep Research topic)
            # Log a deep research entry first
            db.log_interaction("deep_research", {"topic": "Tesla Motors"}, None, "p", "o", "Report on Tesla")
            
            # Check with slightly different topic
            fuzzy_cached = db.check_existing_log("deep_research", {"topic": "Tesla Motor"}) # Typo
            if fuzzy_cached == "Report on Tesla":
                print("✓ Cache: Fuzzy hit successful (Tesla Motors vs Tesla Motor)")
            else:
                print(f"✗ Cache: Fuzzy miss. Got: {fuzzy_cached}")
                
            # 3. Bypass Cache
            bypass_result = db.check_existing_log("deep_research", {"topic": "Tesla Motors"}, None, bypass_cache=True)
            if bypass_result is None:
                print("✓ Cache: Bypass successful")
            else:
                print(f"✗ Cache: Bypass failed. Got: {bypass_result}")
            
            # Cleanup
            if os.path.exists(test_db):
                os.remove(test_db)
            return True
        else:
            print("✗ Database: Log verification failed")
            return False
            
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_backend_api():
    """Test that the backend API can be imported with all endpoints."""
    try:
        from main import app
        print("✓ Backend API: Import successful")
        
        # Check that new endpoints exist
        routes = [route.path for route in app.routes]
        
        required_endpoints = [
            "/api/secrets/set",
            "/api/secrets/get/{key}",
            "/api/research",
            "/api/generate-note",
            "/api/deep-research"
        ]
        
        for endpoint in required_endpoints:
            if endpoint in routes:
                print(f"✓ Backend API: Endpoint {endpoint} registered")
            else:
                print(f"✗ Backend API: Endpoint {endpoint} NOT found")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Backend API Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_files_exist():
    """Test that all expected files were created."""
    files = [
        "README.md",
        "SECRETS_USAGE.md",
        ".env.example",
        ".gitignore",
        "requirements.txt",
        "backend/main.py",
        "backend/agent.py",
        "backend/secrets_manager.py",
        "backend/database.py",
        "backend/schemas.py"
    ]
    
    all_exist = True
    for file in files:
        if os.path.exists(file):
            print(f"✓ File exists: {file}")
        else:
            print(f"✗ File missing: {file}")
            all_exist = False
    
    return all_exist

def main():
    print("=" * 60)
    print("Research Agent - Verification Tests")
    print("=" * 60)
    print()
    
    print("1. Testing File Creation")
    print("-" * 60)
    test_files_exist()
    print()
    
    print("2. Testing Secrets Manager")
    print("-" * 60)
    test_secrets_manager()
    print()
    
    print("3. Testing Research Agent")
    print("-" * 60)
    test_research_agent()
    print()

    print("4. Testing Database Logging")
    print("-" * 60)
    test_database_logging()
    print()
    
    print("5. Testing Backend API")
    print("-" * 60)
    test_backend_api()
    print()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
