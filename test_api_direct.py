"""
Tiesioginis Django API testavimas
"""

import requests
import json

# Testuojame autentifikaciją
login_data = {
    "username": "test@example.com",
    "password": "test123"
}

try:
    response = requests.post("http://127.0.0.1:8000/api/auth/token/", json=login_data)
    print(f"Auth status: {response.status_code}")
    print(f"Auth response: {response.text}")
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data.get('access')
        
        # Testuojame leads endpoint
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        leads_response = requests.get("http://127.0.0.1:8000/api/leads/?limit=5", headers=headers)
        print(f"\nLeads status: {leads_response.status_code}")
        print(f"Leads response: {json.dumps(leads_response.json(), indent=2)}")
        
        # Testuojame dashboard
        dashboard_response = requests.get("http://127.0.0.1:8000/api/dashboard/summary/", headers=headers)
        print(f"\nDashboard status: {dashboard_response.status_code}")
        print(f"Dashboard response: {json.dumps(dashboard_response.json(), indent=2)}")
        
    else:
        print("Auth failed")
        
except Exception as e:
    print(f"Error: {e}")
