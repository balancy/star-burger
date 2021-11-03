from django.core.exceptions import ValidationError
import phonenumbers as ph_n
from rest_framework import serializers

from .models import Order, OrderPosition


class OrderPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPosition
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'address',
            'firstname',
            'lastname',
            'phonenumber',
            'products',
        ]

    id = serializers.IntegerField(read_only=True)
    firstname = serializers.CharField(source='first_name')
    lastname = serializers.CharField(source='last_name')
    phonenumber = serializers.CharField(source='contact_phone')
    products = serializers.ListField(
        child=OrderPositionSerializer(), allow_empty=False, write_only=True
    )

    def validate_phonenumber(self, value):
        if not ph_n.is_valid_number(ph_n.parse(value, 'RU')):
            raise ValidationError('Некорректное значение')
        return value

    def create(self, validated_data):
        return Order.objects.create(**validated_data)
