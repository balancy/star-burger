from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = RestaurantMenuItem.objects.filter(
            availability=True
        ).values_list('product')
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    image = models.ImageField('картинка')
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже', default=True, db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [['restaurant', 'product']]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def with_total_prices(self):
        return self.annotate(
            total_price=Sum(
                F('order_positions__quantity') * F('order_positions__price')
            )
        )


class Order(models.Model):
    first_name = models.CharField('имя', max_length=50)

    last_name = models.CharField('фамилия', max_length=50)

    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )

    contact_phone = PhoneNumberField('номер телефона')

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        related_name='orders',
        verbose_name='ресторан',
        null=True,
        blank=True,
    )

    class OrderStatus(models.TextChoices):
        PROCESSED = 'PROCESSED', _('Обработанный')
        UNPROCESSED = 'UNPROCESSED', _('Необработанный')

    status = models.CharField(
        max_length=11,
        choices=OrderStatus.choices,
        default=OrderStatus.UNPROCESSED,
        verbose_name='статус',
    )

    comment = models.TextField("комментарий", blank=True, max_length=200)

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'Заказ от {self.first_name} {self.last_name}'


class OrderPosition(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_positions',
        verbose_name='продукт',
    )

    quantity = models.IntegerField(
        'количество', default=1, validators=[MinValueValidator(1)]
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_positions',
        verbose_name='заказ',
    )

    price = models.DecimalField(
        'стоимость',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
    )

    class Meta:
        verbose_name = 'позиция заказа'
        verbose_name_plural = 'позиции заказа'

    def __str__(self):
        return f'{self.__class__.__name__}, {self.quantity} {self.product}'
