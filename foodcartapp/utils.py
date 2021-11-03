def check_request_data(data: dict) -> dict:
    """Check if data is correct according to expected rules."""

    if not 'products' in data:
        return {'error': 'Field <products> is required'}

    if data['products'] is None:
        return {'error': 'Field <products> cannot be null'}

    if isinstance(data['products'], list) and not data['products']:
        return {'error': 'Field <products> cannot be an empty list'}

    if not isinstance(data['products'], list):
        return {'error': 'Field <products> must be a list'}

    return data
