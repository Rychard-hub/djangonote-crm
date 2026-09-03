from datetime import datetime, timezone as dt_timezone
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from accounts.models import get_organization
from catalog.models import Product
from crm.models import Lead

from .models import PaymentLink, Plan, Subscription
from .services import (
    StripeNotConfigured,
    create_checkout_session,
    create_subscription_checkout_session,
    get_subscription,
    verify_webhook_event,
)


@login_required(login_url='login')
def payment_link_list_view(request):
    organization = get_organization(request.user)
    subscription = get_subscription(organization)
    links = PaymentLink.objects.filter(organization=organization)

    context = {
        'links': links,
        'subscription': subscription,
        'remaining': subscription.payment_links_remaining(),
    }
    if request.headers.get('HX-Request'):
        return render(request, 'billing/partials/_payment_link_table.html', context)
    return render(request, 'billing/payment_link_list.html', context)


@login_required(login_url='login')
def payment_link_create_view(request):
    organization = get_organization(request.user)
    subscription = get_subscription(organization)
    products = Product.objects.filter(organization=organization, active=True)
    leads = Lead.objects.filter(organization=organization)
    remaining = subscription.payment_links_remaining()
    quota_exceeded = remaining is not None and remaining <= 0

    if request.method == 'POST':
        if quota_exceeded:
            error = f'Pasiektas „{subscription.plan.name}“ plano mėnesio mokėjimo nuorodų limitas ({subscription.plan.max_payment_links_per_month}).'
            context = {'error': error, 'products': products, 'leads': leads}
            if request.headers.get('HX-Request'):
                return render(request, 'billing/partials/_payment_link_form_modal.html', context)
            return render(request, 'billing/payment_link_form.html', context)

        try:
            amount = Decimal(request.POST.get('amount', '0') or '0')
        except InvalidOperation:
            amount = Decimal('0')

        payment_link = PaymentLink(
            organization=organization,
            description=request.POST.get('description', '').strip(),
            amount=amount,
            currency=request.POST.get('currency', 'EUR').strip() or 'EUR',
            product_id=request.POST.get('product') or None,
            lead_id=request.POST.get('lead') or None,
            created_by=request.user,
        )

        try:
            session = create_checkout_session(
                payment_link,
                success_url=request.build_absolute_uri(reverse('payment-link-list')) + '?paid=1',
                cancel_url=request.build_absolute_uri(reverse('payment-link-list')),
            )
        except StripeNotConfigured as exc:
            context = {'error': str(exc), 'products': products, 'leads': leads}
            if request.headers.get('HX-Request'):
                return render(request, 'billing/partials/_payment_link_form_modal.html', context)
            return render(request, 'billing/payment_link_form.html', context)

        payment_link.stripe_checkout_session_id = session.id
        payment_link.url = session.url
        payment_link.save()

        if request.headers.get('HX-Request'):
            response = HttpResponse(status=204)
            response['HX-Redirect'] = reverse('payment-link-list')
            return response
        return redirect('payment-link-list')

    context = {
        'products': products,
        'leads': leads,
        'selected_lead': request.GET.get('lead', ''),
        'quota_exceeded': quota_exceeded,
        'remaining': remaining,
        'plan_name': subscription.plan.name,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'billing/partials/_payment_link_form_modal.html', context)
    return render(request, 'billing/payment_link_form.html', context)


@login_required(login_url='login')
def plan_list_view(request):
    organization = get_organization(request.user)
    subscription = get_subscription(organization)
    plans = Plan.objects.exclude(code=subscription.plan.code).order_by('monthly_price')

    context = {'subscription': subscription, 'plans': plans}
    return render(request, 'billing/plan_list.html', context)


@login_required(login_url='login')
def subscribe_view(request, plan_code):
    organization = get_organization(request.user)
    subscription = get_subscription(organization)
    plan = get_object_or_404(Plan, code=plan_code)

    if request.method == 'POST':
        try:
            session = create_subscription_checkout_session(
                organization,
                plan,
                success_url=request.build_absolute_uri(reverse('plan-list')) + '?subscribed=1',
                cancel_url=request.build_absolute_uri(reverse('plan-list')),
            )
        except StripeNotConfigured as exc:
            context = {
                'subscription': subscription,
                'plans': Plan.objects.exclude(code=subscription.plan.code).order_by('monthly_price'),
                'error': str(exc),
            }
            return render(request, 'billing/plan_list.html', context)
        return redirect(session.url)

    return redirect('plan-list')


@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = verify_webhook_event(payload, sig_header)
    except StripeNotConfigured:
        return HttpResponse(status=503)
    except Exception:
        return HttpResponseBadRequest()

    event_type = event['type']
    data = event['data']['object']

    if event_type == 'checkout.session.completed':
        if data.get('mode') == 'subscription':
            _activate_subscription_from_session(data)
        else:
            PaymentLink.objects.filter(stripe_checkout_session_id=data['id']).update(
                status='paid', paid_at=timezone.now(),
            )
    elif event_type == 'customer.subscription.updated':
        _sync_subscription_status(data)
    elif event_type == 'customer.subscription.deleted':
        Subscription.objects.filter(stripe_subscription_id=data['id']).update(status='canceled')

    return HttpResponse(status=200)


def _activate_subscription_from_session(session):
    """Handle checkout.session.completed for a mode='subscription' session."""
    organization_id = session.get('metadata', {}).get('organization_id')
    plan_code = session.get('metadata', {}).get('plan_code')
    if not organization_id or not plan_code:
        return

    try:
        plan = Plan.objects.get(code=plan_code)
    except Plan.DoesNotExist:
        return

    Subscription.objects.update_or_create(
        organization_id=organization_id,
        defaults={
            'plan': plan,
            'stripe_subscription_id': session.get('subscription', ''),
            'status': 'active',
        },
    )


def _sync_subscription_status(stripe_subscription):
    status_map = {
        'active': 'active',
        'trialing': 'active',
        'past_due': 'past_due',
        'unpaid': 'past_due',
        'canceled': 'canceled',
        'incomplete_expired': 'canceled',
    }
    status = status_map.get(stripe_subscription.get('status'), 'past_due')

    period_end = stripe_subscription.get('current_period_end')
    update_fields = {'status': status}
    if period_end:
        update_fields['current_period_end'] = datetime.fromtimestamp(period_end, tz=dt_timezone.utc)

    Subscription.objects.filter(stripe_subscription_id=stripe_subscription['id']).update(**update_fields)
