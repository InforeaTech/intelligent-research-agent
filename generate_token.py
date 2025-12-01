import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from auth import create_access_token

token = create_access_token({
    'user_id': 1,
    'email': 'test@example.com',
    'name': 'Test User'
})

print(token)
