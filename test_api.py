"""
API testavimo skriptas Django REST Framework integracijai patikrinti
"""

import json
import requests
from datetime import date, timedelta

# API testavimo konfigūracija
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

def test_api_endpoints():
    """
    Testuoti pagrindinius API endpoint'us
    """
    print("🧪 Pradedamas API testavimas...")
    
    # 1. Testuojame autentifikaciją
    print("\n1. 🔐 Testuojame autentifikaciją...")
    
    # Pirmiausia bandome be token
    response = requests.get(f"{API_BASE}/leads/")
    print(f"Be autentifikacijos: {response.status_code} - {response.text[:100]}")
    
    # Bandom prisijungti (jeigu egzistuoja testinis vartotojas)
    login_data = {
        "username": "test@example.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/token/", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access')
            refresh_token = token_data.get('refresh')
            print("✅ Sėkmingai gauti JWT tokenai")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # 2. Testuojame lead'ų endpoint'us
            print("\n2. 📋 Testuojame lead'ų endpoint'us...")
            
            # Gauti lead'ų sąrašą
            response = requests.get(f"{API_BASE}/leads/", headers=headers)
            print(f"Lead'ų sąrašas: {response.status_code}")
            if response.status_code == 200:
                leads = response.json()
                print(f"Rasta lead'ų: {len(leads.get('results', leads))}")
                if leads.get('results', leads):
                    print(f"Pirmas lead: {leads.get('results', leads)[0].get('name', 'N/A')}")
            
            # Sukurti naują lead'ą
            print("\n3. ➕ Testuojame lead'o kūrimą...")
            new_lead_data = {
                "name": "API Test Lead",
                "company": "Test Company",
                "email": "api@test.com",
                "phone": "+37060000000",
                "status": "new",
                "budget": 5000.00,
                "notes": "Sukurtas per API testą"
            }
            
            response = requests.post(f"{API_BASE}/leads/", json=new_lead_data, headers=headers)
            print(f"Lead'o kūrimas: {response.status_code}")
            
            if response.status_code == 201:
                created_lead = response.json()
                lead_id = created_lead['id']
                print(f"✅ Lead'as sukurtas su ID: {lead_id}")
                
                # 4. Testuojame lead'o atnaujinimą
                print("\n4. 🔄 Testuojame lead'o statuso atnaujinimą...")
                
                status_update = {"status": "contacted"}
                response = requests.patch(
                    f"{API_BASE}/leads/{lead_id}/update_status/", 
                    json=status_update, 
                    headers=headers
                )
                print(f"Statuso atnaujinimas: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Statusas sėkmingai atnaujintas")
                
                # 5. Testuojame komentarų pridėjimą
                print("\n5. 💬 Testuojame komentaro pridėjimą...")
                
                comment_data = {
                    "body": "API test komentaras",
                    "kind": "note",
                    "author": "API Test"
                }
                
                response = requests.post(
                    f"{API_BASE}/leads/{lead_id}/add_comment/", 
                    json=comment_data, 
                    headers=headers
                )
                print(f"Komentaro pridėjimas: {response.status_code}")
                
                if response.status_code == 201:
                    print("✅ Komentaras sėkmingai pridėtas")
                
                # 6. Testuojame užduoties pridėjimą
                print("\n6. 📝 Testuojame užduoties pridėjimą...")
                
                task_data = {"title": "API test užduotis"}
                response = requests.post(
                    f"{API_BASE}/leads/{lead_id}/add_task/", 
                    json=task_data, 
                    headers=headers
                )
                print(f"Užduoties pridėjimas: {response.status_code}")
                
                if response.status_code == 201:
                    print("✅ Užduotis sėkmingai pridėta")
                
                # 7. Testuojame dashboard statistiką
                print("\n7. 📊 Testuojame dashboard statistiką...")
                
                response = requests.get(f"{API_BASE}/leads/dashboard_stats/", headers=headers)
                print(f"Dashboard statistika: {response.status_code}")
                
                if response.status_code == 200:
                    stats = response.json()
                    print(f"✅ Statistika gauta:")
                    print(f"   - Viso lead'ų: {stats.get('total_leads', 0)}")
                    print(f"   - Nauji lead'ai: {stats.get('new_leads', 0)}")
                    print(f"   - Šiandienos follow-up'ai: {stats.get('today_followups', 0)}")
                
                # 8. Testuojame follow-up'us
                print("\n8. ⏰ Testuojame follow-up'us...")
                
                response = requests.get(f"{API_BASE}/leads/upcoming_followups/?days=7", headers=headers)
                print(f"Artėjantys follow-up'ai: {response.status_code}")
                
                response = requests.get(f"{API_BASE}/leads/overdue_followups/", headers=headers)
                print(f"Vėluojantys follow-up'ai: {response.status_code}")
                
            else:
                print(f"❌ Lead'o kūrimas nepavyko: {response.text}")
                
        else:
            print(f"❌ Prisijungimas nepavyko: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Klaida testuojant: {e}")
    
    print("\n🏁 API testavimas baigtas!")

def test_mcp_integration():
    """
    Testuoti MCP integraciją
    """
    print("\n🤖 Testuojame MCP integraciją...")
    
    try:
        from crm.mcp_tools import CRMIntegration
        import asyncio
        
        async def test_mcp():
            # Sukuriam CRM integraciją
            crm = CRMIntegration()
            
            # Testuojame lead'ų gavimą
            leads = await crm.list_leads(limit=5)
            print(f"✅ MCP gavo {len(leads)} lead'ų")
            
            # Testuojame dashboard statistiką
            stats = await crm.get_dashboard_stats()
            if stats:
                print(f"✅ MCP gavo statistiką: {stats.get('total_leads', 0)} lead'ų")
            
            await crm.close()
        
        asyncio.run(test_mcp())
        
    except ImportError:
        print("❌ MCP moduliai nepasiekiami (reikia įdiegti aiohttp)")
    except Exception as e:
        print(f"❌ MCP testavimo klaida: {e}")

if __name__ == "__main__":
    # Patikriname ar serveris veikia
    try:
        response = requests.get(f"{BASE_URL}/admin/")
        if response.status_code == 200:
            print("✅ Django serveris veikia")
        else:
            print("❌ Django serveris neatsako")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Nepavyko prisijungti prie Django serverio")
        print("📝 Paleisk serverį: python manage.py runserver")
        exit(1)
    
    # Vykdom testus
    test_api_endpoints()
    test_mcp_integration()
