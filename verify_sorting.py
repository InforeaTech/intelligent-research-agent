import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from models.profile import Profile
from repositories.profile_repository import ProfileRepository

DATABASE_URL = "sqlite:///./agent_logs.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify_sorting():
    db = SessionLocal()
    try:
        repo = ProfileRepository(db)
        user_id = 1
        
        # Create dummy profiles with varying lengths if not enough exist
        # Or just search and check lengths
        
        print("--- Testing Search Sorting (Length Descending) ---")
        # Search for something common or just "a" to match most
        results = repo.search(user_id, "a", limit=10)
        
        if not results:
            print("No profiles found to test sorting.")
            return

        print(f"Found {len(results)} profiles.")
        previous_length = float('inf')
        is_sorted = True
        
        for p in results:
            length = len(p.profile_text) if p.profile_text else 0
            print(f"Profile: {p.name}, Length: {length}")
            
            if length > previous_length:
                is_sorted = False
                print("FAIL: Not sorted correctly (larger item came after smaller item)")
            
            previous_length = length
            
        if is_sorted:
            print("SUCCESS: Results are sorted by length descending.")
        else:
            print("FAIL: Results are NOT sorted by length descending.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_sorting()
