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
from django.contrib import admin
from django.urls import path, include

from crm.views import (
    dashboard_view,
    followup_list_view,
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
    password_reset_view,
    register_view,
    task_toggle_view,
    health_check,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),
    path('api/', include('crm.api_urls')),  # API endpoints
    path('catalog/', include('catalog.urls')),
    path('billing/', include('billing.urls')),
    path('', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('password-reset/', password_reset_view, name='password-reset'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('followups/', followup_list_view, name='followup-list'),
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
