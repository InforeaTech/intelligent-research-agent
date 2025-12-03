"""
Test script for Phase 1: Database Models & Configuration
Tests that all models are properly configured and tables can be created.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models import init_db, User, Profile, Note, Log, SessionLocal, Base, engine


def test_table_creation():
    """Test that all tables can be created."""
    print("Testing table creation...")
    try:
        # Drop all tables (clean slate for testing)
        Base.metadata.drop_all(bind=engine)
        print("✓ Dropped existing tables")
        
        # Create all tables
        init_db()
        print("✓ Created all tables")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['users', 'profiles', 'notes', 'logs']
        for table in expected_tables:
            if table in tables:
                print(f"✓ Table '{table}' exists")
            else:
                print(f"✗ Table '{table}' missing!")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_model_relationships():
    """Test that model relationships work correctly."""
    print("\nTesting model relationships...")
    db = SessionLocal()
    try:
        # Create a test user
        user = User(
            email="test@example.com",
            name="Test User",
            provider="google",
            provider_user_id="123456"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✓ Created user: {user}")
        
        # Create a test profile
        profile = Profile(
            user_id=user.id,
            name="John Doe",
            company="Acme Corp",
            profile_text="Test profile content",
            search_provider="ddg",
            model_provider="openai",
            from_cache=False
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        print(f"✓ Created profile: {profile}")
        
        # Create a test note
        note = Note(
            profile_id=profile.id,
            user_id=user.id,
            note_text="Test connection note",
            tone="professional",
            length=300,
            model_provider="openai",
            from_cache=False
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        print(f"✓ Created note: {note}")
        
        # Create a test log
        log = Log(
            user_id=user.id,
            action_type="test_action",
            user_input={"test": "data"},
            final_output="test output"
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        print(f"✓ Created log: {log}")
        
        # Test relationships
        user_from_db = db.query(User).filter(User.id == user.id).first()
        assert len(user_from_db.profiles) == 1
        assert len(user_from_db.notes) == 1
        assert len(user_from_db.logs) == 1
        print("✓ User relationships working")
        
        profile_from_db = db.query(Profile).filter(Profile.id == profile.id).first()
        assert len(profile_from_db.notes) == 1
        assert profile_from_db.user.email == "test@example.com"
        print("✓ Profile relationships working")
        
        note_from_db = db.query(Note).filter(Note.id == note.id).first()
        assert note_from_db.profile.name == "John Doe"
        assert note_from_db.user.email == "test@example.com"
        print("✓ Note relationships working")
        
        # Clean up test data
        db.delete(log)
        db.delete(note)
        db.delete(profile)
        db.delete(user)
        db.commit()
        print("✓ Cleaned up test data")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Run all Phase 1 tests."""
    print("=" * 60)
    print("Phase 1: Database Models & Configuration - Testing")
    print("=" * 60)
    
    # Test 1: Table creation
    if not test_table_creation():
        print("\n❌ Table creation test FAILED")
        return False
    
    # Test 2: Relationships
    if not test_model_relationships():
        print("\n❌ Relationship test FAILED")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All Phase 1 tests PASSED")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review the created models in backend/models/")
    print("2. Update requirements.txt with new dependencies")
    print("3. Proceed to Phase 2: Repository Layer")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
