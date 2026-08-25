"""
MCP Server v2 testavimo skriptas
"""

import asyncio
import json
import os
import sys
import time
import aiohttp
from datetime import timedelta

# Pridedame CRM katalogą prie Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'crm'))

from crm.mcp_tools import CRMIntegration, MCP_FUNCTIONS, MCP_FUNCTION_DESCRIPTIONS

# Konfigūracija
DEV_MODE = os.getenv('DEV_MODE', 'true').lower() == 'true'

class AuditLogger:
    """Audit log sistema"""
    
    def __init__(self):
        self.logs = []
    
    def log_request(self, tool_name: str, arguments: dict, user_id: str = None):
        log_entry = {
            'timestamp': time.time(),
            'tool': tool_name,
            'arguments': arguments,
            'user_id': user_id,
            'type': 'request'
        }
        self.logs.append(log_entry)
        print(f"AUDIT REQUEST: {json.dumps(log_entry, indent=2)}")
    
    def log_response(self, tool_name: str, success: bool, result: any = None, error: any = None):
        log_entry = {
            'timestamp': time.time(),
            'tool': tool_name,
            'success': success,
            'result': result if success else None,
            'error': str(error) if error else None,
            'type': 'response'
        }
        self.logs.append(log_entry)
        print(f"AUDIT RESPONSE: {json.dumps(log_entry, indent=2)}")

