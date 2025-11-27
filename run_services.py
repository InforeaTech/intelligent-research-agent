import subprocess
import sys
import time
import os

def run_services():
    services = [
        {"name": "Audit Service", "path": "microservices_app/audit_service/main.py", "port": 8003},
        {"name": "Content Service", "path": "microservices_app/content_service/main.py", "port": 8002},
        {"name": "Search Service", "path": "microservices_app/search_service/main.py", "port": 8001},
        {"name": "Gateway", "path": "microservices_app/gateway/main.py", "port": 8000},
    ]

    processes = []
    
    print("Starting Microservices...")
    
    try:
        for service in services:
            print(f"Starting {service['name']} on port {service['port']}...")
            # Use python -m to run the module, assuming we are in the root 'agentic' dir
            # We need to adjust PYTHONPATH so imports work if needed, but since we use relative imports or standard libs, it should be fine.
            # Actually, running as scripts might have import issues if they rely on package structure.
            # Let's run them as python scripts.
            
            # Ensure we use the same python interpreter
            python_exe = sys.executable
            
            # Construct command: python microservices_app/audit_service/main.py
            cmd = [python_exe, service['path']]
            
            # Start process
            p = subprocess.Popen(cmd, cwd=os.getcwd())
            processes.append(p)
            time.sleep(2) # Wait a bit for startup

        print("\nAll services started! Press Ctrl+C to stop.")
        print("Gateway is running at http://localhost:8000")
        
        # Keep alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping services...")
        for p in processes:
            p.terminate()
        print("Services stopped.")

if __name__ == "__main__":
    run_services()
