import os

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.views.generic import DetailView
from mainapp.models import Product, ProductCategory
# from django.views.decorators.cache import cache_page

MODULE_DIR = os.path.dirname(__file__)


def index(request):
    context = {
        'title': 'Geekshop', }
    return render(request, 'mainapp/index.html', context)


def get_links_menu():
    if settings.LOW_CACHE:
        key = 'links_menu'
        links_menu = cache.get(key)
        if links_menu is None:
            links_menu = ProductCategory.objects.filter(is_active=True)
            cache.set(key, links_menu)
        return links_menu
    else:
        return ProductCategory.objects.filter(is_active=True)


def get_products(category_pk=None):
    if settings.LOW_CACHE:
        if category_pk:
            key = f'category_{category_pk}'
            products = cache.get(key)
            if products is None:
                products = Product.objects.filter(is_active=True, category__is_active=True,
                                                  category_id=category_pk).select_related('category')
                cache.set(key, products)
            return products
        else:
            key = 'products'
            products = cache.get(key)
            if products is None:
                products = Product.objects.filter(is_active=True, category__is_active=True).select_related('category')
                cache.set(key, products)
            return products
    else:
        if category_pk:
            return Product.objects.filter(is_active=True, category__is_active=True,
                                          category_id=category_pk).select_related('category')
        else:
            return Product.objects.filter(is_active=True, category__is_active=True).select_related('category')


def get_product_one(pk):
    if settings.LOW_CACHE:
        key = f'product_{pk}'
        product = cache.get(key)
        if product is None:
            product = Product.objects.get(pk=pk)
            cache.set(key, product)
        return product
    else:
        return Product.objects.get(pk=pk)


# @cache_page(3600)
def products(request, id_category=None, page=1):
    context = {
        'title': 'Geekshop | Каталог',
    }

    products = get_products(id_category)
    paginator = Paginator(products, per_page=3)

    try:
        products_paginator = paginator.page(page)
    except PageNotAnInteger:
        products_paginator = paginator.page(1)
    except EmptyPage:
        products_paginator = paginator.page(paginator.num_pages)

    context['products'] = products_paginator
    context['categories'] = get_links_menu()
    return render(request, 'mainapp/products.html', context)


class ProductDetail(DetailView):
    """
    Контроллер вывода информации о продукте
    """
    model = Product
    template_name = 'mainapp/detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        context['product'] = get_product_one(self.kwargs.get('pk'))
        return context
