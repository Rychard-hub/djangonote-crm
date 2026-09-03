from django.urls import path

from .views import (
    payment_link_create_view,
    payment_link_list_view,
    plan_list_view,
    stripe_webhook_view,
    subscribe_view,
)

urlpatterns = [
    path('payment-links/', payment_link_list_view, name='payment-link-list'),
    path('payment-links/new/', payment_link_create_view, name='payment-link-create'),
    path('plans/', plan_list_view, name='plan-list'),
    path('plans/<str:plan_code>/subscribe/', subscribe_view, name='subscribe'),
    path('stripe-webhook/', stripe_webhook_view, name='stripe-webhook'),
]
