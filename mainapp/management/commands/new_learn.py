from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Q, F, When, Case, DecimalField, IntegerField
from ordersapp.models import OrderItem
from prettytable import PrettyTable


class Command(BaseCommand):

    def handle(self, *args, **options):
        ACTION_1 = 1
        ACTION_2 = 2
        ACTION_EXPIRED = 3

        action_1__time_delta = timedelta(hours=12)
        action_2__time_delta = timedelta(days=1)

        action_1__discount = 0.3
        action_2__discount = 0.15
        action_expired__discount = 0.05

        action_1__condition = Q(order__updated__lte=F('order__created') + action_1__time_delta)

        action_2__condition = Q(order__updated__gt=F('order__created') + action_1__time_delta) & Q(order__updated__lte=F('order__created') + action_2__time_delta)

        action_expired__condition = Q(order__updated__gt=F('order__created') + action_2__time_delta)

        action_1__order = When(action_1__condition, then=ACTION_1)
        action_2__order = When(action_2__condition, then=ACTION_2)
        action_expired__order = When(action_expired__condition, then=ACTION_EXPIRED)

        action_1__price = When(action_1__condition, then=F('product__price') * F('quantity') * action_1__discount)

        action_2__price = When(action_2__condition, then=F('product__price') * F('quantity') * -action_2__discount)

        action_expired__price = When(action_expired__condition, then=F('product__price') * F('quantity') * action_expired__discount)

        test_orderss = OrderItem.objects.annotate(
            action_order=Case(
                action_1__order,
                action_2__order,
                action_expired__order,
                output_field=IntegerField(),
            )).annotate(
            total_price=Case(
                action_1__price,
                action_2__price,
                action_expired__price,
                output_field=DecimalField(),
            )).order_by('action_order', 'total_price').select_related()

        t_list = PrettyTable(["Заказ", "Товар", "Скидка", 'Разница времени'])
        t_list.align = 'l'
        i = 0
        for orderitem in test_orderss:
            t_list.add_row([f'{orderitem.action_order} заказ №{orderitem.pk:}', f'{orderitem.product.name:15}',
                            f'{abs(orderitem.total_price):6.2f} руб.',
                            orderitem.order.updated - orderitem.order.created])
            if i == 0:
                update_queries = list(filter(lambda x: 'SELECT' in x['sql'], connection.queries))
                print(f'basket_add {update_queries} ')
                i += 1

        print(t_list)
