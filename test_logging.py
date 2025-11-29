"""
Test script for the new logging system.
Tests logger_config.py and database.py logging functionality.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from logger_config import get_logger, set_request_id, log_performance
from database import DatabaseManager
import uuid

# Test 1: Basic logging
print("=" * 60)
print("TEST 1: Basic Logging")
print("=" * 60)

logger = get_logger("test_logging")
logger.info("Testing basic info log")
logger.debug("Testing debug log (may not appear if LOG_LEVEL=INFO)")
logger.warning("Testing warning log")
logger.error("Testing error log")

# Test 2: Request correlation
print("\n" + "=" * 60)
print("TEST 2: Request Correlation")
print("=" * 60)

request_id = str(uuid.uuid4())
set_request_id(request_id)
logger.info("Log with request ID", extra={'extra_data': {'test_field': 'test_value'}})

# Test 3: Performance timing decorator
print("\n" + "=" * 60)
print("TEST 3: Performance Timing")
print("=" * 60)

@log_performance()
def slow_function():
    """Simulate a slow operation."""
    import time
    time.sleep(0.1)
    return "completed"

result = slow_function()
print(f"Function result: {result}")

# Test 4: Database logging
print("\n" + "=" * 60)
print("TEST 4: Database Logging")
print("=" * 60)

db = DatabaseManager("test_logs.db")

# Log an interaction
db.log_interaction(
    action_type="test_action",
    user_input={"name": "Test User", "company": "Test Corp"},
    final_output="Test output"
)

# Check cache (should return None)
cached = db.check_existing_log("test_action", {"name": "Test User"})
print(f"Cache check result: {cached}")

# Test 5: Log cleanup
print("\n" + "=" * 60)
print("TEST 5: Log Cleanup")
print("=" * 60)

deleted_count = db.cleanup_old_logs(retention_days=30)
print(f"Deleted {deleted_count} old log entries")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED")
print("=" * 60)
print("\nCheck the following:")
print("1. Console output above shows structured logs")
print("2. logs/app.log file was created (if LOG_FILE is set)")
print("3. backend/test_logs.db was created")
print("4. Request IDs appear in logs")
print("5. Performance timing appears in logs")
