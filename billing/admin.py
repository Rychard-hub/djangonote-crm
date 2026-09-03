from django.contrib import admin

from .models import PaymentLink, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'monthly_price', 'max_payment_links_per_month', 'ai_content_quota')
    search_fields = ('code', 'name')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('organization', 'plan', 'status', 'current_period_end', 'created_at')
    list_filter = ('status', 'plan')
    search_fields = ('organization__name', 'stripe_subscription_id')


@admin.register(PaymentLink)
class PaymentLinkAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'organization', 'status', 'created_by', 'created_at', 'paid_at')
    list_filter = ('status', 'organization')
    search_fields = ('description', 'stripe_checkout_session_id')
    readonly_fields = ('stripe_checkout_session_id', 'url', 'created_at', 'paid_at')
