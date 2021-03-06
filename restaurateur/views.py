from django import forms
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from foodcartapp.models import Order, Product, Restaurant, RestaurantMenuItem
from geoposition.handle_coordinates import (
    fill_db_with_missing_places,
    get_places_missing_in_db,
)


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


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    apikey = settings.YANDEX_API_TOKEN

    available_menu_items = RestaurantMenuItem.objects.select_related(
        'restaurant',
        'product',
    ).filter(availability=True)

    orders = (
        Order.objects.prefetch_related('order_positions__product')
        .filter(status='UNPROCESSED')
        .with_total_prices()
    )

    missing_places = get_places_missing_in_db(orders, available_menu_items)
    if missing_places:
        fill_db_with_missing_places(missing_places, apikey)

    orders.add_restaurants_with_distances(available_menu_items)

    return render(
        request,
        template_name='order_items.html',
        context={
            'order_items': orders,
        },
    )
