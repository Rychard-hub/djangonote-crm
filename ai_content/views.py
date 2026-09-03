from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.models import get_organization
from billing.decorators import require_plan_feature
from billing.services import get_subscription

from .models import ContentJob
from .services import content_jobs_remaining
from .tasks import run_content_job


@login_required(login_url='login')
def content_job_list_view(request):
    organization = get_organization(request.user)
    subscription = get_subscription(organization)
    jobs = ContentJob.objects.filter(organization=organization)
    has_feature = subscription.has_feature('ai_content')

    context = {
        'jobs': jobs,
        'subscription': subscription,
        'has_feature': has_feature,
        'remaining': content_jobs_remaining(subscription) if has_feature else 0,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'ai_content/partials/_content_job_table.html', context)
    return render(request, 'ai_content/content_job_list.html', context)


@login_required(login_url='login')
def content_job_create_view(request):
    organization = get_organization(request.user)
    subscription = get_subscription(organization)
    has_feature = subscription.has_feature('ai_content')
    remaining = content_jobs_remaining(subscription) if has_feature else 0
    blocked = (not has_feature) or remaining <= 0

    if request.method == 'POST':
        if blocked:
            if not has_feature:
                error = f'AI turinio generavimas nepasiekiamas „{subscription.plan.name}“ plane.'
            else:
                error = f'Pasiektas „{subscription.plan.name}“ plano mėnesio AI generavimų limitas ({subscription.plan.ai_content_quota}).'
            context = {'error': error, 'has_feature': has_feature, 'blocked': True}
            if request.headers.get('HX-Request'):
                return render(request, 'ai_content/partials/_content_job_form_modal.html', context)
            return render(request, 'ai_content/content_job_form.html', context)

        kind = request.POST.get('kind', 'headline')
        prompt = request.POST.get('prompt', '').strip()
        job = ContentJob.objects.create(organization=organization, created_by=request.user, kind=kind, prompt=prompt)
        run_content_job.delay(job.pk)

        if request.headers.get('HX-Request'):
            response = HttpResponse(status=204)
            response['HX-Redirect'] = reverse('content-job-list')
            return response
        return redirect('content-job-list')

    context = {
        'has_feature': has_feature,
        'blocked': blocked,
        'remaining': remaining,
        'plan_name': subscription.plan.name,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'ai_content/partials/_content_job_form_modal.html', context)
    return render(request, 'ai_content/content_job_form.html', context)


@login_required(login_url='login')
@require_plan_feature('ai_content')
def content_job_status_view(request, pk):
    """Polled by HTMX (every 2s) while a job is pending/processing."""
    organization = get_organization(request.user)
    job = get_object_or_404(ContentJob, pk=pk, organization=organization)
    return render(request, 'ai_content/partials/_content_job_row.html', {'job': job})
