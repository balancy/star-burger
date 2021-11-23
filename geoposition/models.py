from django.db import models


class Place(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
        unique=True,
    )

    latitude = models.DecimalField(
        'широта',
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        'долгота',
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(
        'дата обновления координат',
        auto_now=True,
    )

    class Meta:
        verbose_name = 'место с координатами'
        verbose_name_plural = 'места с координатами'

    def __str__(self):
        return self.address
