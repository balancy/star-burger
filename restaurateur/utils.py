from collections import Counter

from geopy import distance

from geoposition.models import Place


def add_matching_restaurants_to_orders(orders, available_menu_items):
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

    for order in orders:
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
                '{:.3f}'.format(
                    distance.distance(
                        places[order.address],
                        places[restaurant.address],
                    ).km
                ),
            )
            for restaurant in matching_restaurants
        ]

        order.restaurants_with_distances = sorted(
            restaurants_with_distances,
            key=lambda x: x[1],
        )
