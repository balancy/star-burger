# Generated by Django 3.2 on 2021-11-23 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoposition', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='latitude',
            field=models.DecimalField(decimal_places=3, max_digits=6, null=True, verbose_name='широта'),
        ),
        migrations.AlterField(
            model_name='place',
            name='longitude',
            field=models.DecimalField(decimal_places=3, max_digits=6, null=True, verbose_name='долгота'),
        ),
    ]
