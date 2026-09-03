import anthropic
from django.conf import settings

from .tools import TOOL_DEFINITIONS, execute_tool

MODEL = 'claude-opus-5'

SYSTEM_PROMPT = (
    "Tu esi Bussy'Note AI verslo asistentas. Padedi vartotojui sekti lead'us, "
    "užduotis ir follow-up'us CRM sistemoje. Naudok pateiktus įrankius CRM "
    "duomenims pasiekti ar keisti -- niekada negalvok ar nespėk duomenų, kurių "
    "neturi iš įrankių. Atsakinėk lietuviškai, trumpai ir konkrečiai."
)

MAX_TOOL_ROUNDS = 5


class AIProviderNotConfigured(Exception):
    """Raised when ANTHROPIC_API_KEY isn't set."""


def run_assistant_turn(organization, user, conversation_history, user_message):
    """Run one user turn through Claude, executing any tool calls it makes.

    conversation_history: prior turns as [{'role': 'user'|'assistant', 'content': str}, ...].
    Returns the assistant's final text reply.
    """
    if not settings.ANTHROPIC_API_KEY:
        raise AIProviderNotConfigured('ANTHROPIC_API_KEY nenustatytas aplinkos kintamuosiuose.')

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    messages = [dict(turn) for turn in conversation_history] + [{'role': 'user', 'content': user_message}]

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        if response.stop_reason != 'tool_use':
            return next((block.text for block in response.content if block.type == 'text'), '')

        messages.append({'role': 'assistant', 'content': response.content})

        tool_results = []
        for block in response.content:
            if block.type != 'tool_use':
                continue
            result_json = execute_tool(block.name, block.input, organization=organization, user=user)
            tool_results.append({'type': 'tool_result', 'tool_use_id': block.id, 'content': result_json})
        messages.append({'role': 'user', 'content': tool_results})

    return 'Atsiprašau, nepavyko užbaigti užklausos per nustatytą žingsnių skaičių. Pabandykite performuluoti klausimą.'
