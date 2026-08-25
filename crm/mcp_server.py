"""
MCP Server implementacija skirta Skybridge ir AI agentų integracijai
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional
from .mcp_bridge import MCPBridge, MCP_FUNCTIONS

# Nustatome logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigūracija
DEV_MODE = os.getenv('DEV_MODE', 'true').lower() == 'true'

class MCPServer:
    """
    MCP Server klasė, kuri teikia CRM funkcionalumą kaip MCP tools
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000", api_token: str = None):
        self.bridge = MCPBridge(base_url=base_url, api_token=api_token)
        self.tools = MCP_FUNCTIONS
        self.descriptions = {name: func['description'] for name, func in MCP_FUNCTIONS.items()}

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apdoroti MCP užklausą
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
                return {
                    'error': {
                        'code': -32601,
                        'message': f'Method {method} not found'
                    }
                }
        except Exception as e:
            logger.error(f"Klaida apdorojant užklausą: {e}")
            return {
                'error': {
                    'code': -32603,
                    'message': str(e)
                }
            }

    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inicializuoti MCP serverį
        """
        logger.info("MCP Server inicializuojamas")
        return {
            'protocolVersion': '2024-11-05',
            'capabilities': {
                'tools': {}
            },
            'serverInfo': {
                'name': 'Freelancer CRM MCP Server',
                'version': '1.0.0'
            }
        }

    async def list_tools(self) -> Dict[str, Any]:
        """
        Grąžinti prieinamų įrankių sąrašą
        """
        tools = []
        for tool_name, description in self.descriptions.items():
            tools.append({
                'name': tool_name,
                'description': description,
                'inputSchema': self.get_tool_schema(tool_name)
            })
        
        return {
            'tools': tools
        }

    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """
        Gauti įrankio schemą
        """
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
        """
        Iškviesti MCP įrankį
        """
        try:
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            if tool_name not in self.tools:
                return {
                    'error': {
                        'code': -32601,
                        'message': f'Tool {tool_name} not found'
                    }
                }
            
            logger.info(f'Kviečiamas įrankis: {tool_name} su argumentais: {arguments}')
            
            # Iškviečiame atitinkamą MCPBridge metodą
            result = await self._execute_tool(tool_name, arguments)
            
            return {
                'result': result,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Klaida iškviečiant įrankį: {e}")
            return {
                'success': False,
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': str(e),
                    'details': {
                        'tool': tool_name,
                        'arguments': arguments
                    }
                }
            }
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vykdyti konkretų MCP įrankį naudojant MCPBridge
        """
        async with self.bridge:
            if tool_name == 'list_leads':
                return await self.bridge.get_leads(
                    limit=arguments.get('limit', 20),
                    status=arguments.get('status'),
                    search=arguments.get('search')
                )
            elif tool_name == 'get_lead':
                return await self.bridge.get_lead(arguments['lead_id'])
            elif tool_name == 'create_lead':
                return await self.bridge.create_lead(arguments)
            elif tool_name == 'update_lead':
                lead_id = arguments.pop('lead_id')
                return await self.bridge.update_lead(lead_id, arguments)
            elif tool_name == 'get_comments':
                return await self.bridge.get_comments(arguments['lead_id'])
            elif tool_name == 'create_comment':
                lead_id = arguments.pop('lead_id')
                return await self.bridge.create_comment(lead_id, arguments)
            elif tool_name == 'get_tasks':
                return await self.bridge.get_tasks(arguments['lead_id'])
            elif tool_name == 'create_task':
                lead_id = arguments.pop('lead_id')
                return await self.bridge.create_task(lead_id, arguments)
            elif tool_name == 'get_dashboard':
                return await self.bridge.get_dashboard_summary()
            else:
                raise ValueError(f'Unknown tool: {tool_name}')

    async def close(self):
        """
        Uždaryti MCP serverį
        """
        await self.bridge.__aexit__(None, None, None)
        logger.info("MCP Server uždarytas")


# Pagalbinė funkcija MCP serverio paleidimui
async def run_mcp_server(base_url: str = "http://127.0.0.1:8000", api_token: str = None):
    """
    Paleisti MCP serverį
    """
    server = MCPServer(base_url=base_url, api_token=api_token)
    
    try:
        # Čia būtų WebSocket arba STDIO komunikacija su klientu
        # Šis pavyzdys parodo kaip naudoti serverį
        print("MCP Server paleistas")
        print("Prieinami įrankiai:")
        for tool_name, description in server.descriptions.items():
            print(f"  - {tool_name}: {description}")
        
        # Laukiame užklausų (realioje implementacijoje čia būtų WebSocket serveris)
        await asyncio.sleep(1)  # Simuliacija
        
    finally:
        await server.close()


if __name__ == "__main__":
    # Testavimas
    asyncio.run(run_mcp_server())
