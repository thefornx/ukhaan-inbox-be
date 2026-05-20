TOOLS = [
    {
        'type': 'function',
        'function': {
            'name': 'list_products',
            'description': (
                'Show product catalog cards. Call when user wants to browse, '
                'view, search, or shop products. Use name for keyword search '
                'and price_min/price_max for budget filtering. Prices are MNT.'
            ),
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Keyword search on product name (case-insensitive partial match)'},
                    'category': {'type': 'string', 'description': 'Filter by category name'},
                    'brand': {'type': 'string', 'description': 'Filter by brand name'},
                    'price_min': {'type': 'number', 'description': 'Minimum price in MNT'},
                    'price_max': {'type': 'number', 'description': 'Maximum price in MNT'},
                },
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'list_categories',
            'description': 'Show available product categories.',
            'parameters': {'type': 'object', 'properties': {}},
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'list_branches',
            'description': 'Show branches with address, phone, and map link when user asks about store locations.',
            'parameters': {'type': 'object', 'properties': {}},
        },
    },
]
