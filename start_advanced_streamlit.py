"""
Startup script for the Advanced Streamlit UI.
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
    # Start Streamlit
    import subprocess
    import sys
    
    print("SUCCESS: Starting Advanced Streamlit UI...")
    print("STREAMLIT: Advanced Analyst Cockpit")
    
    # Run streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "src/frontend/advanced_streamlit_app.py",
        "--server.port", "8501",
        "--server.address", "localhost",
        "--theme.base", "dark",
        "--theme.primaryColor", "#FF6B6B",
        "--theme.backgroundColor", "#0E1117",
        "--theme.secondaryBackgroundColor", "#262730"
    ])
    
except Exception as e:
    print(f"ERROR: Error starting Advanced Streamlit: {e}")
    import traceback
    traceback.print_exc()
