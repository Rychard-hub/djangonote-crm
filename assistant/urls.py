from django.urls import path

from .views import assistant_view, send_message_view

urlpatterns = [
    path('', assistant_view, name='assistant'),
    path('send/', send_message_view, name='assistant-send'),
]
