#!/usr/bin/env python3
"""
Tiesioginis Django API testavimas
"""

import requests
import json

def test_api():
    base_url = "http://127.0.0.1:8000"
    
    # 1. Autentifikacija
    print("1. Autentifikacija...")
    auth_data = {
        "username": "test@example.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/token/", json=auth_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data['access']
            print(f"✅ Token gautas")
        else:
            print(f"❌ Autentifikacija nepavyko: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Autentifikacijos klaida: {e}")
        return
    
    # 2. Lead'ų gavimas
    print("\n2. Lead'ų gavimas...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{base_url}/api/leads/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Lead'ai gauti")
            print(f"   Atsakymo tipas: {type(data)}")
            print(f"   Raktai: {list(data.keys())}")
            
            if 'results' in data:
                leads = data['results']
                print(f"   Lead'ų skaičius (paginavimas): {len(leads)}")
                print(f"   Bendras skaičius: {data.get('count', 'N/A')}")
            else:
                leads = data
                print(f"   Lead'ų skaičius (tiesioginis): {len(leads)}")
            
            print(f"   Pirmi 3 lead'ai:")
            for i, lead in enumerate(leads[:3]):
                print(f"     {i+1}. {lead.get('name', 'N/A')} - {lead.get('company', 'N/A')}")
                
        else:
            print(f"❌ Lead'ų gavimas nepavyko: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Lead'ų gavimo klaida: {e}")

if __name__ == "__main__":
    print("🔍 Django API tiesioginis testavimas")
    print("=" * 50)
    test_api()
