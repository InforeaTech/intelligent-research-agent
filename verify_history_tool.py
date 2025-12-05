import sys
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from models.database import Base
from models.profile import Profile
from models.user import User
from tool_executor import ToolExecutor

# Setup test DB
TEST_DB_URL = "sqlite:///./test_history_tool.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # Create test user
    user = User(email="test@example.com", name="Test User", provider="google", provider_user_id="123")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create test profiles
    p1 = Profile(
        user_id=user.id,
        name="Elon Musk",
        company="Tesla",
        profile_text="Elon Musk is the CEO of Tesla and SpaceX.",
        search_provider="ddg",
        model_provider="openai"
    )
    
    p2 = Profile(
        user_id=user.id,
        name="Sam Altman",
        company="OpenAI",
        profile_text="Sam Altman is the CEO of OpenAI.",
        search_provider="ddg",
        model_provider="openai"
    )
    
    p3 = Profile(
        user_id=user.id,
        name="Jensen Huang",
        company="NVIDIA",
        profile_text="Jensen Huang is the CEO of NVIDIA.",
        search_provider="ddg",
        model_provider="openai"
    )
    
    db.add_all([p1, p2, p3])
    db.commit()
    db.close()

def test_history_tool():
    print("Setting up test database...")
    setup_db()
    
    db = TestingSessionLocal()
    executor = ToolExecutor(db=db)
    
    print("\nTest 1: Fetch recent history (no query)")
    result = executor.execute_tool("get_user_research_history", {"limit": 2})
    print(f"Success: {result['success']}")
    print(f"Result:\n{result['result']}")
    
    if "Elon Musk" in result['result'] or "Sam Altman" in result['result'] or "Jensen Huang" in result['result']:
        print("PASS: Found profiles in history")
    else:
        print("FAIL: Did not find profiles")
        
    print("\nTest 2: Search history (query='Tesla')")
    result = executor.execute_tool("get_user_research_history", {"query": "Tesla"})
    print(f"Success: {result['success']}")
    print(f"Result:\n{result['result']}")
    
    if "Elon Musk" in result['result'] and "Sam Altman" not in result['result']:
        print("PASS: Found correct profile for query")
    else:
        print("FAIL: Search results incorrect")
        
    print("\nTest 3: Search history (query='Nonexistent')")
    result = executor.execute_tool("get_user_research_history", {"query": "Nonexistent"})
    print(f"Success: {result['success']}")
    print(f"Result:\n{result['result']}")
    
    if "No history found" in result['result']:
        print("PASS: Correctly handled empty results")
    else:
        print("FAIL: Did not handle empty results correctly")

    db.close()
    
    # Cleanup
    if os.path.exists("test_history_tool.db"):
        os.remove("test_history_tool.db")

if __name__ == "__main__":
    test_history_tool()
