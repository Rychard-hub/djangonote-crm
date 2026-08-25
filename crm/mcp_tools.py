"""
MCP (Model Context Protocol) integracijos sluoksnis skirtas Skybridge ir AI agentams
"""

import asyncio
import json
import aiohttp
from datetime import date, timedelta
from typing import Dict, List, Optional, Any

class CRMIntegration:
    """
    CRM integracijos klasė, kuri pateikia API funkcionalumą MCP serveriui
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000", api_token: str = None, user_id: str = None):
        self.base_url = base_url
        self.api_token = api_token
        self.user_id = user_id
        self.session = None

    async def get_session(self):
        """Gauti HTTP sesiją su autentifikacija"""
        if self.session is None:
            headers = {}
            if self.api_token:
                headers['Authorization'] = f'Bearer {self.api_token}'
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session

    async def close(self):
        """Uždaryti sesiją"""
        if self.session:
            await self.session.close()

    # Lead'ų valdymo funkcijos
    async def list_leads(self, status: str = None, search: str = None, limit: int = 50, view: str = "detailed") -> List[Dict]:
        """Gauti lead'ų sąrašą su compact/detailed režimais"""
        session = await self.get_session()
        params = {'limit': limit}
        
        if status:
            params['status'] = status
        if search:
            params['search'] = search
            
        async with session.get(f"{self.base_url}/api/leads/", params=params) as response:
            if response.status == 200:
                data = await response.json()
                leads = data.get('results', data)
                
                # Compact režimas - grąžina tik esminę informaciją AI agentui
                if view == "compact":
                    compact_leads = []
                    for lead in leads:
                        compact_lead = {
                            'id': lead.get('id'),
                            'name': lead.get('name'),
                            'company': lead.get('company'),
                            'status': lead.get('status'),
                            'status_display': lead.get('status_display'),
                            'next_follow_up': lead.get('next_follow_up'),
                            'budget': lead.get('budget'),
                            'email': lead.get('email')
                        }
                        compact_leads.append(compact_lead)
                    return compact_leads
                
                # Detailed režimas - grąžina pilną informaciją
                return leads
            return []

    async def get_lead(self, lead_id: int) -> Optional[Dict]:
        """Gauti konkretų lead'ą"""
        session = await self.get_session()
        async with session.get(f"{self.base_url}/api/leads/{lead_id}/") as response:
            if response.status == 200:
                return await response.json()
            return None

    async def create_lead(self, lead_data: Dict) -> Optional[Dict]:
        """Sukurti naują lead'ą"""
        session = await self.get_session()
        async with session.post(f"{self.base_url}/api/leads/", json=lead_data) as response:
            if response.status == 201:
                return await response.json()
            return None

    async def update_lead_status(self, lead_id: int, status: str) -> Optional[Dict]:
        """Atnaujinti lead'o statusą"""
        session = await self.get_session()
        async with session.patch(
            f"{self.base_url}/api/leads/{lead_id}/update_status/", 
            json={'status': status}
        ) as response:
            if response.status == 200:
                return await response.json()
            return None

    # Dashboard ir statistikos funkcijos
    async def get_dashboard_stats(self) -> Dict:
        """Gauti dashboard statistiką"""
        session = await self.get_session()
        async with session.get(f"{self.base_url}/api/leads/dashboard_stats/") as response:
            if response.status == 200:
                return await response.json()
            return {}

    async def get_upcoming_followups(self, days: int = 7) -> List[Dict]:
        """Gauti artėjančius follow-up'us"""
        session = await self.get_session()
        async with session.get(f"{self.base_url}/api/leads/upcoming_followups/?days={days}") as response:
            if response.status == 200:
                return await response.json()
            return []

    async def get_overdue_followups(self) -> List[Dict]:
        """Gauti vėluojančius follow-up'us"""
        session = await self.get_session()
        async with session.get(f"{self.base_url}/api/leads/overdue_followups/") as response:
            if response.status == 200:
                return await response.json()
            return []

    # Komentarų ir užduočių funkcijos
    async def add_comment(self, lead_id: int, body: str, kind: str = 'note', author: str = 'AI Assistant') -> Optional[Dict]:
        """Pridėti komentarą prie lead'o"""
        session = await self.get_session()
        comment_data = {
            'body': body,
            'kind': kind,
            'author': author
        }
        async with session.post(f"{self.base_url}/api/leads/{lead_id}/add_comment/", json=comment_data) as response:
            if response.status == 201:
                return await response.json()
            return None

    async def add_task(self, lead_id: int, title: str) -> Optional[Dict]:
        """Pridėti užduotį prie lead'o"""
        session = await self.get_session()
        task_data = {'title': title}
        async with session.post(f"{self.base_url}/api/leads/{lead_id}/add_task/", json=task_data) as response:
            if response.status == 201:
                return await response.json()
            return None

    async def get_lead_activities(self, lead_id: int) -> List[Dict]:
        """Gauti lead'o veiksmų istoriją"""
        session = await self.get_session()
        async with session.get(f"{self.base_url}/api/leads/{lead_id}/activities/") as response:
            if response.status == 200:
                return await response.json()
            return []

    # Užduočių valdymas
    async def list_tasks(self, completed: bool = None) -> List[Dict]:
        """Gauti užduočių sąrašą"""
        session = await self.get_session()
        params = {}
        if completed is not None:
            params['completed'] = completed
            
        async with session.get(f"{self.base_url}/api/tasks/", params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('results', data)
            return []

    async def toggle_task_complete(self, task_id: int) -> Optional[Dict]:
        """Perjungti užduoties būseną"""
        session = await self.get_session()
        async with session.patch(f"{self.base_url}/api/tasks/{task_id}/toggle_complete/") as response:
            if response.status == 200:
                return await response.json()
            return None


# MCP funkcijos, kurios bus registruojamos
async def mcp_list_leads(crm: CRMIntegration, arguments: Dict) -> List[Dict]:
    """MCP funkcija: lead'ų sąrašas"""
    status = arguments.get('status')
    search = arguments.get('search')
    limit = arguments.get('limit', 50)
    
    leads = await crm.list_leads(status=status, search=search, limit=limit)
    return leads

async def mcp_get_lead_details(crm: CRMIntegration, arguments: Dict) -> Optional[Dict]:
    """MCP funkcija: lead'o detalės"""
    lead_id = arguments.get('lead_id')
    if not lead_id:
        raise ValueError("lead_id parametras privalomas")
    
    return await crm.get_lead(lead_id)

async def mcp_create_lead(crm: CRMIntegration, arguments: Dict) -> Optional[Dict]:
    """MCP funkcija: sukurti lead'ą"""
    required_fields = ['name']
    for field in required_fields:
        if field not in arguments:
            raise ValueError(f"{field} parametras privalomas")
    
    return await crm.create_lead(arguments)

async def mcp_update_lead_status(crm: CRMIntegration, arguments: Dict) -> Optional[Dict]:
    """MCP funkcija: atnaujinti lead'o statusą"""
    lead_id = arguments.get('lead_id')
    status = arguments.get('status')
    
    if not lead_id or not status:
        raise ValueError("lead_id ir status parametrai privalomi")
    
    return await crm.update_lead_status(lead_id, status)

async def mcp_get_dashboard_summary(crm: CRMIntegration, arguments: Dict) -> Dict:
    """MCP funkcija: dashboard suvestinė"""
    return await crm.get_dashboard_stats()

async def mcp_get_followups(crm: CRMIntegration, arguments: Dict) -> Dict:
    """MCP funkcija: follow-up'ai"""
    followup_type = arguments.get('type', 'upcoming')  # upcoming, overdue
    days = arguments.get('days', 7)
    
    if followup_type == 'overdue':
        return {'overdue_followups': await crm.get_overdue_followups()}
    else:
        return {'upcoming_followups': await crm.get_upcoming_followups(days)}

async def mcp_add_comment(crm: CRMIntegration, arguments: Dict) -> Optional[Dict]:
    """MCP funkcija: pridėti komentarą"""
    lead_id = arguments.get('lead_id')
    body = arguments.get('body')
    kind = arguments.get('kind', 'note')
    author = arguments.get('author', 'AI Assistant')
    
    if not lead_id or not body:
        raise ValueError("lead_id ir body parametrai privalomi")
    
    return await crm.add_comment(lead_id, body, kind, author)

async def mcp_add_task(crm: CRMIntegration, arguments: Dict) -> Optional[Dict]:
    """MCP funkcija: pridėti užduotį"""
    lead_id = arguments.get('lead_id')
    title = arguments.get('title')
    
    if not lead_id or not title:
        raise ValueError("lead_id ir title parametrai privalomi")
    
    return await crm.add_task(lead_id, title)

async def mcp_get_activities(crm: CRMIntegration, arguments: Dict) -> List[Dict]:
    """MCP funkcija: gauti veiksmų istoriją"""
    lead_id = arguments.get('lead_id')
    if not lead_id:
        raise ValueError("lead_id parametras privalomas")
    
    return await crm.get_lead_activities(lead_id)


# MCP funkcijų registras
MCP_FUNCTIONS = {
    'list_leads': mcp_list_leads,
    'get_lead_details': mcp_get_lead_details,
    'create_lead': mcp_create_lead,
    'update_lead_status': mcp_update_lead_status,
    'get_dashboard_summary': mcp_get_dashboard_summary,
    'get_followups': mcp_get_followups,
    'add_comment': mcp_add_comment,
    'add_task': mcp_add_task,
    'get_activities': mcp_get_activities,
}

# Funkcijų aprašymai dokumentacijai
MCP_FUNCTION_DESCRIPTIONS = {
    'list_leads': 'Gauti leadų sąrašą su filtravimo galimybėmis',
    'get_lead_details': 'Gauti detalų informaciją apie konkretų leadą',
    'create_lead': 'Sukurti naują leadą su nurodytais duomenimis',
    'update_lead_status': 'Atnaujinti leado statusą (new, contacted, proposal, won, lost)',
    'get_dashboard_summary': 'Gauti dashboard statistiką ir suvestinę',
    'get_followups': 'Gauti artėjančius ar vėluojančius follow-upus',
    'add_comment': 'Pridėti komentarą ar pastabą prie leado',
    'add_task': 'Pridėti užduotį prie leado',
    'get_activities': 'Gauti leado veiksmų istoriją',
}
