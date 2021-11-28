from collections import Counter

from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from geopy import distance
from phonenumber_field.modelfields import PhoneNumberField

from geoposition.models import Place


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

    def add_restaurants_with_distances(self, available_menu_items):
        """Add matching restaurants with distances to orders
        (Restaurants that could handle all corresponding order positions).

        Args:
            orders: unprocessed orders
            available_menu_items: all available menu items
        """

        places = {
            place.address: (place.latitude, place.longitude)
            for place in Place.objects.all()
        }

        for order in self:
            order_products = [
                order_position.product
                for order_position in order.order_positions.all()
            ]

            restaurants_with_at_least_one_order_item = [
                menu_item.restaurant
                for menu_item in available_menu_items
                if menu_item.product in order_products
            ]

            matching_restaurants = [
                restaurant
                for restaurant, total_items in Counter(
                    restaurants_with_at_least_one_order_item
                ).items()
                if total_items == len(order_products)
            ]

            restaurants_with_distances = [
                (
                    restaurant,
                    (
                        '{:.3f} км'.format(
                            distance.distance(
                                order_coordinates,
                                places[restaurant.address],
                            ).km
                        )
                    )
                    if not None in (order_coordinates := places[order.address])
                    else 'адрес не распознан',
                )
                for restaurant in matching_restaurants
            ]

            order.restaurants_with_distances = sorted(
                restaurants_with_distances,
                key=lambda x: x[1],
            )

        return self


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PROCESSED = 'PROCESSED', _('Обработанный')
        UNPROCESSED = 'UNPROCESSED', _('Необработанный')

    class OrderPaymentMethod(models.TextChoices):
        CASH = 'CASH', _('Наличностью')
        ONLINE = 'ONLINE', _('Онлайн')
        UNDEFINED = 'UNDEFINED', _('Не указано')

    first_name = models.CharField('имя', max_length=50)
    last_name = models.CharField('фамилия', max_length=50)

    address = models.CharField(
        'адрес',
        max_length=100,
    )

    contact_phone = PhoneNumberField('номер телефона', db_index=True)

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        related_name='orders',
        verbose_name='ресторан',
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=11,
        choices=OrderStatus.choices,
        default=OrderStatus.UNPROCESSED,
        verbose_name='статус',
        db_index=True,
    )

    comment = models.TextField('комментарий', blank=True)

    registered_at = models.DateTimeField(
        'дата регистрации',
        default=timezone.now,
        db_index=True,
    )

    called_at = models.DateTimeField(
        'дата звонка',
        blank=True,
        null=True,
        db_index=True,
    )

    delivered_at = models.DateTimeField(
        'дата доставки',
        blank=True,
        null=True,
        db_index=True,
    )

    payment_method = models.CharField(
        max_length=9,
        choices=OrderPaymentMethod.choices,
        default=OrderPaymentMethod.UNDEFINED,
        verbose_name='способ оплаты',
        db_index=True,
    )

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
        'количество',
        validators=[MinValueValidator(1)],
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
    )

    class Meta:
        verbose_name = 'позиция заказа'
        verbose_name_plural = 'позиции заказа'

    def __str__(self):
        return f'{self.__class__.__name__}, {self.quantity} {self.product}'
