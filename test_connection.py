#!/usr/bin/env python3
"""
Simple test script to verify frontend-backend connection
"""

import requests
import json

def test_backend_connection():
    """Test if backend is running and accessible"""
    try:
        response = requests.get('http://127.0.0.1:8000/api/auth/token/', timeout=5)
        print(f"✅ Backend is running (status: {response.status_code})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_frontend_connection():
    """Test if frontend is running and accessible"""
    try:
        response = requests.get('http://localhost:3000/', timeout=5)
        print(f"✅ Frontend is running (status: {response.status_code})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend connection failed: {e}")
        return False

def test_authentication():
    """Test authentication endpoint"""
    try:
        auth_data = {
            "username": "admin",
            "password": "dizain123"
        }
        response = requests.post(
            'http://127.0.0.1:8000/api/auth/token/',
            json=auth_data,
            timeout=5
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Authentication successful")
            print(f"   Access token received: {token_data.get('access', 'N/A')[:20]}...")
            return token_data.get('access')
        else:
            print(f"❌ Authentication failed (status: {response.status_code})")
            print(f"   Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication request failed: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing protected endpoint with token"""
    if not token:
        print("❌ No token provided, skipping protected endpoint test")
        return False
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(
            'http://127.0.0.1:8000/api/leads/',
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Protected endpoint accessible (status: {response.status_code})")
            data = response.json()
            print(f"   Found {data.get('count', 0)} leads")
            return True
        else:
            print(f"❌ Protected endpoint failed (status: {response.status_code})")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Protected endpoint request failed: {e}")
        return False

def main():
    print("🔍 Testing CRM Frontend-Backend Connection")
    print("=" * 50)
    
    # Test basic connectivity
    backend_ok = test_backend_connection()
    frontend_ok = test_frontend_connection()
    
    if not backend_ok:
        print("\n❌ Backend is not running. Please start Django server:")
        print("   python manage.py runserver")
        return
    
    if not frontend_ok:
        print("\n❌ Frontend is not running. Please start Vite dev server:")
        print("   npm run dev")
        return
    
    print("\n🔐 Testing authentication...")
    token = test_authentication()
    
    if token:
        print("\n🛡️ Testing protected endpoints...")
        test_protected_endpoint(token)
    
    print("\n📋 Summary:")
    print(f"   Backend: {'✅' if backend_ok else '❌'}")
    print(f"   Frontend: {'✅' if frontend_ok else '❌'}")
    print(f"   Auth: {'✅' if token else '❌'}")
    
    if backend_ok and frontend_ok and token:
        print("\n🎉 All systems are ready! You can now:")
        print("   1. Open http://localhost:3000/ in your browser")
        print("   2. Login with username: admin, password: dizain123")
        print("   3. Test the CRM functionality")

if __name__ == "__main__":
    main()
