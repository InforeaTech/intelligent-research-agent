
import sys
import os
import unittest
from datetime import timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

try:
    import jose
    import itsdangerous
    import authlib
    print("[OK] Dependencies installed: python-jose, itsdangerous, authlib")
except ImportError as e:
    print(f"[FAIL] Missing dependency: {e}")
    sys.exit(1)

try:
    from auth import (
        create_access_token, 
        verify_access_token, 
        get_oauth_client, 
        OAUTH_PROVIDERS
    )
    print("[OK] backend/auth.py importable")
except ImportError as e:
    print(f"[FAIL] Failed to import backend/auth.py: {e}")
    sys.exit(1)

class TestAuthPhase1(unittest.TestCase):
    def test_jwt_flow(self):
        user_data = {"user_id": 123, "email": "verify@example.com"}
        token = create_access_token(user_data)
        self.assertIsInstance(token, str)
        print("[OK] JWT Token creation successful")
        
        decoded = verify_access_token(token)
        self.assertEqual(decoded["user_id"], 123)
        self.assertEqual(decoded["email"], "verify@example.com")
        print("[OK] JWT Token verification successful")

    def test_oauth_config_structure(self):
        self.assertIn("google", OAUTH_PROVIDERS)
        self.assertIn("microsoft", OAUTH_PROVIDERS)
        self.assertIn("github", OAUTH_PROVIDERS)
        print("[OK] OAuth Providers configuration present")

    def test_oauth_client_init_error(self):
        # Force clear credentials to ensure ValueError is raised
        # This handles cases where .env might have placeholder values
        original_id = OAUTH_PROVIDERS["google"]["client_id"]
        OAUTH_PROVIDERS["google"]["client_id"] = None
        
        try:
            with self.assertRaises(ValueError):
                get_oauth_client("google")
            print("[OK] get_oauth_client validation working (expected ValueError for missing creds)")
        finally:
            # Restore for other tests if needed
            OAUTH_PROVIDERS["google"]["client_id"] = original_id

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
