"""
Simple startup script to launch both API and Streamlit.
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def start_api_server():
    """Start the Advanced API Server."""
    print("🚀 Starting Advanced API Server...")
    
    # Start API server in background
    api_process = subprocess.Popen([
        sys.executable, "start_advanced_api.py"
    ], cwd=Path(__file__).parent)
    
    print("✅ API Server starting on http://localhost:8001")
    return api_process

def start_streamlit():
    """Start the Advanced Streamlit UI."""
    print("🎨 Starting Advanced Streamlit UI...")
    
    # Wait a bit for API to start
    time.sleep(5)
    
    # Start Streamlit
    streamlit_process = subprocess.Popen([
        sys.executable, "start_advanced_streamlit.py"
    ], cwd=Path(__file__).parent)
    
    print("✅ Streamlit UI starting on http://localhost:8501")
    return streamlit_process

def main():
    """Main startup function."""
    print("🔧 Financial Intelligence Platform - Starting System...")
    print("=" * 60)
    
    try:
        # Start API server
        api_process = start_api_server()
        
        # Wait for API to be ready
        print("⏳ Waiting for API server to be ready...")
        time.sleep(10)
        
        # Start Streamlit
        streamlit_process = start_streamlit()
        
        print("=" * 60)
        print("🎉 System Started Successfully!")
        print("📊 API Server: http://localhost:8001")
        print("🕵️ Streamlit UI: http://localhost:8501")
        print("=" * 60)
        print("Press Ctrl+C to stop both services")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down services...")
            api_process.terminate()
            streamlit_process.terminate()
            print("✅ Services stopped")
            
    except Exception as e:
        print(f"❌ Error starting system: {e}")

if __name__ == "__main__":
    main()
