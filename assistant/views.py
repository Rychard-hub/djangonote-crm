import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from accounts.models import get_organization

from .models import Conversation, Message
from .services import AIProviderNotConfigured, run_assistant_turn

logger = logging.getLogger(__name__)

HISTORY_LIMIT = 20


@login_required(login_url='login')
def assistant_view(request):
    organization = get_organization(request.user)
    conversation, _ = Conversation.objects.get_or_create(organization=organization, created_by=request.user)
    messages = conversation.messages.all()

    initial_messages = [{'id': m.pk, 'role': m.role, 'content': m.content} for m in messages]
    return render(request, 'assistant/chat.html', {'initial_messages': initial_messages})


@login_required(login_url='login')
@require_POST
def send_message_view(request):
    organization = get_organization(request.user)
    conversation, _ = Conversation.objects.get_or_create(organization=organization, created_by=request.user)

    user_text = request.POST.get('message', '').strip()
    if not user_text:
        return HttpResponseBadRequest('message is required')

    recent = list(conversation.messages.order_by('-created_at')[:HISTORY_LIMIT])[::-1]
    history = [{'role': m.role, 'content': m.content} for m in recent]

    Message.objects.create(conversation=conversation, role='user', content=user_text)

    try:
        reply_text = run_assistant_turn(organization, request.user, history, user_text)
    except AIProviderNotConfigured as exc:
        reply_text = f'AI asistentas šiuo metu nepasiekiamas: {exc}'
    except Exception:
        logger.exception('Assistant turn failed for organization %s', organization.pk)
        reply_text = 'Atsiprašau, įvyko klaida bandant atsakyti. Bandykite dar kartą.'

    Message.objects.create(conversation=conversation, role='assistant', content=reply_text)

    return JsonResponse({'reply': reply_text})
