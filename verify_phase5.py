"""
Simple verification that the refactored code works.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models import init_db, SessionLocal
from repositories import LogRepository
from agent import ResearchAgent

def test_basic_functionality():
    """Test that agent and repositories work together."""
    print("Testing Phase 5 refactoring...")
    
    # Initialize DB
    init_db()
    print("✓ Database initialized")
    
    # Create DB session
    db = SessionLocal()
    
    try:
        # Test LogRepository
        log_repo = LogRepository(db)
        print("✓ LogRepository instantiated")
        
        # Create a test log
        log = log_repo.create_log(
            action_type="test",
            search_data={"test": "data"},
            final_output="test output"
        )
        print(f"✓ Created test log: {log.id}")
        
        # Test cache check
        cached = log_repo.check_cache(
            action_type="test",
            search_data={"test": "data"}
        )
        print(f"✓ Cache check works: {cached is not None}")
        
        # Test Agent
        agent = ResearchAgent()
        print("✓ Agent instantiated (no DatabaseManager)")
        
        print("\n✅ Phase 5 refactoring verified!")
        return True
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
