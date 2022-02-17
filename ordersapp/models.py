from django.conf import settings
from django.db import models
from mainapp.models import Product


class Order(models.Model):
    FORMING = 'FM'
    SENT_TO_PROCEED = 'STP'
    PROCEEDED = 'PRD'
    PAID = 'PD'
    READY = 'RDY'
    CANCEL = 'CNC'
    ORDER_STATUS_CHOICES = (
        (FORMING, 'формируется'),
        (SENT_TO_PROCEED, 'отправлен в обработку'),
        (PAID, 'оплачен'),
        (PROCEEDED, 'обрабатывается'),
        (READY, 'готов к выдаче'),
        (CANCEL, 'отменен'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(verbose_name='создан', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='обновлен', auto_now=True)
    status = models.CharField(verbose_name='статус', max_length=3, choices=ORDER_STATUS_CHOICES, default=FORMING)
    is_active = models.BooleanField(verbose_name='активен', db_index=True, default=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'Текущий заказ: {self.pk}'

    def get_summary(self):
        items = self.orderitems.select_related()
        return {'total_cost': sum(list(map(lambda x: x.quantity * x.product.price, items))),
                'total_quantity': sum(list(map(lambda x: x.quantity, items)))}

    # def get_total_quantity(self):
    #     items = self.orderitems.select_related('product')
    #     return sum(list(map(lambda x: x.quantity, items)))

    def get_product_type_quantity(self):
        items = self.orderitems.select_related()
        return len(items)

    # def get_total_cost(self):
    #     items = self.orderitems.select_related('product')
    #     return sum(list(map(lambda x: x.quantity * x.product.price, items)))

    def delete(self):
        for item in self.orderitems.select_related('product'):
            item.product.quantity += item.quantity
            item.product.save()
        self.is_active = False
        self.save()


class OrderItemQuerySet(models.QuerySet):

    def delete(self, *args, **kwargs):
        for object in self:
            object.product.quantity += object.quantity
            object.product.save()
        super(OrderItemQuerySet, self).delete(*args, **kwargs)


class OrderItem(models.Model):
    objects = OrderItemQuerySet.as_manager()
    order = models.ForeignKey(Order, verbose_name='заказ', related_name='orderitems', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='продукт', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='количество', default=0)

    def get_product_cost(self):
        return self.product.price * self.quantity

    def delete(self):
        self.product.quantity += self.quantity
        self.product.save()
        super(OrderItem, self).delete()

    def save(self, *args, **kwargs):
        if self.pk:
            get_object = self.get_object(int(self.pk))
            self.product.quantity -= self.quantity - get_object
        else:
            self.product.quantity -= self.quantity
        self.product.save()
        super(OrderItem, self).save(*args, **kwargs)

    @staticmethod
    def get_object(pk):
        return OrderItem.objects.get(pk=pk).quantity
