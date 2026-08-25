"""
Hibridinio sprendimo testavimo skriptas
Testuoja Django API + MCP Bridge + Skybridge integraciją
"""

import asyncio
import json
import sys
from crm.mcp_bridge import MCPBridge
from crm.mcp_server import MCPServer

async def test_django_api_connection():
    """Testuoti Django API prisijungimą"""
    print("🔗 Testuojame Django API prisijungimą...")
    
    bridge = MCPBridge("http://127.0.0.1:8000")
    
    # Testuojame autentifikaciją
    success = await bridge.authenticate("test@example.com", "test123")
    if success:
        print("✅ Autentifikacija sėkminga")
        return bridge
    else:
        print("❌ Autentifikacija nepavyko")
        return None

async def test_mcp_server(bridge):
    """Testuoti MCP serverio funkcionalumą"""
    print("\n🚀 Testuojame MCP serverį...")
    
    server = MCPServer(base_url="http://127.0.0.1:8000", api_token=bridge.api_token)
    
    # Testuojame įrankių sąrašą
    list_request = {
        'method': 'tools/list',
        'params': {}
    }
    
    response = await server.handle_request(list_request)
    if 'tools' in response:
        print(f"✅ MCP serveris veikia. Rasti {len(response['tools'])} įrankiai:")
        for tool in response['tools']:
            print(f"   • {tool['name']}: {tool['description']}")
        return server
    else:
        print("❌ MCP serverio klaida")
        return None

async def test_dashboard_stats(server):
    """Testuoti dashboard statistiką"""
    print("\n📊 Testuojame dashboard statistiką...")
    
    dashboard_request = {
        'method': 'tools/call',
        'params': {
            'name': 'get_dashboard',
            'arguments': {}
        }
    }
    
    response = await server.handle_request(dashboard_request)
    if 'content' in response:
        stats_data = json.loads(response['content'][0]['text'])
        if 'data' in stats_data:
            stats = stats_data['data']
            print("✅ Dashboard statistika gauta:")
            print(f"   • Visi lead'ai: {stats.get('total_leads', 0)}")
            print(f"   • Nauji: {stats.get('new_leads', 0)}")
            print(f"   • Laimėti: {stats.get('won_leads', 0)}")
            print(f"   • Biudžetas: €{stats.get('total_budget', 0)}")
            return True
        else:
            print("❌ Neteisingas statistikos formatas")
            return False
    else:
        print("❌ Nepavyko gauti dashboard statistikos")
        return False

async def test_leads_operations(server):
    """Testuoti lead'ų operacijas"""
    print("\n📋 Testuojame lead'ų operacijas...")
    
    # 1. Gauti lead'ų sąrašą
    list_request = {
        'method': 'tools/call',
        'params': {
            'name': 'list_leads',
            'arguments': {'limit': 5}
        }
    }
    
    response = await server.handle_request(list_request)
    if 'content' in response:
        leads_data = json.loads(response['content'][0]['text'])
        if 'data' in leads_data:
            leads = leads_data['data']
            print(f"✅ Gauti {len(leads)} lead'ai")
            
            if leads:
                # 2. Gauti pirmo lead'o detales
                first_lead = leads[0]
                detail_request = {
                    'method': 'tools/call',
                    'params': {
                        'name': 'get_lead',
                        'arguments': {'lead_id': first_lead['id']}
                    }
                }
                
                detail_response = await server.handle_request(detail_request)
                if 'content' in detail_response:
                    detail_data = json.loads(detail_response['content'][0]['text'])
                    if 'data' in detail_data:
                        lead_detail = detail_data['data']
                        print(f"✅ Lead'o detalės gautos: {lead_detail['name']}")
                        
                        # 3. Sukurti komentarą
                        comment_request = {
                            'method': 'tools/call',
                            'params': {
                                'name': 'create_comment',
                                'arguments': {
                                    'lead_id': first_lead['id'],
                                    'body': 'Testinis komentras iš MCP',
                                    'kind': 'note',
                                    'author': 'MCP Test'
                                }
                            }
                        }
                        
                        comment_response = await server.handle_request(comment_request)
                        if 'content' in comment_response:
                            print("✅ Komentaras sėkmingai sukurtas")
                            return True
                        else:
                            print("❌ Nepavyko sukurti komentaro")
                            return False
                    else:
                        print("❌ Neteisingas lead'o detalių formatas")
                        return False
                else:
                    print("❌ Nepavyko gauti lead'o detalių")
                    return False
            else:
                print("⚠️  Lead'ų nėra, testuojame naujo lead'o kūrimą...")
                
                # Sukuriam testinį lead'ą
                create_request = {
                    'method': 'tools/call',
                    'params': {
                        'name': 'create_lead',
                        'arguments': {
                            'name': 'MCP Test Lead',
                            'company': 'Test Company',
                            'email': 'mcp@test.com',
                            'status': 'new',
                            'budget': 5000
                        }
                    }
                }
                
                create_response = await server.handle_request(create_request)
                if 'content' in create_response:
                    create_data = json.loads(create_response['content'][0]['text'])
                    if 'data' in create_data:
                        new_lead = create_data['data']
                        print(f"✅ Testinis lead'as sukurtas: {new_lead['name']}")
                        return True
                    else:
                        print("❌ Neteisingas lead'o kūrimo formatas")
                        return False
                else:
                    print("❌ Nepavyko sukurti lead'o")
                    return False
        else:
            print("❌ Neteisingas lead'ų sąrašo formatas")
            return False
    else:
        print("❌ Nepavyko gauti lead'ų sąrašo")
        return False

