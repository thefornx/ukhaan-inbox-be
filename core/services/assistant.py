import json

from django.conf import settings
from openai import OpenAI

from core.services.messenger import Messenger
from messenger.models import MessengerEvent
from product.models import Category, Product
from store.models import Branch


class Assistant:
    history_limit = 10

    def __init__(self, page):
        self.page = page
        self.client = OpenAI(api_key=settings.OPENAI['API_KEY'])
        self.model = settings.OPENAI['MODEL']
        self.messenger = Messenger()

    def respond(self, psid, text):
        messages = [
            {'role': 'system', 'content': self._system_prompt()},
            *self._load_history(psid),
            {'role': 'user', 'content': text},
        ]

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self._tools(),
        )
        choice = completion.choices[0].message

        if choice.tool_calls:
            for call in choice.tool_calls:
                args = json.loads(call.function.arguments or '{}')
                self._dispatch_tool(psid, call.function.name, args)
        elif choice.content:
            self._send_text(psid, choice.content)

    def handle_postback(self, psid, payload):
        if payload.startswith('PRODUCT_'):
            self._show_product_detail(psid, payload[len('PRODUCT_'):])
        elif payload.startswith('CATEGORY_'):
            self._show_products(psid, category_id=payload[len('CATEGORY_'):])
        elif payload == 'BRANCHES':
            self._show_branches(psid)
        elif payload == 'CATEGORIES':
            self._show_categories(psid)
        else:
            self.respond(psid, payload)

    def _system_prompt(self):
        return (
            f"Та '{self.page.name}' дэлгүүрийн найрсаг туслах. "
            "Хэрэглэгчтэй Монгол хэлээр товч, эелдгээр ярь. "
            "Хэрэглэгч бараа үзэх, худалдаж авах, эсвэл каталог хүсвэл list_products tool-г дууд. "
            "Ангилал асуувал list_categories, салбар эсвэл байршил асуувал list_branches tool-г дууд. "
            "Бусад мэндчилгээ болон ерөнхий асуултанд эелдгээр текстээр хариул."
        )

    def _tools(self):
        return [
            {
                'type': 'function',
                'function': {
                    'name': 'list_products',
                    'description': 'Show product catalog cards. Call when user wants to browse, view, search, or shop products. Use name for keyword search and price_min/price_max for budget filtering (prices are in Mongolian Tugrik).',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string', 'description': 'Optional keyword to search product name (partial, case-insensitive)'},
                            'category': {'type': 'string', 'description': 'Optional category name to filter'},
                            'brand': {'type': 'string', 'description': 'Optional brand name to filter'},
                            'price_min': {'type': 'number', 'description': 'Optional minimum price in MNT'},
                            'price_max': {'type': 'number', 'description': 'Optional maximum price in MNT'},
                        },
                    },
                },
            },
            {
                'type': 'function',
                'function': {
                    'name': 'list_categories',
                    'description': 'Show available product categories when user asks what categories exist.',
                    'parameters': {'type': 'object', 'properties': {}},
                },
            },
            {
                'type': 'function',
                'function': {
                    'name': 'list_branches',
                    'description': 'Show branches with address, phone, and Google Maps link when user asks about store locations or how to find the shop.',
                    'parameters': {'type': 'object', 'properties': {}},
                },
            },
        ]

    def _dispatch_tool(self, psid, tool_name, args):
        if tool_name == 'list_products':
            self._show_products(
                psid,
                name=args.get('name'),
                category=args.get('category'),
                brand=args.get('brand'),
                price_min=args.get('price_min'),
                price_max=args.get('price_max'),
            )
        elif tool_name == 'list_categories':
            self._show_categories(psid)
        elif tool_name == 'list_branches':
            self._show_branches(psid)

    def _show_products(self, psid, name=None, category=None, brand=None, category_id=None, price_min=None, price_max=None):
        qs = (
            Product.objects.filter(page=self.page)
            .select_related('brand', 'category')
            .prefetch_related('variants__images')
        )
        if name:
            qs = qs.filter(name__icontains=name)
        if category_id:
            qs = qs.filter(category_id=category_id)
        if category:
            qs = qs.filter(category__name__icontains=category)
        if brand:
            qs = qs.filter(brand__name__icontains=brand)
        if price_min is not None:
            qs = qs.filter(variants__price__gte=price_min)
        if price_max is not None:
            qs = qs.filter(variants__price__lte=price_max)
        if price_min is not None or price_max is not None:
            qs = qs.distinct()

        products = list(qs[:10])
        if not products:
            self._send_text(psid, 'Уучлаарай, тохирох бараа олдсонгүй.')
            return

        elements = [self._product_element(p) for p in products]
        self.messenger.send_generic_template(self.page.access_token, psid, elements)
        self._record_echo(psid, f'[{len(products)} бараа илгээв]')

    def _show_product_detail(self, psid, product_id):
        try:
            product = (
                Product.objects.select_related('brand', 'category')
                .prefetch_related('variants__images')
                .get(pk=product_id, page=self.page)
            )
        except Product.DoesNotExist:
            self._send_text(psid, 'Уучлаарай, бараа олдсонгүй.')
            return

        self.messenger.send_generic_template(
            self.page.access_token, psid, [self._product_element(product)],
        )
        self._record_echo(psid, f'[бараа {product.id} илгээв]')

    def _product_element(self, product):
        variant = product.variants.all().first()
        image = None
        price = None
        if variant:
            price = variant.price
            image_obj = variant.images.all().first()
            image = image_obj.url if image_obj else None

        subtitle_parts = []
        if price is not None:
            subtitle_parts.append(f'{int(price):,}₮')
        if product.brand:
            subtitle_parts.append(product.brand.name)

        element = {
            'title': product.name[:80],
            'buttons': [
                {
                    'type': 'postback',
                    'title': 'Дэлгэрэнгүй',
                    'payload': f'PRODUCT_{product.id}',
                },
            ],
        }
        subtitle = ' · '.join(subtitle_parts)
        if subtitle:
            element['subtitle'] = subtitle[:80]
        if image:
            element['image_url'] = image
        return element

    def _show_categories(self, psid):
        categories = list(
            Category.objects.filter(page=self.page, parent__isnull=True)[:3]
        )
        if not categories:
            self._send_text(psid, 'Одоогоор ангилал бүртгэгдээгүй байна.')
            return

        buttons = [
            {
                'type': 'postback',
                'title': c.name[:20],
                'payload': f'CATEGORY_{c.id}',
            }
            for c in categories
        ]
        self.messenger.send_button_template(
            self.page.access_token,
            psid,
            'Ямар ангилал сонирхож байна?',
            buttons,
        )
        self._record_echo(psid, '[ангилал илгээв]')

    def _show_branches(self, psid):
        branches = list(Branch.objects.filter(page=self.page)[:10])
        if not branches:
            self._send_text(psid, 'Салбар бүртгэгдээгүй байна.')
            return

        elements = [self._branch_element(b) for b in branches]
        self.messenger.send_generic_template(self.page.access_token, psid, elements)
        self._record_echo(psid, '[салбар илгээв]')

    def _branch_element(self, branch):
        subtitle_parts = []
        if branch.address_text:
            subtitle_parts.append(branch.address_text)
        if branch.phone:
            subtitle_parts.append(branch.phone)

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

        element = {'title': branch.name[:80]}
        subtitle = ' · '.join(subtitle_parts)
        if subtitle:
            element['subtitle'] = subtitle[:80]
        if buttons:
            element['buttons'] = buttons[:3]
        return element

    def _load_history(self, psid):
        events = list(
            MessengerEvent.objects.filter(
                page_facebook_id=self.page.facebook_id,
                psid=psid,
                event_type__in=('message', 'echo'),
                text__isnull=False,
            ).order_by('-id')[:self.history_limit]
        )
        return [
            {
                'role': 'assistant' if event.is_echo or event.event_type == 'echo' else 'user',
                'content': event.text,
            }
            for event in reversed(events)
        ]

    def _send_text(self, psid, text):
        self.messenger.send_message(self.page.access_token, psid, text)
        self._record_echo(psid, text)

    def _record_echo(self, psid, text):
        MessengerEvent.objects.create(
            page_facebook_id=self.page.facebook_id,
            psid=psid,
            event_type='echo',
            text=text,
            payload={},
            is_echo=True,
        )
