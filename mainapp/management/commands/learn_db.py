from django.core.management.base import BaseCommand
from mainapp.models import ProductCategory, Product
from django.db import connection
from django.db.models import Q


def db_profile_by_type(prefix, type, queries):
    update_queries = list(filter(lambda x: type in x['sql'], queries))
    print(f'db_profile {type} for {prefix}:')
    [print(query['sql']) for query in update_queries]


class Command(BaseCommand):
    def handle(self, *args, **options):
        test_products = Product.objects.filter(Q(category__name='Одежда') | Q(category__name='Обувь'))
        print(len(test_products))
        db_profile_by_type('learn db', '', connection.queries)
