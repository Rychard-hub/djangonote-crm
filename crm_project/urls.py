"""
URL configuration for crm_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse_lazy

from crm.views import (
    dashboard_view,
    followup_list_view,
    followup_toast_view,
    followup_toast_dismiss_view,
    pipeline_view,
    settings_view,
    lead_comment_add_view,
    lead_create_view,
    lead_delete_view,
    lead_detail_view,
    lead_edit_view,
    lead_list_view,
    lead_pipeline_move_view,
    lead_quick_action_view,
    lead_reminder_send_view,
    lead_status_mark_view,
    lead_status_update_view,
    lead_task_add_view,
    login_view,
    logout_view,
    register_view,
    resend_verification_view,
    verify_email_view,
    task_toggle_view,
    health_check,
)

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),
    path('api/', include('crm.api_urls')),  # API endpoints
    path('catalog/', include('catalog.urls')),
    path('billing/', include('billing.urls')),
    path('ai-content/', include('ai_content.urls')),
    path('assistant/', include('assistant.urls')),
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='crm/password_reset.html',
        email_template_name='crm/email/password_reset.txt',
        subject_template_name='crm/email/password_reset_subject.txt',
        success_url=reverse_lazy('password-reset-done'),
    ), name='password-reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='crm/password_reset_done.html',
    ), name='password-reset-done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='crm/password_reset_confirm.html',
        success_url=reverse_lazy('password-reset-complete'),
    ), name='password-reset-confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='crm/password_reset_complete.html',
    ), name='password-reset-complete'),
    path('verify-email/resend/', resend_verification_view, name='resend-verification'),
    path('verify-email/<uuid:token>/', verify_email_view, name='verify-email'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('followups/', followup_list_view, name='followup-list'),
    path('followups/toast/', followup_toast_view, name='followup-toast'),
    path('followups/toast/dismiss/', followup_toast_dismiss_view, name='followup-toast-dismiss'),
    path('pipeline/', pipeline_view, name='pipeline'),
    path('settings/', settings_view, name='settings'),
    path('leads/', lead_list_view, name='lead-list'),
    path('leads/new/', lead_create_view, name='lead-create'),
    path('leads/<int:pk>/', lead_detail_view, name='lead-detail'),
    path('leads/<int:pk>/edit/', lead_edit_view, name='lead-edit'),
    path('leads/<int:pk>/delete/', lead_delete_view, name='lead-delete'),
    path('leads/<int:pk>/status/', lead_status_update_view, name='lead-status-update'),
    path('leads/<int:pk>/comments/', lead_comment_add_view, name='lead-comment-add'),
    path('leads/<int:pk>/reminder/', lead_reminder_send_view, name='lead-reminder-send'),
    path('leads/<int:pk>/tasks/', lead_task_add_view, name='lead-task-add'),
    path('tasks/<int:pk>/toggle/', task_toggle_view, name='task-toggle'),
    path('leads/<int:pk>/mark/<str:status>/', lead_status_mark_view, name='lead-status-mark'),
    path('leads/<int:pk>/pipeline-move/<str:status>/', lead_pipeline_move_view, name='lead-pipeline-move'),
    path('leads/<int:pk>/quick-action/', lead_quick_action_view, name='lead-quick-action'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
