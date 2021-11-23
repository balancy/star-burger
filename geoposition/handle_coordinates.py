import requests

from .models import Place


def get_missing_in_db_places(orders, menu_items):
    """Return set of places with specified addresses that are not yet in the database.

    Args:
        orders: unprocessed orders
        menu_items: all available menu items
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

    return addresses_not_in_db


def fill_db_with_missing_places(addresses, apikey):
    """Fill the database with places that are not yet in the database. For every
    such place functions make a call to Map API and fetches its coordinates.

    Args:
        addresses: addresses missing in the database
        apikey: yandex api key to fetch coordinates
    """

    places_to_add_to_db = [
        {**{'address': address}, **fetch_coordinates(apikey, address)}
        for address in addresses
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
        return {'latitude': None, 'longitude': None}

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return {'latitude': lat, 'longitude': lon}
