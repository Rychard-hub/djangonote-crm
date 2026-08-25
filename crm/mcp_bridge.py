"""
MCP Bridge - Django API integracija su Skybridge
Hibridinio sprendimo pagrindas
"""

import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, date


class MCPBridge:
    """
    MCP Bridge serveris - sujungia Django API su Skybridge MCP protokolu
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000", api_token: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_headers(self) -> Dict[str, str]:
        """Gauti HTTP headers su autentifikacija"""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers
    
    async def authenticate(self, username: str, password: str) -> bool:
        """
        Autentifikuoti su Django API ir gauti JWT tokeną
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        login_data = {
            "username": username,
            "password": password
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/token/",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.api_token = token_data.get('access')
                    return True
                return False
        except Exception as e:
            print(f"Autentifikacijos klaida: {e}")
            return False
    
    async def get_leads(self, limit: int = 20, status: str = None, search: str = None) -> Dict[str, Any]:
        """
        Gauti lead'ų sąrašą iš Django API
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        params = {}
        if limit:
            params['limit'] = limit
        if status:
            params['status'] = status
        if search:
            params['search'] = search
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/leads/",
                params=params,
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Django DRF grąžina results su count
                    if isinstance(data, dict) and 'results' in data:
                        return {
                            'data': data['results'],
                            'count': data.get('count', len(data['results']))
                        }
                    elif isinstance(data, list):
                        return {
                            'data': data,
                            'count': len(data)
                        }
                    else:
                        return data
                else:
                    return {"error": f"HTTP {response.status}", "details": await response.text()}
        except Exception as e:
            return {"error": "connection_error", "details": str(e)}
    
    async def get_lead(self, lead_id: int) -> Dict[str, Any]:
        """
        Gauti konkretų lead'ą
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/leads/{lead_id}/",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {'data': data}
                else:
                    return {"error": f"HTTP {response.status}", "details": await response.text()}
        except Exception as e:
            return {"error": "connection_error", "details": str(e)}
    
    async def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sukurti naują lead'ą
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        # Validavimas
        required_fields = ['name']
        for field in required_fields:
            if field not in lead_data:
                return {"error": "validation_error", "details": f"Missing required field: {field}"}
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/leads/",
                json=lead_data,
                headers=self.get_headers()
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    return {'data': data}
                else:
                    return {"error": f"HTTP {response.status}", "details": await response.text()}
        except Exception as e:
            return {"error": "connection_error", "details": str(e)}
    
    async def update_lead(self, lead_id: int, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atnaujinti lead'ą
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.patch(
                f"{self.base_url}/api/leads/{lead_id}/",
                json=lead_data,
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {'data': data}
                else:
                    return {"error": f"HTTP {response.status}", "details": await response.text()}
        except Exception as e:
            return {"error": "connection_error", "details": str(e)}
    
    async def get_comments(self, lead_id: int) -> Dict[str, Any]:
        """
        Gauti lead'o komentarus
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/leads/{lead_id}/comments/",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {'data': data}
                else:
                    return {"error": f"HTTP {response.status}", "details": await response.text()}
        except Exception as e:
            return {"error": "connection_error", "details": str(e)}
    
    async def create_comment(self, lead_id: int, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sukurti komentarą
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/leads/{lead_id}/comments/",
                json=comment_data,
                headers=self.get_headers()
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    return {'data': data}
                else:
                    return {"error": f"HTTP {response.status}", "details": await response.text()}
        except Exception as e:
            return {"error": "connection_error", "details": str(e)}
    
    async def get_tasks(self, lead_id: int) -> Dict[str, Any]:
        """
        Gauti lead'o užduotis
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/leads/{lead_id}/tasks/",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {'data': data}
                else:
                    return {"error": f"HTTP {response.status}", "details": await response.text()}
        except Exception as e:
            return {"error": "connection_error", "details": str(e)}
    
    async def create_task(self, lead_id: int, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sukurti užduotį
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/leads/{lead_id}/tasks/",
                json=task_data,
                headers=self.get_headers()
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    return {'data': data}
                else:
                    return {"error": f"HTTP {response.status}", "details": await response.text()}
        except Exception as e:
            return {"error": "connection_error", "details": str(e)}
    
    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Gauti dashboard statistiką
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/dashboard/summary/",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {'data': data}
                else:
                    return {"error": f"HTTP {response.status}", "details": await response.text()}
        except Exception as e:
            return {"error": "connection_error", "details": str(e)}


# MCP funkcijų aprašymai Skybridge integracijai
MCP_FUNCTIONS = {
    'list_leads': {
        'description': 'Gauti leadų sąrašą',
        'parameters': {
            'type': 'object',
            'properties': {
                'limit': {'type': 'integer', 'description': 'Rezultatų limitas', 'default': 20},
                'status': {'type': 'string', 'description': 'Filtruoti pagal statusą'},
                'search': {'type': 'string', 'description': 'Paieškos tekstas'}
            }
        }
    },
    'get_lead': {
        'description': 'Gauti konkretų leadą',
        'parameters': {
            'type': 'object',
            'properties': {
                'lead_id': {'type': 'integer', 'description': 'Lead ID'}
            },
            'required': ['lead_id']
        }
    },
    'create_lead': {
        'description': 'Sukurti naują leadą',
        'parameters': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'description': 'Lead vardas'},
                'company': {'type': 'string', 'description': 'Kompanija'},
                'email': {'type': 'string', 'description': 'El. paštas'},
                'phone': {'type': 'string', 'description': 'Telefonas'},
                'status': {'type': 'string', 'description': 'Statusas'},
                'budget': {'type': 'number', 'description': 'Biudžetas'},
                'notes': {'type': 'string', 'description': 'Pastabos'}
            },
            'required': ['name']
        }
    },
    'update_lead': {
        'description': 'Atnaujinti leadą',
        'parameters': {
            'type': 'object',
            'properties': {
                'lead_id': {'type': 'integer', 'description': 'Lead ID'},
                'name': {'type': 'string', 'description': 'Lead vardas'},
                'company': {'type': 'string', 'description': 'Kompanija'},
                'email': {'type': 'string', 'description': 'El. paštas'},
                'phone': {'type': 'string', 'description': 'Telefonas'},
                'status': {'type': 'string', 'description': 'Statusas'},
                'budget': {'type': 'number', 'description': 'Biudžetas'},
                'notes': {'type': 'string', 'description': 'Pastabos'}
            },
            'required': ['lead_id']
        }
    },
    'get_comments': {
        'description': 'Gauti leado komentarų sąrašą',
        'parameters': {
            'type': 'object',
            'properties': {
                'lead_id': {'type': 'integer', 'description': 'Lead ID'}
            },
            'required': ['lead_id']
        }
    },
    'create_comment': {
        'description': 'Sukurti komentarą',
        'parameters': {
            'type': 'object',
            'properties': {
                'lead_id': {'type': 'integer', 'description': 'Lead ID'},
                'body': {'type': 'string', 'description': 'Komentaro tekstas'},
                'kind': {'type': 'string', 'description': 'Komentaro tipas'},
                'author': {'type': 'string', 'description': 'Autorius'}
            },
            'required': ['lead_id', 'body']
        }
    },
    'get_tasks': {
        'description': 'Gauti leado užduočių sąrašą',
        'parameters': {
            'type': 'object',
            'properties': {
                'lead_id': {'type': 'integer', 'description': 'Lead ID'}
            },
            'required': ['lead_id']
        }
    },
    'create_task': {
        'description': 'Sukurti užduotį',
        'parameters': {
            'type': 'object',
            'properties': {
                'lead_id': {'type': 'integer', 'description': 'Lead ID'},
                'title': {'type': 'string', 'description': 'Užduoties pavadinimas'}
            },
            'required': ['lead_id', 'title']
        }
    },
    'get_dashboard': {
        'description': 'Gauti dashboard statistiką',
        'parameters': {
            'type': 'object',
            'properties': {}
        }
    }
}
