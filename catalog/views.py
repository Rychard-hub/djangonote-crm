from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.models import get_organization
from .models import Product


@login_required(login_url='login')
def product_list_view(request):
    organization = get_organization(request.user)
    products = Product.objects.filter(organization=organization)

    query = request.GET.get('q', '').strip()
    kind = request.GET.get('kind', '')
    active = request.GET.get('active', '')

    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)

    if kind:
        products = products.filter(kind=kind)

    if active == 'yes':
        products = products.filter(active=True)
    elif active == 'no':
        products = products.filter(active=False)

    context = {
        'products': products,
        'query': query,
        'kind': kind,
        'active': active,
        'total_products': products.count(),
    }
    if request.headers.get('HX-Request'):
        return render(request, 'catalog/partials/_product_list_response.html', context)
    return render(request, 'catalog/product_list.html', context)


@login_required(login_url='login')
def product_create_view(request):
    if request.method == 'POST':
        Product.objects.create(
            name=request.POST.get('name', '').strip(),
            kind=request.POST.get('kind', 'service'),
            description=request.POST.get('description', '').strip(),
            price=request.POST.get('price', '0') or '0',
            currency=request.POST.get('currency', 'EUR').strip() or 'EUR',
            active=bool(request.POST.get('active')),
            organization=get_organization(request.user),
        )
        if request.headers.get('HX-Request'):
            response = HttpResponse(status=204)
            response['HX-Redirect'] = reverse('product-list')
            return response
        return redirect('product-list')

    if request.headers.get('HX-Request'):
        return render(request, 'catalog/partials/_product_form_modal.html', {'mode': 'create'})
    return render(request, 'catalog/product_form.html', {'mode': 'create'})


@login_required(login_url='login')
def product_edit_view(request, pk):
    product = get_object_or_404(Product, pk=pk, organization=get_organization(request.user))

    if request.method == 'POST':
        product.name = request.POST.get('name', '').strip()
        product.kind = request.POST.get('kind', 'service')
        product.description = request.POST.get('description', '').strip()
        product.price = request.POST.get('price', '0') or '0'
        product.currency = request.POST.get('currency', 'EUR').strip() or 'EUR'
        product.active = bool(request.POST.get('active'))
        product.save()
        if request.headers.get('HX-Request'):
            response = HttpResponse(status=204)
            response['HX-Redirect'] = reverse('product-list')
            return response
        return redirect('product-list')

    if request.headers.get('HX-Request'):
        return render(request, 'catalog/partials/_product_form_modal.html', {'mode': 'edit', 'product': product})
    return render(request, 'catalog/product_form.html', {'mode': 'edit', 'product': product})


@login_required(login_url='login')
def product_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk, organization=get_organization(request.user))
    if request.method == 'POST':
        product.delete()
        return redirect('product-list')
    return render(request, 'catalog/product_confirm_delete.html', {'product': product})
