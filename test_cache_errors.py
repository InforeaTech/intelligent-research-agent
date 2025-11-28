import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import DatabaseManager

def test_error_cache_handling():
    """Test that cached errors are skipped and None is returned."""
    print("=" * 60)
    print("Testing Error-Based Cache Invalidation")
    print("=" * 60)
    
    # Initialize database
    db = DatabaseManager(db_path="test_cache_errors.db")
    
    # Test 1: Insert an error result
    print("\n1. Inserting error result into cache...")
    db.log_interaction(
        action_type="generate_profile",
        search_data={"test": "data"},
        final_output="Error: API Key is required for profile generation."
    )
    print("✓ Error result cached")
    
    # Test 2: Try to retrieve it (should return None)
    print("\n2. Attempting to retrieve cached error...")
    result = db.check_existing_log(
        action_type="generate_profile",
        search_data={"test": "data"}
    )
    
    if result is None:
        print("✓ SUCCESS: Cached error was skipped, returned None")
    else:
        print(f"✗ FAIL: Expected None, got: {result}")
    
    # Test 3: Insert a valid result
    print("\n3. Inserting valid result into cache...")
    db.log_interaction(
        action_type="generate_profile",
        search_data={"test": "valid_data"},
        final_output="Valid profile content here"
    )
    print("✓ Valid result cached")
    
    # Test 4: Retrieve valid result (should return the content)
    print("\n4. Attempting to retrieve cached valid result...")
    result = db.check_existing_log(
        action_type="generate_profile",
        search_data={"test": "valid_data"}
    )
    
    if result == "Valid profile content here":
        print("✓ SUCCESS: Valid cached result was returned")
    else:
        print(f"✗ FAIL: Expected 'Valid profile content here', got: {result}")
    
    # Test 5: Test fuzzy match with error
    print("\n5. Testing fuzzy match with error for deep_research...")
    db.log_interaction(
        action_type="deep_research",
        user_input={"topic": "Test Topic"},
        final_output="Error generating report: Connection timeout"
    )
    print("✓ Error result cached for deep_research")
    
    result = db.check_existing_log(
        action_type="deep_research",
        user_input={"topic": "Test Topic"}
    )
    
    if result is None:
        print("✓ SUCCESS: Cached error was skipped in fuzzy match")
    else:
        print(f"✗ FAIL: Expected None, got: {result}")
    
    # Test 6: Test note generation with error and tone/length matching
    print("\n6. Testing note generation with error...")
    db.log_interaction(
        action_type="generate_note",
        user_input={"profile_text": "Test profile", "tone": "professional", "length": 300, "context": "test"},
        final_output="Error: Rate limit exceeded"
    )
    print("✓ Error result cached for generate_note")
    
    result = db.check_existing_log(
        action_type="generate_note",
        user_input={"profile_text": "Test profile", "tone": "professional", "length": 300, "context": "test"}
    )
    
    if result is None:
        print("✓ SUCCESS: Cached note error was skipped")
    else:
        print(f"✗ FAIL: Expected None, got: {result}")
    
    # Cleanup
    if os.path.exists("test_cache_errors.db"):
        os.remove("test_cache_errors.db")
        print("\n✓ Test database cleaned up")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_error_cache_handling()
