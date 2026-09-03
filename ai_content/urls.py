from django.urls import path

from .views import content_job_create_view, content_job_list_view, content_job_status_view

urlpatterns = [
    path('', content_job_list_view, name='content-job-list'),
    path('new/', content_job_create_view, name='content-job-create'),
    path('<int:pk>/status/', content_job_status_view, name='content-job-status'),
]
