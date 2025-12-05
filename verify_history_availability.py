import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from models.profile import Profile
from models.base import Base
from tool_executor import ToolExecutor

# Setup DB connection (using the same DB as the app)
# Assuming the app uses 'sqlite:///./agent_logs.db' based on previous context or common patterns
# I need to verify the DB URL from main.py or database.py, but standard is usually local sqlite.
# Let's check main.py or database.py to be sure, but I'll try the default first.

DATABASE_URL = "sqlite:///./agent_logs.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify_history_availability():
    db = SessionLocal()
    try:
        # 1. Count total profiles in DB
        total_profiles = db.query(Profile).count()
        print(f"Total profiles in DB: {total_profiles}")
        
        # 2. List all profiles for manual verification
        all_profiles = db.query(Profile).all()
        print("--- All Profiles in DB ---")
        for p in all_profiles:
            print(f"ID: {p.id}, Name: {p.name}, Company: {p.company}")
        print("--------------------------")
        
        # 3. Test Tool Execution with default limit
        print("\n--- Testing Tool Execution (Default Limit) ---")
        executor = ToolExecutor(db=db)
        result = executor.execute_tool("get_user_research_history", {})
        print(f"Result Success: {result['success']}")
        print(f"Result Content:\n{result.get('result')}")
        
        # 4. Test Tool Execution with high limit (to see if it gets all)
        print("\n--- Testing Tool Execution (Limit=100) ---")
        result_high = executor.execute_tool("get_user_research_history", {"limit": 100})
        print(f"Result Content Length: {len(result_high.get('result', ''))}")
        # Count items in result string (rough check)
        count_in_result = result_high.get('result', '').count("Profile:")
        print(f"Items returned: {count_in_result}")
        
        if count_in_result == total_profiles:
            print("\nSUCCESS: Tool can retrieve all profiles.")
        else:
            print(f"\nWARNING: Tool retrieved {count_in_result} items, but DB has {total_profiles}.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_history_availability()
