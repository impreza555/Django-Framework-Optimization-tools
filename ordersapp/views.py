from django.db import transaction
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, TemplateView
from baskets.models import Basket
from mainapp.mixin import BaseClassContextMixin
from mainapp.models import Product
from ordersapp.forms import OrderItemsForm
from ordersapp.models import Order, OrderItem


class OrderList(ListView, BaseClassContextMixin):
    model = Order
    title = 'Geekshop | Список заказов'

    def get_queryset(self):
        return Order.objects.filter(is_active=True, user=self.request.user)


class OrderItemsCreate(CreateView, BaseClassContextMixin):
    model = Order
    fields = []
    success_url = reverse_lazy('ordersapp:orders_list')
    title = 'Geekshop | Заказы/cоздание'

    def get_context_data(self, **kwargs):
        context = super(OrderItemsCreate, self).get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(Order, OrderItem, OrderItemsForm, extra=1)
        if self.request.POST:
            formset = OrderFormSet(self.request.POST)
        else:
            basket_items = Basket.objects.filter(user=self.request.user)
            if basket_items:
                OrderFormSet = inlineformset_factory(Order, OrderItem, OrderItemsForm, extra=basket_items.count())
                formset = OrderFormSet()
                for num, form in enumerate(formset.forms):
                    form.initial['product'] = basket_items[num].product
                    form.initial['quantity'] = basket_items[num].quantity
                    form.initial['price'] = basket_items[num].product.price
                basket_items.delete()
            else:
                formset = OrderFormSet()
        context['orderitems'] = formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']
        with transaction.atomic():
            form.instance.user = self.request.user
            self.object = form.save()
            if orderitems.is_valid():
                orderitems.instance = self.object
                orderitems.save()
            if self.object.get_total_cost() == 0:
                self.object.delete()
        return super(OrderItemsCreate, self).form_valid(form)


class OrderItemsUpdate(UpdateView, BaseClassContextMixin):
    model = Order
    fields = []
    success_url = reverse_lazy('ordersapp:orders_list')
    title = 'Geekshop | Заказы/редактирование'

    def get_context_data(self, **kwargs):
        context = super(OrderItemsUpdate, self).get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(Order, OrderItem, OrderItemsForm, extra=1)
        if self.request.POST:
            formset = OrderFormSet(self.request.POST, instance=self.object)
        else:
            queryset = self.object.orderitems.select_related()
            formset = OrderFormSet(instance=self.object, queryset=queryset)
            for form in formset:
                if form.instance.pk:
                    form.initial['price'] = form.instance.product.price
        context['orderitems'] = formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']
        with transaction.atomic():
            self.object = form.save()
            if orderitems.is_valid():
                orderitems.instance = self.object
                orderitems.save()
            if self.object.get_total_cost() == 0:
                self.object.delete()
        return super(OrderItemsUpdate, self).form_valid(form)


class OrderDelete(DeleteView, BaseClassContextMixin):
    model = Order
    success_url = reverse_lazy('ordersapp:orders_list')
    title = 'Geekshop | Заказы/удаление'


class OrderRead(DetailView, BaseClassContextMixin):
    model = Order
    title = 'Geekshop | Заказы/просмотр'


def order_forming_complete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = Order.SENT_TO_PROCEED
    order.save()
    return HttpResponseRedirect(reverse('ordersapp:orders_list'))


def get_product_price(request, pk):
    if request.is_ajax():
        product = Product.objects.filter(pk=int(pk)).first()
        if product:
            return JsonResponse({'price': product.price})
        else:
            return JsonResponse({'price': 0})
