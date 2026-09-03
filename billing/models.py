from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from accounts.models import Organization
from catalog.models import Product
from crm.models import Lead


class Plan(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=60)
    monthly_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    stripe_price_id = models.CharField(max_length=100, blank=True)
    # 0 means unlimited.
    max_payment_links_per_month = models.PositiveIntegerField(default=3)
    ai_content_quota = models.PositiveIntegerField(default=0)
    # Named feature flags this plan unlocks, e.g. ['ai_content', 'ai_video'].
    # Nothing sets these to a non-empty list yet -- see require_plan_feature
    # in billing/decorators.py for how a future app (ai_content, assistant)
    # is meant to use them.
    features = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Aktyvi'),
        ('past_due', 'Vėluoja mokėjimas'),
        ('canceled', 'Atšaukta'),
    ]

    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.organization.name} — {self.plan.name}'

    def has_feature(self, feature_code):
        return self.status == 'active' and feature_code in self.plan.features

    def payment_links_remaining(self):
        """Payment links this organization can still create this month, or None if unlimited."""
        limit = self.plan.max_payment_links_per_month
        if limit == 0:
            return None
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        used = PaymentLink.objects.filter(organization=self.organization, created_at__gte=month_start).count()
        return max(limit - used, 0)


class PaymentLink(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Laukiama'),
        ('paid', 'Apmokėta'),
        ('expired', 'Nebegalioja'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='payment_links')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_links')
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_links')
    description = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    stripe_checkout_session_id = models.CharField(max_length=150, blank=True)
    url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_links')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.description or "Mokėjimas"} — {self.amount} {self.currency}'
