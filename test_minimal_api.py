"""
Minimal test server to verify API functionality.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Minimal Test API")

@app.get("/")
def root():
    return {"message": "Minimal API is working!"}

@app.get("/health")
def health():
    return {"status": "healthy", "message": "Server is running"}

if __name__ == "__main__":
    print("Starting minimal test server on http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
