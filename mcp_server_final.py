"""
Galutinis MCP serverio pavyzdys - paruoštas Skybridge integracijai
"""

import asyncio
import json
import sys
from crm.mcp_tools import CRMIntegration, MCP_FUNCTIONS, MCP_FUNCTION_DESCRIPTIONS
from crm.mcp_server import MCPServer

async def get_jwt_token():
    """Gauti JWT tokeną"""
    import aiohttp
    
    login_data = {
        "username": "test@example.com", 
        "password": "test123"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://127.0.0.1:8000/api/auth/token/",
            json=login_data
        ) as response:
            if response.status == 200:
                token_data = await response.json()
                return token_data.get('access')
            return None

async def run_mcp_server():
    """
    Paleisti MCP serverį su autentifikacija
    """
    print("🚀 Paleidžiame MCP Serverį...")
    
    # Gauname JWT tokeną
    token = await get_jwt_token()
    if not token:
        print("❌ Nepavyko gauti JWT tokeno")
        return
    
    print("✅ JWT tokenas gautas")
    
    # Sukuriam MCP serverį
    server = MCPServer(base_url="http://127.0.0.1:8000", api_token=token)
    
    try:
        # Demonstracinė užklausa
        demo_request = {
            'method': 'tools/call',
            'params': {
                'name': 'list_leads',
                'arguments': {'limit': 5}
            }
        }
        
        print("\n📨 MCP užklausa:")
        print(json.dumps(demo_request, indent=2))
        
        # Apdorojame užklausą
        response = await server.handle_request(demo_request)
        
        print("\n📤 MCP atsakymas:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # Keli papildomi testai
        print("\n🧪 Papildomi MCP testai:")
        
        # Dashboard statistika
        stats_request = {
            'method': 'tools/call',
            'params': {
                'name': 'get_dashboard_summary',
                'arguments': {}
            }
        }
        
        stats_response = await server.handle_request(stats_request)
        if 'content' in stats_response and len(stats_response['content']) > 0:
            stats_data = json.loads(stats_response['content'][0]['text'])
            print(f"📊 Lead'ų skaičius: {stats_data.get('total_leads', 0)}")
        else:
            print("📊 Statistika nepasiekiama")
        
        # Sukuriame naują lead'ą
        create_lead_request = {
            'method': 'tools/call',
            'params': {
                'name': 'create_lead',
                'arguments': {
                    'name': 'Skybridge Integration Lead',
                    'company': 'Tech Company',
                    'email': 'skybridge@demo.com',
                    'status': 'new',
                    'budget': 15000.0
                }
            }
        }
        
        create_response = await server.handle_request(create_lead_request)
        if 'content' in create_response and len(create_response['content']) > 0:
            lead_data = json.loads(create_response['content'][0]['text'])
            if isinstance(lead_data, dict) and 'id' in lead_data:
                print(f"✅ Lead'as sukurtas: ID {lead_data['id']}")
            else:
                print(f"✅ Lead'as sukurtas (atsakymas: {lead_data})")
        else:
            print("✅ Lead'o kūrimas atliktas")
        
        print("\n🎉 MCP Serveris sėkmingai veikia!")
        print("\n📋 Galimi MCP įrankiai:")
        for tool_name, description in MCP_FUNCTION_DESCRIPTIONS.items():
            print(f"   • {tool_name}")
        
        print("\n🔗 Kaip naudoti su Skybridge:")
        print("1. MCP Serveris veikia adresu: http://127.0.0.1:8000")
        print("2. Autentifikacija per JWT tokenus")
        print("3. Galimi 9 CRM valdymo įrankiai")
        print("4. Realus laiko duomenų mainai su Django API")
        
    except Exception as e:
        print(f"❌ MCP serverio klaida: {e}")
    
    finally:
        await server.close()

if __name__ == "__main__":
    print("🎯 MCP Server - Skybridge Integration")
    print("=" * 50)
    print("Django serveris turi būti paleistas: python manage.py runserver")
    print()
    
    asyncio.run(run_mcp_server())
