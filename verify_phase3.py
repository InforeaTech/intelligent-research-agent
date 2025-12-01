"""
Verification script for Phase 3: Backend API Endpoints
Tests authentication schemas and endpoint availability
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

print("=" * 60)
print("Verifying Phase 3: Backend API Endpoints")
print("=" * 60)

# Test 1: Import schemas
print("\n[TEST 1] Verifying authentication schemas...")
try:
    from schemas import User, LoginResponse, AuthCallbackResponse
    print("[OK] User schema imported")
    print("[OK] LoginResponse schema imported")
    print("[OK] AuthCallbackResponse schema imported")
    
    # Test schema validation
    test_user = User(
        id=1,
        email="test@example.com",
        name="Test User",
        picture="http://example.com/pic.jpg",
        provider="google"
    )
    print(f"[OK] User schema validation works: {test_user.email}")
except ImportError as e:
    print(f"[FAIL] Schema import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[FAIL] Schema validation failed: {e}")
    sys.exit(1)

# Test 2: Check if main.py has authentication imports
print("\n[TEST 2] Verifying main.py auth imports...")
try:
    with open('backend/main.py', 'r') as f:
        main_content = f.read()
        
    required_imports = [
        'from auth import',
        'get_authorization_url',
        'exchange_code_for_token',
        'get_user_info',
        'create_access_token',
        'verify_access_token'
    ]
    
    for imp in required_imports:
        if imp in main_content:
            print(f"[OK] Found import: {imp}")
        else:
            print(f"[FAIL] Missing import: {imp}")
except Exception as e:
    print(f"[FAIL] Could not read main.py: {e}")

# Test 3: Check if endpoints are defined
print("\n[TEST 3] Verifying authentication endpoints...")
try:
    required_endpoints = [
        '@app.get("/auth/login/{provider}")',
        '@app.get("/auth/callback/{provider}")',
        '@app.get("/auth/user")',
        '@app.post("/auth/logout")'
    ]
    
    for endpoint in required_endpoints:
        if endpoint in main_content:
            print(f"[OK] Found endpoint: {endpoint}")
        else:
            print(f"[FAIL] Missing endpoint: {endpoint}")
except Exception as e:
    print(f"[FAIL] Endpoint check failed: {e}")

# Test 4: Verify FastAPI app can be imported (basic syntax check)
print("\n[TEST 4] Verifying FastAPI app imports...")
try:
    from main import app
    print("[OK] FastAPI app imported successfully")
    print(f"[OK] App title: {app.title}")
    
    # Count routes
    route_count = len(app.routes)
    print(f"[OK] Total routes: {route_count}")
    
    # Check for auth routes
    auth_routes = [route for route in app.routes if hasattr(route, 'path') and '/auth/' in route.path]
    print(f"[OK] Authentication routes: {len(auth_routes)}")
    
except Exception as e:
    print(f"[FAIL] FastAPI app import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Verification Complete")
print("=" * 60)