class MCPServerV2:
    """MCP Server v2 implementacija"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000", api_token: str = None, user_id: str = None):
        self.crm = CRMIntegration(base_url=base_url, api_token=api_token, user_id=user_id)
        self.tools = MCP_FUNCTIONS
        self.descriptions = MCP_FUNCTION_DESCRIPTIONS
        self.audit_logger = AuditLogger()
        self.start_time = time.time()
        self.current_user_id = user_id
    
    async def handle_request(self, request: dict) -> dict:
        """Apdoroti MCP užklausą su struktūruotais atsakymais"""
        try:
            method = request.get('method')
            params = request.get('params', {})
            
            if method == 'tools/list':
                return await self.list_tools()
            elif method == 'tools/call':
                return await self.call_tool(params)
            elif method == 'initialize':
                return await self.initialize(params)
            else:
                return self._error_response('METHOD_NOT_FOUND', f'Method {method} not found')
                
        except Exception as e:
            print(f"Klaida apdorojant užklausą: {e}")
            return self._error_response('INTERNAL_ERROR', str(e))
    
    async def initialize(self, params: dict) -> dict:
        """Incializuoti MCP serverį"""
        print("MCP Server v2 inicializuojamas")
        print(f"DEV_MODE: {DEV_MODE}")
        
        return {
            'protocolVersion': '2024-11-05',
            'capabilities': {
                'tools': {
                    'structuredOutputs': True,
                    'errorHandling': True
                }
            },
            'serverInfo': {
                'name': 'Freelancer CRM MCP Server v2',
                'version': '2.0.0',
                'devMode': DEV_MODE
            }
        }
    
    async def list_tools(self) -> dict:
        """Grąžinti prieinamų įrankių sąrašą"""
        tools = []
        for tool_name, description in self.descriptions.items():
            tools.append({
                'name': tool_name,
                'description': description,
                'inputSchema': self.get_tool_schema(tool_name)
            })
        
        return {
            'tools': tools,
            'success': True
        }
    
    def get_tool_schema(self, tool_name: str) -> dict:
        """Gauti įrankio schemą"""
        schemas = {
            'list_leads': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'enum': ['new', 'contacted', 'proposal', 'won', 'lost']},
                    'search': {'type': 'string'},
                    'limit': {'type': 'integer', 'default': 50},
                    'view': {'type': 'string', 'enum': ['compact', 'detailed'], 'default': 'detailed'}
                }
            },
            'create_lead': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'company': {'type': 'string'},
                    'email': {'type': 'string', 'format': 'email'},
                    'status': {'type': 'string', 'enum': ['new', 'contacted', 'proposal', 'won', 'lost'], 'default': 'new'},
                    'budget': {'type': 'number'}
                },
                'required': ['name']
            }
        }
        return schemas.get(tool_name, {'type': 'object'})
    
    async def call_tool(self, params: dict) -> dict:
        """Iškviesti MCP įrankį su struktūruotu atsakymu"""
        try:
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            if tool_name not in self.tools:
                return self._error_response('TOOL_NOT_FOUND', f'Tool {tool_name} not found')
            
            print(f'Kviečiamas įrankis: {tool_name} su argumentais: {arguments}')
            
            # Audit log - request
            self.audit_logger.log_request(tool_name, arguments, self.current_user_id)
            
            # Iškviečiame funkciją
            start_time = time.time()
            result = await self.tools[tool_name](self.crm, arguments)
            execution_time = time.time() - start_time
            
            # Audit log - response
            self.audit_logger.log_response(tool_name, True, result)
            
            # Struktūruotas atsakymas
            response = {
                'success': True,
                'data': result,
                'metadata': {
                    'tool': tool_name,
                    'executionTime': round(execution_time, 3),
                    'timestamp': time.time()
                }
            }
            
            print(f'Įrankis {tool_name} sėkmingai įvykdytas per {execution_time:.3f}s')
            return response
            
        except Exception as e:
            print(f"Klaida iškviečiant įrankį: {e}")
            self.audit_logger.log_response(tool_name, False, error=e)
            return self._error_response('EXECUTION_ERROR', str(e), {
                'tool': tool_name,
                'arguments': arguments
            })
    
    def _error_response(self, code: str, message: str, details: dict = None) -> dict:
        """Sukurti vieningą error atsakymą"""
        return {
            'success': False,
            'error': {
                'code': code,
                'message': message,
                'details': details or {}
            },
            'timestamp': time.time()
        }
    
    async def close(self):
        """Uždaryti MCP serverį"""
        await self.crm.close()
        print("MCP Server v2 uždarytas")

async def get_jwt_token():
    """Gauti JWT tokeną"""
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

async def run_dev_tests(server: MCPServerV2):
    """Vykdyti development testus"""
    print("🧪 DEV_MODE: Vykdomi MCP v2 testai...")
    
    # Test 1: list_leads
    print("\n1️⃣ Testuojame list_leads...")
    list_request = {
        'method': 'tools/call',
        'params': {
            'name': 'list_leads',
            'arguments': {'limit': 3}
        }
    }
    
    response = await server.handle_request(list_request)
    if response.get('success'):
        leads = response.get('data', [])
        metadata = response.get('metadata', {})
        print(f"✅ Gauta {len(leads)} lead'ų")
        print(f"   Execution time: {metadata.get('executionTime', 0)}s")
        if leads:
            print(f"   Pirmas lead: {leads[0].get('name', 'N/A')}")
    else:
        error = response.get('error', {})
        print(f"❌ Klaida: {error.get('message', 'Unknown')}")
    
    # Test 2: create_lead
    print("\n2️⃣ Testuojame create_lead...")
    create_request = {
        'method': 'tools/call',
        'params': {
            'name': 'create_lead',
            'arguments': {
                'name': 'DEV Test Lead v2',
                'company': 'Test Company',
                'email': 'dev@test.com',
                'status': 'new',
                'budget': 7500.0
            }
        }
    }
    
    response = await server.handle_request(create_request)
    if response.get('success'):
        lead_data = response.get('data', {})
        metadata = response.get('metadata', {})
        print(f"✅ Lead'as sukurtas")
        print(f"   Execution time: {metadata.get('executionTime', 0)}s")
        if isinstance(lead_data, dict) and 'id' in lead_data:
            print(f"   ID: {lead_data['id']}")
        else:
            print(f"   Atsakymas: {json.dumps(lead_data, indent=2)}")
    else:
        error = response.get('error', {})
        print(f"❌ Klaida: {error.get('message', 'Unknown')}")
    
    # Test 3: get_dashboard_summary
    print("\n3️⃣ Testuojame get_dashboard_summary...")
    dashboard_request = {
        'method': 'tools/call',
        'params': {
            'name': 'get_dashboard_summary',
            'arguments': {}
        }
    }
    
    response = await server.handle_request(dashboard_request)
    if response.get('success'):
        stats = response.get('data', {})
        metadata = response.get('metadata', {})
        print(f"✅ Statistika gauta")
        print(f"   Execution time: {metadata.get('executionTime', 0)}s")
        if isinstance(stats, dict):
            total_leads = stats.get('total_leads', 0)
            print(f"   Lead'ų skaičius: {total_leads}")
        else:
            print(f"   Atsakymas: {json.dumps(stats, indent=2)}")
    else:
        error = response.get('error', {})
        print(f"❌ Klaida: {error.get('message', 'Unknown')}")
    
    # Test 4: error handling
    print("\n4️⃣ Testuojame error handling...")
    error_request = {
        'method': 'tools/call',
        'params': {
            'name': 'nonexistent_tool',
            'arguments': {}
        }
    }
    
    response = await server.handle_request(error_request)
    if not response.get('success'):
        error = response.get('error', {})
        print(f"✅ Error handling veikia")
        print(f"   Code: {error.get('code')}")
        print(f"   Message: {error.get('message')}")
    else:
        print("❌ Error handling neveikia")
    
    # Test 5: tools/list
    print("\n5️⃣ Testuojame tools/list...")
    tools_request = {
        'method': 'tools/list',
        'params': {}
    }
    
    response = await server.handle_request(tools_request)
    if response.get('success'):
        tools = response.get('tools', [])
        print(f"✅ Gauta {len(tools)} įrankių")
        for tool in tools[:3]:  # Rodyti tik pirmus 3
            print(f"   - {tool.get('name')}: {tool.get('description', 'N/A')}")
    else:
        error = response.get('error', {})
        print(f"❌ Klaida: {error.get('message', 'Unknown')}")
    
    # Test 6: list_leads compact režimas
    print("\n6️⃣ Testuojame list_leads compact režimą...")
    compact_request = {
        'method': 'tools/call',
        'params': {
            'name': 'list_leads',
            'arguments': {'limit': 3, 'view': 'compact'}
        }
    }
    
    response = await server.handle_request(compact_request)
    if response.get('success'):
        leads = response.get('data', [])
        metadata = response.get('metadata', {})
        print(f"✅ Compact režimas: {len(leads)} lead'ų")
        print(f"   Execution time: {metadata.get('executionTime', 0)}s")
        if leads:
            first_lead = leads[0]
            print(f"   Pirmas lead (compact): {first_lead.get('name')} - ID: {first_lead.get('id')}")
            print(f"   Laukai: {list(first_lead.keys())}")
    else:
        error = response.get('error', {})
        print(f"❌ Klaida: {error.get('message', 'Unknown')}")
    
    print("\n🎉 MCP Server v2 testai sėkmingai baigti!")

async def run_mcp_server_v2():
    """Paleisti MCP serverį v2"""
    print("🚀 Paleidžiame MCP Server v2...")
    print(f"🔧 DEV_MODE: {DEV_MODE}")
    
    # Gauname JWT tokeną
    token = await get_jwt_token()
    
    if not token:
        print("❌ Nepavyko gauti JWT tokeno")
        return
    
    print("✅ JWT tokenas gautas")
    
    # Sukuriam MCP serverį su user_id
    server = MCPServerV2(base_url="http://127.0.0.1:8000", api_token=token, user_id="test@example.com")
    
    try:
        if DEV_MODE:
            # DEV_MODE: paleidžiam testus
            await run_dev_tests(server)
        else:
            # Production mode: laukiame užklausų
            print("🔄 Production mode: laukiama MCP užklausų...")
            await asyncio.sleep(1)  # Simuliacija
            
    except Exception as e:
        print(f"Klaida paleidžiant MCP serverį: {e}")
    
    finally:
        await server.close()

if __name__ == "__main__":
    print("🎯 MCP Server v2 - Patobulinta Skybridge Integration")
    print("=" * 60)
    print("Django serveris turi būti paleistas: python manage.py runserver")
    print(f"DEV_MODE: {DEV_MODE} (naudokite 'set DEV_MODE=false' production režimui)")
    print()
    
    asyncio.run(run_mcp_server_v2())