async def test_skybridge_app():
    """Testuoti Skybridge app struktūrą"""
    print("\n🌉 Testuojame Skybridge app struktūrą...")
    
    import os
    skybridge_path = "c:/Users/ACER/Desktop/Django-CRM/skybridge_crm"
    
    required_files = [
        "package.json",
        "index.ts",
        "crm-bridge.ts",
        "tsconfig.json",
        "views/DashboardView.tsx",
        "views/LeadListView.tsx",
        "views/LeadDetailView.tsx"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(skybridge_path, file_path.replace('/', os.sep))
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if not missing_files:
        print("✅ Visi Skybridge failai sukurti")
        print("   • package.json - Skybridge app konfigūracija")
        print("   • index.ts - Pagrindinis MCP serveris")
        print("   • crm-bridge.ts - Django API jungtis")
        print("   • React Views - UI komponentai")
        return True
    else:
        print(f"❌ Trūkstami failai: {', '.join(missing_files)}")
        return False

async def main():
    """Pagrindinė testavimo funkcija"""
    print("🎯 Hibridinio CRM sprendimo testavimas")
    print("=" * 50)
    
    # Testuojame Skybridge app struktūrą
    skybridge_ok = await test_skybridge_app()
    
    if not skybridge_ok:
        print("\n❌ Skybridge app struktūra nebaigta. Sustabdom testavimą.")
        return
    
    print("\n" + "=" * 50)
    print("🔧 Django API + MCP Bridge testavimas")
    print("=" * 50)
    
    # Testuojame Django API prisijungimą
    bridge = await test_django_api_connection()
    if not bridge:
        print("\n❌ Nepavyko prisijungti prie Django API. Patikrinkite:")
        print("   • Django serveris veikia (python manage.py runserver)")
        print("   • Testinis vartotojas egzistuoja")
        print("   • API endpoint'ai prieinami")
        return
    
    # Testuojame MCP serverį
    server = await test_mcp_server(bridge)
    if not server:
        print("\n❌ MCP serveris neveikia")
        return
    
    # Testuojame funkcionalumą
    tests = [
        ("Dashboard statistika", test_dashboard_stats),
        ("Lead'ų operacijos", test_leads_operations),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func(server)
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} klaida: {e}")
            results.append((test_name, False))
    
    # Uždaryti serverį
    await server.close()
    await bridge.__aexit__(None, None, None)
    
    # Rezultatų suvestinė
    print("\n" + "=" * 50)
    print("📊 TESTAVIMO REZULTATAI")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ Sėkminga" if result else "❌ Nepavyko"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\nSkybridge app: {'✅ Baigta' if skybridge_ok else '❌ Nebaigta'}")
    
    if all_passed and skybridge_ok:
        print("\n🎉 VISI TESTAI SĖKMINGI!")
        print("\n📋 KITI ŽINGSNIAI:")
        print("1. Įdiekite Skybridge dependencies:")
        print("   cd skybridge_crm && npm install")
        print("2. Paleiskite Skybridge development serverį:")
        print("   npm run dev")
        print("3. Testuokite su ChatGPT arba Claude")
        print("\n🔗 Hibridinis sprendimas paruoštas!")
    else:
        print("\n⚠️  Kai kurie testai nepavyko. Patikrinkite klaidas ir pataisykite.")

if __name__ == "__main__":
    print("Įsitikinkite, kad Django serveris veikia:")
    print("python manage.py runserver")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Testavimas nutrauktas")
    except Exception as e:
        print(f"\n❌ Nepageidaujama klaida: {e}")
        sys.exit(1)
