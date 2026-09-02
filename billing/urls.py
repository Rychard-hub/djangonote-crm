from django.urls import path

from .views import payment_link_create_view, payment_link_list_view, stripe_webhook_view

urlpatterns = [
    path('payment-links/', payment_link_list_view, name='payment-link-list'),
    path('payment-links/new/', payment_link_create_view, name='payment-link-create'),
    path('stripe-webhook/', stripe_webhook_view, name='stripe-webhook'),
]
