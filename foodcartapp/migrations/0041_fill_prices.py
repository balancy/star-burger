# Generated by Django 3.2 on 2021-11-04 14:15

from django.db import migrations
from django.db.models import F


def fill_prices_in_order_positions(apps, schema_editor):
    OrderPosition = apps.get_model('foodcartapp', 'OrderPosition')
    order_positions = OrderPosition.objects.select_related('product')

    for position in order_positions.iterator():
        position.price = position.product.price
        position.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_orderposition_price'),
    ]

    operations = [
        migrations.RunPython(fill_prices_in_order_positions),
    ]
