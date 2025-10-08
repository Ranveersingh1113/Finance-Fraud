"""
Simple test to check API connection and diagnose issues.
"""
import requests
import sys

def test_api_connection():
    """Test API connection with detailed error reporting."""
    print("🔍 Testing API Connection...")
    
    # Test different endpoints
    endpoints = [
        ("http://localhost:8001", "Root endpoint"),
        ("http://localhost:8001/health", "Health endpoint"),
        ("http://localhost:8002", "Alternative port 8002"),
        ("http://localhost:8000", "Alternative port 8000")
    ]
    
    for url, description in endpoints:
        print(f"\n📡 Testing {description}: {url}")
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ SUCCESS: Status {response.status_code}")
            if response.status_code == 200:
                print(f"📄 Response: {response.json()}")
                return True
        except requests.exceptions.ConnectionError:
            print(f"❌ CONNECTION ERROR: Cannot connect to {url}")
        except requests.exceptions.Timeout:
            print(f"⏰ TIMEOUT: Request timed out for {url}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n🔧 DIAGNOSIS:")
    print("The API server is not running. Please start it with:")
    print("python start_advanced_api.py")
    
    return False

if __name__ == "__main__":
    test_api_connection()


