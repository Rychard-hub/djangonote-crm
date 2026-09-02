from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from accounts.models import get_organization
from catalog.models import Product
from crm.models import Lead

from .models import PaymentLink
from .services import StripeNotConfigured, create_checkout_session, verify_webhook_event


@login_required(login_url='login')
def payment_link_list_view(request):
    organization = get_organization(request.user)
    links = PaymentLink.objects.filter(organization=organization)

    context = {'links': links}
    if request.headers.get('HX-Request'):
        return render(request, 'billing/partials/_payment_link_table.html', context)
    return render(request, 'billing/payment_link_list.html', context)


@login_required(login_url='login')
def payment_link_create_view(request):
    organization = get_organization(request.user)
    products = Product.objects.filter(organization=organization, active=True)
    leads = Lead.objects.filter(organization=organization)

    if request.method == 'POST':
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
    }
    if request.headers.get('HX-Request'):
        return render(request, 'billing/partials/_payment_link_form_modal.html', context)
    return render(request, 'billing/payment_link_form.html', context)


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

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        PaymentLink.objects.filter(stripe_checkout_session_id=session['id']).update(
            status='paid', paid_at=timezone.now(),
        )

    return HttpResponse(status=200)
