"""
MCP serverio demonstracija su autentifikacija
"""

import asyncio
import json
import aiohttp
from crm.mcp_tools import CRMIntegration, MCP_FUNCTIONS

async def get_jwt_token():
    """Gauti JWT tokeną testiniam vartotojui"""
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

async def demo_mcp_with_auth():
    """
    Demonstracija MCP su autentifikacija
    """
    print("🔐 MCP Demo su autentifikacija")
    print("=" * 40)
    
    # Gauname JWT tokeną
    print("📤 Gauname JWT tokeną...")
    token = await get_jwt_token()
    
    if not token:
        print("❌ Nepavyko gauti JWT tokeno")
        return
    
    print("✅ JWT tokenas gautas")
    
    # Sukuriam CRM integraciją su token
    crm = CRMIntegration(base_url="http://127.0.0.1:8000", api_token=token)
    
    try:
        # 1. Dashboard statistika
        print("\n📊 Dashboard statistika:")
        stats = await crm.get_dashboard_stats()
        if stats:
            print(f"   Viso lead'ų: {stats.get('total_leads', 0)}")
            print(f"   Nauji lead'ai: {stats.get('new_leads', 0)}")
            print(f"   Šiandienos follow-up'ai: {stats.get('today_followups', 0)}")
        
        # 2. Lead'ų sąrašas
        print("\n📋 Lead'ų sąrašas:")
        leads = await crm.list_leads(limit=5)
        if leads:
            for i, lead in enumerate(leads[:3], 1):
                print(f"   {i}. {lead.get('name')} - {lead.get('status_display')}")
        
        # 3. Sukurti naują lead'ą
        print("\n➕ Kuriamas naujas lead'as:")
        new_lead = await crm.create_lead({
            'name': 'MCP Auth Demo Lead',
            'company': 'Demo Company',
            'email': 'auth@demo.com',
            'status': 'new',
            'budget': 5000.0
        })
        
        if new_lead:
            lead_id = new_lead['id']
            print(f"   ✅ Lead'as sukurtas: ID {lead_id}")
            
            # 4. Pridėti komentarą
            comment = await crm.add_comment(
                lead_id=lead_id,
                body="Komentaras per MCP su autentifikacija",
                kind="note",
                author="MCP Auth Demo"
            )
            
            if comment:
                print(f"   ✅ Komentaras pridėtas")
        
        print("\n🎉 MCP su autentifikacija sėkmingai veikia!")
        
    except Exception as e:
        print(f"❌ Klaida: {e}")
    
    finally:
        await crm.close()

if __name__ == "__main__":
    asyncio.run(demo_mcp_with_auth())
