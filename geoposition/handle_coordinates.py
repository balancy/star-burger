import requests

from .models import Place


def check_places_presence_in_db(orders, menu_items, apikey):
    """Check if places with specified addresses are already in the database.
    If at least one place is not in the database, function add the place with
    coordinates to the database.

    Args:
        orders: unprocessed orders
        menu_items: all available menu items
        apikey: yandex api key to fetch coordinates
    """

    addresses_to_check = {order.address for order in orders}.union(
        {item.restaurant.address for item in menu_items}
    )

    places_in_db = Place.objects.filter(address__in=addresses_to_check)

    addresses_not_in_db = {
        address
        for address in addresses_to_check
        if address not in {place.address for place in places_in_db}
    }

    if addresses_not_in_db:
        places_to_add_to_db = [
            {**{'address': address}, **fetch_coordinates(apikey, address)}
            for address in addresses_not_in_db
        ]

        Place.objects.bulk_create(
            [Place(**place_to_add) for place_to_add in places_to_add_to_db]
        )


def fetch_coordinates(apikey, address):
    """Fetch coordinates with yandex api

    Args:
        apikey: yandex api token
        address: address to fetch coordinates for

    Returns:
        dictionary containing coordinates
    """

    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        },
    )
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection'][
        'featureMember'
    ]

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return {'latitude': lat, 'longitude': lon}
