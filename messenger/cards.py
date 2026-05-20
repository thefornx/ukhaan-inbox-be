def product_card(product):
    variant = product.variants.all().first()
    price = variant.price if variant else None
    image = None
    if variant:
        image_obj = variant.images.all().first()
        image = image_obj.url if image_obj else None

    parts = []
    if price is not None:
        parts.append(f'{int(price):,}₮')
    if product.brand:
        parts.append(product.brand.name)
    subtitle = ' · '.join(parts)

    card = {
        'title': product.name[:80],
        'buttons': [{
            'type': 'postback',
            'title': 'Дэлгэрэнгүй',
            'payload': f'PRODUCT_{product.id}',
        }],
    }
    if subtitle:
        card['subtitle'] = subtitle[:80]
    if image:
        card['image_url'] = image
    return card


def branch_card(branch):
    parts = []
    if branch.address_text:
        parts.append(branch.address_text)
    if branch.phone:
        parts.append(branch.phone)

    buttons = []
    if branch.latitude is not None and branch.longitude is not None:
        buttons.append({
            'type': 'web_url',
            'title': 'Газрын зураг',
            'url': f'https://www.google.com/maps?q={branch.latitude},{branch.longitude}',
        })
    if branch.phone:
        buttons.append({
            'type': 'phone_number',
            'title': 'Залгах',
            'payload': branch.phone,
        })
    if branch.website:
        buttons.append({
            'type': 'web_url',
            'title': 'Веб',
            'url': branch.website,
        })

    card = {'title': branch.name[:80]}
    subtitle = ' · '.join(parts)
    if subtitle:
        card['subtitle'] = subtitle[:80]
    if buttons:
        card['buttons'] = buttons[:3]
    return card


def category_button(category):
    return {
        'type': 'postback',
        'title': category.name[:20],
        'payload': f'CATEGORY_{category.id}',
    }
