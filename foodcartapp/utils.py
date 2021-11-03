import phonenumbers as ph_n

from .models import Product


def check_request_data(data: dict) -> dict:
    """Check if data is correct according to expected rules."""

    # check if fieldnames are presented, not null, not empty and of correct type
    for field, fieldtype in [
        ('products', list),
        ('firstname', str),
        ('lastname', str),
        ('phonenumber', str),
    ]:
        if not field in data:
            return {'error': f'Field <{field}> is required'}

        if data[field] is None:
            return {'error': f'Field <{field}> cannot be null'}

        if not isinstance(data[field], fieldtype):
            return {'error': f'Field <{field}> must be of {fieldtype} type'}

        if not data[field]:
            return {'error': f'Field <{field}> cannot be empty'}

    # check if phone number is correct
    if not ph_n.is_valid_number(ph_n.parse(data['phonenumber'], 'RU')):
        return {'error': 'Field <phonenumber> contains incorrect value'}

    # check if Product ids are correct
    product_ids_in_data = [item['product'] for item in data['products']]
    products_in_db = Product.objects.filter(pk__in=product_ids_in_data)
    if products_in_db.count() != len(product_ids_in_data):
        return {'error': 'Cannot find some of <product> in the db'}

    return data
