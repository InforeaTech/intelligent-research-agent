import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import init_db

if __name__ == "__main__":
    print("Running database migration...")
    try:
        init_db()
        print("Migration successful.")
    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
