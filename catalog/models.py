from django.db import models

from accounts.models import Organization


class Product(models.Model):
    KIND_CHOICES = [
        ('product', 'Produktas'),
        ('service', 'Paslauga'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=150)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default='service')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='EUR')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
