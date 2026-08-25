"""
MCP serverio demonstracija - parodyta, kaip Skybridge gali naudoti CRM API
"""

import asyncio
import json
from crm.mcp_tools import CRMIntegration, MCP_FUNCTIONS, MCP_FUNCTION_DESCRIPTIONS

async def demo_mcp_integration():
    """
    Demonstracija MCP integracijos su Django CRM
    """
    print("🤖 MCP Server Demo - Freelancer CRM Integration")
    print("=" * 50)
    
    # Sukuriam CRM integraciją
    crm = CRMIntegration(base_url="http://127.0.0.1:8000")
    
    try:
        # 1. Gauti dashboard statistiką
        print("\n📊 1. Dashboard statistika:")
        stats = await crm.get_dashboard_stats()
        if stats:
            print(f"   Viso lead'ų: {stats.get('total_leads', 0)}")
            print(f"   Nauji lead'ai: {stats.get('new_leads', 0)}")
            print(f"   Šiandienos follow-up'ai: {stats.get('today_followups', 0)}")
            print(f"   Biudžetas: €{stats.get('total_budget', 0):.2f}")
        else:
            print("   ⚠️  Nepavyko gauti statistikos")
        
        # 2. Gauti lead'ų sąrašą
        print("\n📋 2. Lead'ų sąrašas:")
        leads = await crm.list_leads(limit=5)
        if leads:
            for i, lead in enumerate(leads[:3], 1):
                print(f"   {i}. {lead.get('name', 'N/A')} - {lead.get('status_display', 'N/A')}")
                print(f"      📧 {lead.get('email', 'N/A')}")
                print(f"      💰 €{lead.get('budget', 0):.2f}")
        else:
            print("   Lead'ų nerasta")
        
        # 3. Sukurti naują lead'ą (demo)
        print("\n➕ 3. Kuriamas naujas lead'as:")
        new_lead_data = {
            'name': 'Demo Lead from MCP',
            'company': 'Demo Company',
            'email': 'demo@mcp.com',
            'phone': '+37060000000',
            'status': 'new',
            'budget': 10000.0,
            'notes': 'Sukurtas per MCP serverio demonstraciją'
        }
        
        new_lead = await crm.create_lead(new_lead_data)
        if new_lead:
            lead_id = new_lead['id']
            print(f"   ✅ Lead'as sukurtas su ID: {lead_id}")
            print(f"   📝 Pavadinimas: {new_lead.get('name')}")
            
            # 4. Pridėti komentarą
            print("\n💬 4. Pridedamas komentaras:")
            comment = await crm.add_comment(
                lead_id=lead_id,
                body="Šis komentaras buvo pridėtas per MCP serverį",
                kind="note",
                author="MCP Demo"
            )
            if comment:
                print(f"   ✅ Komentaras pridėtas: {comment.get('body', '')[:50]}...")
            
            # 5. Pridėti užduotį
            print("\n📝 5. Pridedama užduotis:")
            task = await crm.add_task(
                lead_id=lead_id,
                title="Susisiekti su klientu per MCP"
            )
            if task:
                print(f"   ✅ Užduotis pridėta: {task.get('title')}")
            
            # 6. Atnaujinti statusą
            print("\n🔄 6. Atnaujinamas statusas:")
            updated_lead = await crm.update_lead_status(lead_id, 'contacted')
            if updated_lead:
                print(f"   ✅ Statusas pakeistas į: {updated_lead.get('status_display')}")
            
            # 7. Gauti lead'o veiksmų istoriją
            print("\n📊 7. Lead'o veiksmų istorija:")
            activities = await crm.get_lead_activities(lead_id)
            if activities:
                for activity in activities[:3]:
                    print(f"   • {activity.get('action', 'N/A')}: {activity.get('details', 'N/A')[:50]}...")
        
        # 8. Gauti artėjančius follow-up'us
        print("\n⏰ 8. Artėjantys follow-up'ai:")
        upcoming = await crm.get_upcoming_followups(days=7)
        if upcoming:
            print(f"   Rasta {len(upcoming)} artėjančių follow-up'ų")
            for followup in upcoming[:2]:
                print(f"   • {followup.get('name')} - {followup.get('next_follow_up', 'N/A')}")
        else:
            print("   Artėjančių follow-up'ų nerasta")
        
        print("\n🎉 MCP Demo sėkmingai baigta!")
        print("\n📋 Galimi MCP įrankiai:")
        for tool_name, description in MCP_FUNCTION_DESCRIPTIONS.items():
            print(f"   • {tool_name}: {description}")
            
    except Exception as e:
        print(f"❌ Klaida demonstracijoje: {e}")
    
    finally:
        await crm.close()

async def demo_mcp_server_simulation():
    """
    Simuliuojame MCP serverio veikimą su realia užklausa
    """
    print("\n🚀 MCP Server Simulation")
    print("=" * 30)
    
    # Simuliuojame MCP užklausą
    mcp_request = {
        'method': 'tools/call',
        'params': {
            'name': 'list_leads',
            'arguments': {
                'status': 'new',
                'limit': 3
            }
        }
    }
    
    print(f"📨 MCP užklausa: {json.dumps(mcp_request, indent=2)}")
    
    # Simuliuojame MCP serverio atsakymą
    crm = CRMIntegration()
    try:
        # Iškviečiame funkciją
        tool_name = mcp_request['params']['name']
        arguments = mcp_request['params']['arguments']
        
        if tool_name in MCP_FUNCTIONS:
            result = await MCP_FUNCTIONS[tool_name](crm, arguments)
            
            mcp_response = {
                'content': [
                    {
                        'type': 'text',
                        'text': json.dumps(result, indent=2, ensure_ascii=False)
                    }
                ]
            }
            
            print(f"📤 MCP atsakymas:")
            print(json.dumps(mcp_response, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Įrankis {tool_name} nerastas")
            
    except Exception as e:
        print(f"❌ MCP serverio klaida: {e}")
    
    finally:
        await crm.close()

if __name__ == "__main__":
    print("🎯 Pradedama MCP integracijos demonstracija")
    print("Django serveris turi būti paleistas: python manage.py runserver")
    print()
    
    # Vykdom demonstraciją
    asyncio.run(demo_mcp_integration())
    asyncio.run(demo_mcp_server_simulation())
