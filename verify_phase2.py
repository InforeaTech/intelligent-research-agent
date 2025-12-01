"""
Verification script for Phase 2: Database Updates
Tests user table creation and user management methods
"""

import sys
import os
import sqlite3
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

try:
    from database import DatabaseManager
    print("[OK] DatabaseManager imported successfully")
except ImportError as e:
    print(f"[FAIL] Failed to import DatabaseManager: {e}")
    sys.exit(1)

# Create test database
TEST_DB = "verify_phase2.db"
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

db = DatabaseManager(TEST_DB)

print("=" * 60)
print("Verifying Phase 2: Database Updates")
print("=" * 60)

# Check 1: Verify Schema
print("\n[CHECK 1] Verifying Schema...")
conn = sqlite3.connect(db.db_path)
cursor = conn.cursor()

# Check users table
cursor.execute("PRAGMA table_info(users)")
user_columns = {col[1] for col in cursor.fetchall()}
expected_user_columns = {'id', 'email', 'name', 'picture', 'provider', 'provider_user_id', 'created_at', 'last_login'}
missing_user_columns = expected_user_columns - user_columns
if not missing_user_columns:
    print("[OK] Users table schema correct")
else:
    print(f"[FAIL] Missing columns in users table: {missing_user_columns}")

# Check logs table for user_id
cursor.execute("PRAGMA table_info(logs)")
log_columns = {col[1] for col in cursor.fetchall()}
if 'user_id' in log_columns:
    print("[OK] Logs table has user_id column")
else:
    print("[FAIL] Logs table missing user_id column")
conn.close()

# Check 2: Verify User Creation
print("\n[CHECK 2] Verifying User Creation...")
user = db.create_or_update_user(
    email="verify@example.com",
    name="Verify User",
    picture="http://example.com/pic.jpg",
    provider="google",
    provider_user_id="12345"
)

if user and user['email'] == "verify@example.com":
    print(f"[OK] User created successfully (ID: {user['id']})")
else:
    print("[FAIL] User creation failed")

# Check 3: Verify User Retrieval
print("\n[CHECK 3] Verifying User Retrieval...")
retrieved = db.get_user_by_email("verify@example.com")
if retrieved and retrieved['id'] == user['id']:
    print("[OK] User retrieval by email successful")
else:
    print("[FAIL] User retrieval failed")

# Check 4: Verify Log Linking
print("\n[CHECK 4] Verifying Log Linking...")
db.log_interaction("test_action", {"test": "data"}, final_output="result")
logs = db.get_logs(limit=1)
if logs:
    log_id = logs[0]['id']
    db.link_log_to_user(log_id, user['id'])
    
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM logs WHERE id = ?", (log_id,))
    linked_id = cursor.fetchone()[0]
    conn.close()
    
    if linked_id == user['id']:
        print("[OK] Log linking successful")
    else:
        print(f"[FAIL] Log linking failed (Expected {user['id']}, got {linked_id})")
else:
    print("[FAIL] Failed to create log entry")

# Cleanup
if os.path.exists(db.db_path):
    try:
        os.remove(db.db_path)
        print("\n[CLEANUP] Test database removed")
    except PermissionError:
        print("\n[WARN] Could not remove test database (file in use)")

print("\n" + "=" * 60)
print("Verification Complete")
print("=" * 60)
