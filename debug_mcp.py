"""
MCP serverio debuginimas
"""

import asyncio
import json
from crm.mcp_bridge import MCPBridge
from crm.mcp_server import MCPServer

async def debug_mcp():
    """Debuginimo funkcija"""
    print("🔧 MCP Debug")
    
    # Prisijungiame
    bridge = MCPBridge("http://127.0.0.1:8000")
    success = await bridge.authenticate("test@example.com", "test123")
    
    if not success:
        print("❌ Autentifikacija nepavyko")
        return
    
    print("✅ Autentifikacija sėkminga")
    
    # Testuojame tiesiogiai MCPBridge
    print("\n🌉 MCPBridge testas:")
    
    # Dashboard
    dashboard_result = await bridge.get_dashboard_summary()
    print(f"Dashboard: {json.dumps(dashboard_result, indent=2)}")
    
    # Leads
    leads_result = await bridge.get_leads(limit=5)
    print(f"\nLeads: {json.dumps(leads_result, indent=2)}")
    
    # MCP Server testas
    print("\n🚀 MCP Server testas:")
    server = MCPServer(base_url="http://127.0.0.1:8000", api_token=bridge.api_token)
    
    # Dashboard request
    dashboard_request = {
        'method': 'tools/call',
        'params': {
            'name': 'get_dashboard',
            'arguments': {}
        }
    }
    
    dashboard_response = await server.handle_request(dashboard_request)
    print(f"MCP Dashboard: {json.dumps(dashboard_response, indent=2)}")
    
    # Leads request
    leads_request = {
        'method': 'tools/call',
        'params': {
            'name': 'list_leads',
            'arguments': {'limit': 5}
        }
    }
    
    leads_response = await server.handle_request(leads_request)
    print(f"\nMCP Leads: {json.dumps(leads_response, indent=2)}")
    
    await server.close()
    await bridge.__aexit__(None, None, None)

if __name__ == "__main__":
    asyncio.run(debug_mcp())
