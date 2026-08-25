#!/usr/bin/env python3
"""
Test script for registration endpoint
"""

import requests
import json

def test_registration():
    """Test the registration endpoint"""
    url = 'http://127.0.0.1:8000/api/auth/register/'
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'test123'
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            return True
        else:
            print("❌ Registration failed")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Registration Endpoint")
    print("=" * 40)
    test_registration()
