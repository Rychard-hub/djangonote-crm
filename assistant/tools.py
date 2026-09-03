"""
CRM tools the assistant can call, scoped to the calling user's organization.

Deliberately not built on crm/mcp_tools.py -- that layer talks to the DRF
API over HTTP (aiohttp + bearer token), designed for an external MCP
client. Calling it from inside a Django view already in the same process
would mean a self-referential HTTP loopback needing an async event loop
and a live server bound to the API host, which is fragile in tests and
adds no real isolation benefit here. The invariant that actually matters
-- every tool is scoped to the caller's organization, not raw unscoped
DB access -- is enforced directly in each function below instead.
"""

import json
from datetime import date

from crm.models import Activity, Comment, Lead, Task

TOOL_DEFINITIONS = [
    {
        'name': 'list_leads',
        'description': "Grąžina organizacijos lead'ų sąrašą, pasirinktinai filtruojant pagal statusą.",
        'input_schema': {
            'type': 'object',
            'properties': {
                'status': {'type': 'string', 'enum': ['new', 'contacted', 'proposal', 'won', 'lost']},
                'limit': {'type': 'integer', 'description': 'Kiek daugiausiai lead\'ų grąžinti (numatyta 10).'},
            },
        },
    },
    {
        'name': 'get_lead',
        'description': "Grąžina vieno lead'o detales pagal ID.",
        'input_schema': {
            'type': 'object',
            'properties': {'lead_id': {'type': 'integer'}},
            'required': ['lead_id'],
        },
    },
    {
        'name': 'create_lead',
        'description': "Sukuria naują lead'ą.",
        'input_schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'company': {'type': 'string'},
                'email': {'type': 'string'},
                'phone': {'type': 'string'},
                'notes': {'type': 'string'},
            },
            'required': ['name'],
        },
    },
    {
        'name': 'update_lead',
        'description': "Atnaujina esamo lead'o statusą ir/arba pastabas.",
        'input_schema': {
            'type': 'object',
            'properties': {
                'lead_id': {'type': 'integer'},
                'status': {'type': 'string', 'enum': ['new', 'contacted', 'proposal', 'won', 'lost']},
                'notes': {'type': 'string'},
            },
            'required': ['lead_id'],
        },
    },
    {
        'name': 'add_note',
        'description': "Prideda pastabą prie lead'o komunikacijos istorijos.",
        'input_schema': {
            'type': 'object',
            'properties': {
                'lead_id': {'type': 'integer'},
                'body': {'type': 'string'},
            },
            'required': ['lead_id', 'body'],
        },
    },
    {
        'name': 'list_due_followups',
        'description': "Grąžina lead'us, kuriems follow-up terminas šiandien arba jau praėjęs.",
        'input_schema': {'type': 'object', 'properties': {}},
    },
    {
        'name': 'mark_task_done',
        'description': 'Pažymi užduotį kaip atliktą.',
        'input_schema': {
            'type': 'object',
            'properties': {'task_id': {'type': 'integer'}},
            'required': ['task_id'],
        },
    },
]


def _lead_to_dict(lead):
    return {
        'id': lead.pk,
        'name': lead.name,
        'company': lead.company,
        'email': lead.email,
        'status': lead.status,
        'next_follow_up': str(lead.next_follow_up) if lead.next_follow_up else None,
        'budget': str(lead.budget),
    }


def _list_leads(organization, user, status=None, limit=10):
    qs = Lead.objects.filter(organization=organization)
    if status:
        qs = qs.filter(status=status)
    return [_lead_to_dict(lead) for lead in qs.order_by('-updated_at')[: limit or 10]]


def _get_lead(organization, user, lead_id):
    try:
        lead = Lead.objects.get(pk=lead_id, organization=organization)
    except Lead.DoesNotExist:
        return {'error': f"Lead'as #{lead_id} nerastas."}
    return _lead_to_dict(lead)


def _create_lead(organization, user, name, company='', email='', phone='', notes=''):
    lead = Lead.objects.create(
        organization=organization, owner=user, name=name, company=company,
        email=email, phone=phone, notes=notes, status='new',
    )
    Activity.objects.create(lead=lead, action='created_by_assistant', details='Sukurta per AI asistentą', created_by=user)
    return _lead_to_dict(lead)


def _update_lead(organization, user, lead_id, status=None, notes=None):
    try:
        lead = Lead.objects.get(pk=lead_id, organization=organization)
    except Lead.DoesNotExist:
        return {'error': f"Lead'as #{lead_id} nerastas."}
    if status:
        lead.status = status
    if notes is not None:
        lead.notes = notes
    lead.save()
    Activity.objects.create(lead=lead, action='updated_by_assistant', details='Atnaujinta per AI asistentą', created_by=user)
    return _lead_to_dict(lead)


def _add_note(organization, user, lead_id, body):
    try:
        lead = Lead.objects.get(pk=lead_id, organization=organization)
    except Lead.DoesNotExist:
        return {'error': f"Lead'as #{lead_id} nerastas."}
    comment = Comment.objects.create(lead=lead, body=body, author=user.username, kind='note', created_by=user)
    return {'id': comment.pk, 'lead_id': lead.pk, 'body': comment.body}


def _list_due_followups(organization, user):
    today = date.today()
    qs = Lead.objects.filter(organization=organization, next_follow_up__isnull=False, next_follow_up__lte=today)
    return [_lead_to_dict(lead) for lead in qs.order_by('next_follow_up')[:20]]


def _mark_task_done(organization, user, task_id):
    try:
        task = Task.objects.get(pk=task_id, lead__organization=organization)
    except Task.DoesNotExist:
        return {'error': f'Užduotis #{task_id} nerasta.'}
    task.completed = True
    task.save()
    Activity.objects.create(lead=task.lead, action='task_toggled', details=f'{task.title} (per AI asistentą)', created_by=user)
    return {'id': task.pk, 'title': task.title, 'completed': task.completed}


TOOL_HANDLERS = {
    'list_leads': _list_leads,
    'get_lead': _get_lead,
    'create_lead': _create_lead,
    'update_lead': _update_lead,
    'add_note': _add_note,
    'list_due_followups': _list_due_followups,
    'mark_task_done': _mark_task_done,
}


def execute_tool(name, tool_input, organization, user):
    """Run a tool call by name, always returning a JSON string (never raising)."""
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        return json.dumps({'error': f'Nežinomas įrankis: {name}'})
    try:
        result = handler(organization=organization, user=user, **tool_input)
    except TypeError as exc:
        result = {'error': f'Netinkami įrankio parametrai: {exc}'}
    return json.dumps(result, ensure_ascii=False)
