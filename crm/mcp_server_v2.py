"""
MCP Server v2 - Patobulinta implementacija su struktūruotais atsakymais
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, Any, List, Optional
from .mcp_tools import CRMIntegration, MCP_FUNCTIONS, MCP_FUNCTION_DESCRIPTIONS

# Nustatome logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigūracija
DEV_MODE = os.getenv('DEV_MODE', 'true').lower() == 'true'
ENABLE_AUDIT_LOG = os.getenv('ENABLE_AUDIT_LOG', 'true').lower() == 'true'

class AuditLogger:
    """Audit log sistema MCP serverio veiksmams sekti"""
    
    def __init__(self):
        self.logs = []
    
    def log_request(self, tool_name: str, arguments: Dict[str, Any], user_id: str = None):
        """Log'inti užklausą"""
        log_entry = {
            'timestamp': time.time(),
            'tool': tool_name,
            'arguments': arguments,
            'user_id': user_id,
            'type': 'request'
        }
        self.logs.append(log_entry)
        if ENABLE_AUDIT_LOG:
            logger.info(f"AUDIT: {json.dumps(log_entry)}")
    
    def log_response(self, tool_name: str, success: bool, result: Any = None, error: Any = None):
        """Log'inti atsakymą"""
        log_entry = {
            'timestamp': time.time(),
            'tool': tool_name,
            'success': success,
            'result': result if success else None,
            'error': str(error) if error else None,
            'type': 'response'
        }
        self.logs.append(log_entry)
        if ENABLE_AUDIT_LOG:
            logger.info(f"AUDIT: {json.dumps(log_entry)}")
    
    def get_logs(self, tool_name: str = None, limit: int = 100) -> List[Dict]:
        """Gauti log'us"""
        filtered_logs = self.logs
        if tool_name:
            filtered_logs = [log for log in filtered_logs if log.get('tool') == tool_name]
        return filtered_logs[-limit:]

# Global audit logger
audit_logger = AuditLogger()

