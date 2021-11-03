import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import Order, OrderPosition, Product
from .utils import check_request_data


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse(
        [
            {
                'title': 'Burger',
                'src': static('burger.jpg'),
                'text': 'Tasty Burger at your door step',
            },
            {
                'title': 'Spices',
                'src': static('food.jpg'),
                'text': 'All Cuisines',
            },
            {
                'title': 'New York',
                'src': static('tasty.jpg'),
                'text': 'Food is incomplete without a tasty dessert',
            },
        ],
        safe=False,
        json_dumps_params={
            'ensure_ascii': False,
            'indent': 4,
        },
    )


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            },
        }
        dumped_products.append(dumped_product)
    return JsonResponse(
        dumped_products,
        safe=False,
        json_dumps_params={
            'ensure_ascii': False,
            'indent': 4,
        },
    )


@api_view(['POST'])
def register_order(request):
    order_data = check_request_data(request.data)

    if not 'error' in order_data:
        new_order = Order(
            first_name=order_data['firstname'],
            last_name=order_data['lastname'],
            address=order_data.get('address', ''),
            contact_phone=order_data['phonenumber'],
        )
        new_order.save()

        order_positions = (
            OrderPosition(
                product=Product.objects.get(id=item['product']),
                order=new_order,
                quantity=item['quantity'],
            )
            for item in order_data['products']
        )

        OrderPosition.objects.bulk_create(order_positions)

    return Response(order_data)
