from functools import wraps

from django.http import HttpResponseForbidden

from accounts.models import get_organization

from .services import get_subscription


def require_plan_feature(feature_code):
    """View decorator gating access behind a named plan feature (e.g. 'ai_video').

    No plan currently has a non-empty `features` list, so nothing is gated
    by this yet -- it's here for ai_content/assistant to use once built,
    per docs/bussynote-mvp-architecture.md sections 6-7, without every new
    app having to re-derive the organization -> subscription -> plan check.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            organization = get_organization(request.user)
            subscription = get_subscription(organization)
            if not subscription.has_feature(feature_code):
                return HttpResponseForbidden(
                    f"Ši funkcija („{feature_code}“) nepasiekiama jūsų plane ({subscription.plan.name})."
                )
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
