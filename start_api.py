"""
Startup script for the Advanced API Server.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = str(project_root)

print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}")

try:
    # Import and run the advanced API
    from src.api.advanced_main import app
    import uvicorn
    
    print("SUCCESS: Advanced API imported successfully")
    print("STARTING: Advanced API Server on http://localhost:8001")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info",
        reload=False
    )
    
except Exception as e:
    print(f"ERROR: Error starting Advanced API: {e}")
    import traceback
    traceback.print_exc()
