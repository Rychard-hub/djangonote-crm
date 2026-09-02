from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'organization', 'price', 'currency', 'active', 'created_at')
    list_filter = ('kind', 'active', 'organization')
    search_fields = ('name', 'description')
