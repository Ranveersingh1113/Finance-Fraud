#!/usr/bin/env python3
"""
Demo script for the Financial Intelligence Platform.
Starts both the FastAPI backend and Streamlit frontend.
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import streamlit
        import chromadb
        import sentence_transformers
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def start_backend():
    """Start the FastAPI backend."""
    print("🚀 Starting FastAPI backend...")
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "src.api.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ])
    return backend_process

def start_frontend():
    """Start the Streamlit frontend."""
    print("🚀 Starting Streamlit frontend...")
    frontend_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", 
        "run", "src/frontend/streamlit_app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])
    return frontend_process

def main():
    """Main demo function."""
    print("🔍 Financial Intelligence Platform - Phase 1 Demo")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Ensure data directories exist
    data_dirs = ["data", "data/ieee_cis", "data/sebi", "data/chroma_db"]
    for dir_path in data_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("📁 Data directories created")
    
    try:
        # Start backend
        backend_process = start_backend()
        time.sleep(3)  # Give backend time to start
        
        # Start frontend
        frontend_process = start_frontend()
        time.sleep(2)  # Give frontend time to start
        
        print("\n" + "=" * 50)
        print("🎉 Demo is running!")
        print("📊 Backend API: http://localhost:8000")
        print("🖥️  Frontend UI: http://localhost:8501")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop the demo")
        print("=" * 50)
        
        # Wait for user to stop
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping demo...")
            
    except Exception as e:
        print(f"❌ Error starting demo: {e}")
        sys.exit(1)
    
    finally:
        # Clean up processes
        try:
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ Demo stopped successfully")
        except:
            pass

if __name__ == "__main__":
    main()
