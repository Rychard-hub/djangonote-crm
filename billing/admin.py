from django.contrib import admin

from .models import PaymentLink


@admin.register(PaymentLink)
class PaymentLinkAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'organization', 'status', 'created_by', 'created_at', 'paid_at')
    list_filter = ('status', 'organization')
    search_fields = ('description', 'stripe_checkout_session_id')
    readonly_fields = ('stripe_checkout_session_id', 'url', 'created_at', 'paid_at')