class MCPServerV2:
    """
    MCP Server v2 - Patobulinta implementacija
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000", api_token: str = None):
        self.crm = CRMIntegration(base_url=base_url, api_token=api_token)
        self.tools = MCP_FUNCTIONS
        self.descriptions = MCP_FUNCTION_DESCRIPTIONS
        self.start_time = time.time()
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apdoroti MCP užklausą su struktūruotais atsakymais
        """
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
            logger.error(f"Klaida apdorojant užklausą: {e}")
            return self._error_response('INTERNAL_ERROR', str(e))
    
    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Incializuoti MCP serverį"""
        logger.info("MCP Server v2 inicializuojamas")
        
        if DEV_MODE:
            logger.info("DEV_MODE: Įjungtas testavimo režimas")
        
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
    
    async def list_tools(self) -> Dict[str, Any]:
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
    
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Gauti įrankio schemą"""
        schemas = {
            'list_leads': {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string',
                        'enum': ['new', 'contacted', 'proposal', 'won', 'lost'],
                        'description': 'Filtruoti pagal statusą'
                    },
                    'search': {
                        'type': 'string',
                        'description': 'Paieškos terminas'
                    },
                    'limit': {
                        'type': 'integer',
                        'default': 50,
                        'description': 'Rezultatų limitas'
                    }
                }
            },
            'get_lead_details': {
                'type': 'object',
                'properties': {
                    'lead_id': {
                        'type': 'integer',
                        'description': 'Lead ID'
                    }
                },
                'required': ['lead_id']
            },
            'create_lead': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': 'Lead pavadinimas'
                    },
                    'company': {
                        'type': 'string',
                        'description': 'Įmonė'
                    },
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'description': 'El. paštas'
                    },
                    'phone': {
                        'type': 'string',
                        'description': 'Telefonas'
                    },
                    'status': {
                        'type': 'string',
                        'enum': ['new', 'contacted', 'proposal', 'won', 'lost'],
                        'default': 'new',
                        'description': 'Statusas'
                    },
                    'budget': {
                        'type': 'number',
                        'description': 'Biudžetas'
                    },
                    'notes': {
                        'type': 'string',
                        'description': 'Pastabos'
                    }
                },
                'required': ['name']
            },
            'update_lead_status': {
                'type': 'object',
                'properties': {
                    'lead_id': {
                        'type': 'integer',
                        'description': 'Lead ID'
                    },
                    'status': {
                        'type': 'string',
                        'enum': ['new', 'contacted', 'proposal', 'won', 'lost'],
                        'description': 'Naujas statusas'
                    }
                },
                'required': ['lead_id', 'status']
            },
            'get_dashboard_summary': {
                'type': 'object',
                'properties': {}
            },
            'get_followups': {
                'type': 'object',
                'properties': {
                    'type': {
                        'type': 'string',
                        'enum': ['upcoming', 'overdue'],
                        'default': 'upcoming',
                        'description': 'Follow-up tipas'
                    },
                    'days': {
                        'type': 'integer',
                        'default': 7,
                        'description': 'Dienų skaičius (artėjantiems)'
                    }
                }
            },
            'add_comment': {
                'type': 'object',
                'properties': {
                    'lead_id': {
                        'type': 'integer',
                        'description': 'Lead ID'
                    },
                    'body': {
                        'type': 'string',
                        'description': 'Komentaro turinys'
                    },
                    'kind': {
                        'type': 'string',
                        'enum': ['note', 'call', 'email', 'message'],
                        'default': 'note',
                        'description': 'Komentaro tipas'
                    },
                    'author': {
                        'type': 'string',
                        'default': 'AI Assistant',
                        'description': 'Autorius'
                    }
                },
                'required': ['lead_id', 'body']
            },
            'add_task': {
                'type': 'object',
                'properties': {
                    'lead_id': {
                        'type': 'integer',
                        'description': 'Lead ID'
                    },
                    'title': {
                        'type': 'string',
                        'description': 'Užduoties pavadinimas'
                    }
                },
                'required': ['lead_id', 'title']
            },
            'get_activities': {
                'type': 'object',
                'properties': {
                    'lead_id': {
                        'type': 'integer',
                        'description': 'Lead ID'
                    }
                },
                'required': ['lead_id']
            }
        }
        
        return schemas.get(tool_name, {'type': 'object'})
    
    async def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Iškviesti MCP įrankį su struktūruotu atsakymu"""
        try:
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            if tool_name not in self.tools:
                return self._error_response('TOOL_NOT_FOUND', f'Tool {tool_name} not found')
            
            logger.info(f'Kviečiamas įrankis: {tool_name} su argumentais: {arguments}')
            
            # Audit log - request
            audit_logger.log_request(tool_name, arguments)
            
            # Iškviečiame funkciją
            start_time = time.time()
            result = await self.tools[tool_name](self.crm, arguments)
            execution_time = time.time() - start_time
            
            # Audit log - response
            audit_logger.log_response(tool_name, True, result)
            
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
            
            logger.info(f'Įrankis {tool_name} sėkmingai įvykdytas per {execution_time:.3f}s')
            return response
            
        except Exception as e:
            logger.error(f"Klaida iškviečiant įrankį: {e}")
            
            # Audit log - error
            audit_logger.log_response(tool_name, False, error=e)
            
            return self._error_response('EXECUTION_ERROR', str(e), {
                'tool': tool_name,
                'arguments': arguments
            })
    
    def _error_response(self, code: str, message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
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
        logger.info("MCP Server v2 uždarytas")
        
        if DEV_MODE:
            # Rodyti audit log'us dev režime
            logs = audit_logger.get_logs(limit=10)
            logger.info(f"DEV_MODE: Audit log ({len(logs)} paskutiniai įrašai):")
            for log in logs:
                logger.info(f"  {json.dumps(log, indent=2)}")

async def run_mcp_server_v2():
    """
    Paleisti MCP serverį v2 su DEV_MODE kontrolė
    """
    print("🚀 Paleidžiame MCP Server v2...")
    print(f"🔧 DEV_MODE: {DEV_MODE}")
    
    # Gauname JWT tokeną
    from .mcp_server_final import get_jwt_token
    token = await get_jwt_token()
    
    if not token:
        print("❌ Nepavyko gauti JWT tokeno")
        return
    
    print("✅ JWT tokenas gautas")
    
    # Sukuriam MCP serverį
    server = MCPServerV2(base_url="http://127.0.0.1:8000", api_token=token)
    
    try:
        if DEV_MODE:
            # DEV_MODE: paleidžiam testus
            await run_dev_tests(server)
        else:
            # Production mode: laukiame užklausų
            print("🔄 Production mode: laukiama MCP užklausų...")
            # Čia būtų WebSocket arba STDIO serverio implementacija
            await asyncio.sleep(1)  # Simuliacija
            
    except Exception as e:
        logger.error(f"Klaida paleidžiant MCP serverį: {e}")
    
    finally:
        await server.close()

async def run_dev_tests(server: MCPServerV2):
    """
    Vykdyti development testus
    """
    print("🧪 DEV_MODE: Vykdomi MCP testai...")
    
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
        print(f"✅ Gauta {len(leads)} lead'ų")
        if leads:
            print(f"   Pirmas lead: {leads[0].get('name', 'N/A')}")
    else:
        print(f"❌ Klaida: {response.get('error', {}).get('message', 'Unknown')}")
    
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
        if 'id' in lead_data:
            print(f"✅ Lead'as sukurtas: ID {lead_data['id']}")
        else:
            print(f"✅ Lead'as sukurtas (be ID): {lead_data.get('name', 'N/A')}")
    else:
        print(f"❌ Klaida: {response.get('error', {}).get('message', 'Unknown')}")
    
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
        total_leads = stats.get('total_leads', 0)
        print(f"✅ Statistika gauta: {total_leads} lead'ų")
    else:
        print(f"❌ Klaida: {response.get('error', {}).get('message', 'Unknown')}")
    
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
        print(f"✅ Error handling veikia: {error.get('code')} - {error.get('message')}")
    else:
        print("❌ Error handling neveikia")
    
    print("\n🎉 MCP Server v2 testai sėkmingai baigti!")

if __name__ == "__main__":
    print("🎯 MCP Server v2 - Patobulinta Skybridge Integration")
    print("=" * 60)
    print("Django serveris turi būti paleistas: python manage.py runserver")
    print(f"DEV_MODE: {DEV_MODE} (naudokite 'set DEV_MODE=false' production režimui)")
    print()
    
    asyncio.run(run_mcp_server_v2())
