# Generated by Django 3.2 on 2021-11-08 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_fill_prices'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, max_length=200, verbose_name='комментарий'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('PROCESSED', 'Обработанный'), ('UNPROCESSED', 'Необработанный')], default='UNPROCESSED', max_length=11, verbose_name='статус'),
        ),
    ]
