"""
Test script for Phase 3: Route Refactoring
Verifies that the refactored endpoints work correctly with SQLAlchemy repositories.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models import init_db, SessionLocal
from repositories import UserRepository, LogRepository

def test_user_repository_integration():
    """Test that UserRepository works correctly."""
    print("\n" + "="*60)
    print("Testing UserRepository Integration")
    print("="*60)
    
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        
        # Create test user
        user = repo.create_or_update(
            email="test@phase3.com",
            provider="google",
            provider_user_id="google_phase3",
            name="Phase 3 Test User"
        )
        print(f"✓ Created user: {user}")
        assert user.id is not None
        
        # Retrieve user
        retrieved = repo.get(user.id)
        print(f"✓ Retrieved user: {retrieved}")
        assert retrieved.email == "test@phase3.com"
        
        # Clean up
        repo.delete(user.id)
        print("✓ Cleaned up test user")
        
        return True
    finally:
        db.close()


def test_log_repository_integration():
    """Test that LogRepository caching works correctly."""
    print("\n" + "="*60)
    print("Testing LogRepository Integration")
    print("="*60)
    
    db = SessionLocal()
    try:
        repo = LogRepository(db)
        
        # Create test log for caching
        test_search_data = {
            "name": "John Doe",
            "company": "TestCo",
            "search_provider": "ddg",
            "model_provider": "openai"
        }
        
        log = repo.create_log(
            action_type="complete_research",
            search_data=test_search_data,
            model_input="Test input",
            model_output="Test output",
            final_output='{"test": "data"}'
        )
        print(f"✓ Created log: {log}")
        
        # Test cache check
        cached = repo.check_cache(
            action_type="complete_research",
            search_data=test_search_data
        )
        print(f"✓ Cache check result: {cached}")
        assert cached == '{"test": "data"}'
        
        # Test cache miss
        cached_miss = repo.check_cache(
            action_type="complete_research",
            search_data={"different": "data"}
        )
        print(f"✓ Cache miss returns None: {cached_miss is None}")
        assert cached_miss is None
        
        # Clean up
        repo.delete(log.id)
        print("✓ Cleaned up test log")
        
        return True
    finally:
        db.close()


def main():
    """Run all Phase 3 tests."""
    print("=" * 60)
    print("Phase 3: Route Refactoring - Integration Testing")
    print("=" * 60)
    
    # Initialize database
    init_db()
    print("✓ Database initialized")
    
    try:
        # Run integration tests
        test_user_repository_integration()
        test_log_repository_integration()
        
        print("\n" + "=" * 60)
        print("✅ All Phase 3 Integration Tests PASSED")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Manually test authentication flow with OAuth")
        print("2. Test profile generation with caching")
        print("3. Verify endpoints work correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
