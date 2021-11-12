from collections import Counter

from django import forms
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View


from foodcartapp.models import Order, Product, Restaurant, RestaurantMenuItem


class Login(forms.Form):
    username = forms.CharField(
        label='Логин',
        max_length=75,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Укажите имя пользователя',
            }
        ),
    )
    password = forms.CharField(
        label='Пароль',
        max_length=75,
        required=True,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}
        ),
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={'form': form})

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(
            request,
            "login.html",
            context={
                'form': form,
                'ivalid': True,
            },
        )


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{
                item.restaurant_id: item.availability
                for item in product.menu_items.all()
            },
        }
        orderer_availability = [
            availability[restaurant.id] for restaurant in restaurants
        ]

        products_with_restaurants.append((product, orderer_availability))

    return render(
        request,
        template_name="products_list.html",
        context={
            'products_with_restaurants': products_with_restaurants,
            'restaurants': restaurants,
        },
    )


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(
        request,
        template_name="restaurants_list.html",
        context={
            'restaurants': Restaurant.objects.all(),
        },
    )


def populate_orders_with_matching_restaurants(orders):
    """Populate orders with matching restaurants (Restaurants that could handle
    all corresponding order positions).

    Args:
        orders: orders queryset
    """

    available_menu_items = RestaurantMenuItem.objects.select_related(
        'restaurant',
        'product',
    ).filter(availability=True)

    for order in orders:
        order_products = [
            order_position.product
            for order_position in order.order_positions.all()
        ]

        restaurants_with_at_least_one_item = [
            menu_item.restaurant
            for menu_item in available_menu_items
            if menu_item.product in order_products
        ]

        order.matching_restaurants = [
            restaurant
            for restaurant, total_items in Counter(
                restaurants_with_at_least_one_item
            ).items()
            if total_items >= len(order_products)
        ]


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    UNPROCESSED = 'UNPROCESSED'

    orders = (
        Order.objects.prefetch_related('order_positions__product')
        .filter(status=UNPROCESSED)
        .with_total_prices()
    )

    populate_orders_with_matching_restaurants(orders)

    return render(
        request,
        template_name='order_items.html',
        context={
            'order_items': orders,
        },
    )
