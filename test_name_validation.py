"""Test script to verify name validation works correctly."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from schemas import ProfileRequest
from pydantic import ValidationError

def test_name_validation():
    """Test various name inputs to verify validation is working."""
    print("=" * 60)
    print("Testing Name Validation")
    print("=" * 60)
    
    # Test cases: (name, company, should_pass)
    test_cases = [
        ("John Doe", "Tech Corp", True, "Valid: Two-word name"),
        ("Mary Jane Watson", "Daily Bugle", True, "Valid: Three-word name"),
        ("Patrick O'Brien", "Corp", True, "Valid: Name with apostrophe"),
        ("Mary-Jane", "Corp", False, "Invalid: Only one part (hyphenated)"),
        ("John", "", False, "Invalid: Single name"),
        ("", "", False, "Invalid: Empty name"),
        ("Tesla Motors", "", False, "Invalid: Company name not person"),
        ("John123", "", False, "Invalid: Contains numbers"),
        ("Dr. Martin Luther King Jr.", "", True, "Valid: Name with titles/suffix"),
    ]
    
    passed = 0
    failed = 0
    
    for name, company, should_pass, description in test_cases:
        try:
            request = ProfileRequest(
                name=name,
                company=company,
                api_key="test_key"
            )
            if should_pass:
                print(f"✓ PASS: {description}")
                print(f"  Input: '{name}'")
                passed += 1
            else:
                print(f"✗ FAIL: {description}")
                print(f"  Input: '{name}' - Expected validation error but passed")
                failed += 1
        except ValidationError as e:
            error_msg = e.errors()[0]['msg']
            if not should_pass:
                print(f"✓ PASS: {description}")
                print(f"  Input: '{name}'")
                print(f"  Error: {error_msg}")
                passed += 1
            else:
                print(f"✗ FAIL: {description}")
                print(f"  Input: '{name}' - Unexpected validation error: {error_msg}")
                failed += 1
        print()
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = test_name_validation()
    sys.exit(0 if success else 1)
