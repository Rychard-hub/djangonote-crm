from django.urls import path

from .views import (
    product_create_view,
    product_delete_view,
    product_edit_view,
    product_list_view,
)

urlpatterns = [
    path('', product_list_view, name='product-list'),
    path('new/', product_create_view, name='product-create'),
    path('<int:pk>/edit/', product_edit_view, name='product-edit'),
    path('<int:pk>/delete/', product_delete_view, name='product-delete'),
]
