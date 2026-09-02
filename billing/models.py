from django.contrib.auth.models import User
from django.db import models

from accounts.models import Organization
from catalog.models import Product
from crm.models import Lead


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
