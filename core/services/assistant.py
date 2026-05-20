import json

from django.conf import settings
from openai import OpenAI

from core.helpers.tools import TOOLS
from core.services.messenger import Messenger
from messenger.cards import branch_card, category_button, order_receipt, product_card
from messenger.models import MessengerEvent
from order.services import add_to_cart, get_open_cart
from product.models import Category, Product
from store.models import Branch


SYSTEM_PROMPT = (
    "Та '{page}' дэлгүүрийн найрсаг туслах. "
    "Хэрэглэгчтэй Монгол хэлээр товч, эелдгээр ярь. "
    "Бараа үзэх хүсвэл list_products, ангилал асуувал list_categories, "
    "салбар эсвэл байршил асуувал list_branches tool-г дууд."
)
HISTORY_LIMIT = 10
CARD_LIMIT = 10
CATEGORY_LIMIT = 3


class Assistant:
    def __init__(self, page):
        self.page = page
        self.openai = OpenAI(api_key=settings.OPENAI['API_KEY'])
        self.model = settings.OPENAI['MODEL']
        self.messenger = Messenger()

    def respond(self, psid, text):
        completion = self.openai.chat.completions.create(
            model=self.model,
            messages=self._messages(psid, text),
            tools=TOOLS,
        )
        msg = completion.choices[0].message

        if msg.tool_calls:
            for call in msg.tool_calls:
                args = json.loads(call.function.arguments or '{}')
                self._invoke_tool(psid, call.function.name, args)
        elif msg.content:
            self._send_text(psid, msg.content)

    def handle_postback(self, psid, payload):
        if payload.startswith('PRODUCT_'):
            self._show_product(psid, payload.removeprefix('PRODUCT_'))
        elif payload.startswith('CATEGORY_'):
            self._list_products(psid, category_id=payload.removeprefix('CATEGORY_'))
        elif payload.startswith('ADD_TO_CART_'):
            self._add_to_cart(psid, payload.removeprefix('ADD_TO_CART_'))
        elif payload == 'CATEGORIES':
            self._list_categories(psid)
        elif payload == 'BRANCHES':
            self._list_branches(psid)
        elif payload == 'GET_ORDER':
            self._show_order(psid)
        else:
            self.respond(psid, payload)

    def _messages(self, psid, text):
        return [
            {'role': 'system', 'content': SYSTEM_PROMPT.format(page=self.page.name)},
            *self._history(psid),
            {'role': 'user', 'content': text},
        ]

    def _history(self, psid):
        events = list(
            MessengerEvent.objects.filter(
                page_facebook_id=self.page.facebook_id,
                psid=psid,
                event_type__in=('message', 'echo'),
                text__isnull=False,
            ).order_by('-id')[:HISTORY_LIMIT]
        )
        return [
            {'role': 'assistant' if e.is_echo else 'user', 'content': e.text}
            for e in reversed(events)
        ]

    def _invoke_tool(self, psid, name, args):
        if name == 'list_products':
            self._list_products(psid, **args)
        elif name == 'list_categories':
            self._list_categories(psid)
        elif name == 'list_branches':
            self._list_branches(psid)
        elif name == 'get_order':
            self._show_order(psid)

    def _list_products(self, psid, name=None, category=None, brand=None,
                       category_id=None, price_min=None, price_max=None):
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

        products = list(qs[:CARD_LIMIT])
        if not products:
            return self._send_text(psid, 'Уучлаарай, тохирох бараа олдсонгүй.')

        self._send_cards(psid, [product_card(p) for p in products], f'[{len(products)} бараа]')

    def _show_product(self, psid, product_id):
        product = (
            Product.objects.select_related('brand', 'category')
            .prefetch_related('variants__images')
            .filter(pk=product_id, page=self.page)
            .first()
        )
        if not product:
            return self._send_text(psid, 'Уучлаарай, бараа олдсонгүй.')

        self._send_cards(psid, [product_card(product)], f'[бараа {product.id}]')

    def _list_categories(self, psid):
        categories = list(
            Category.objects.filter(page=self.page, parent__isnull=True)[:CATEGORY_LIMIT]
        )
        if not categories:
            return self._send_text(psid, 'Одоогоор ангилал бүртгэгдээгүй байна.')

        self.messenger.send_button_template(
            self.page.access_token, psid,
            'Ямар ангилал сонирхож байна?',
            [category_button(c) for c in categories],
        )
        self._log_echo(psid, '[ангилал]')

    def _list_branches(self, psid):
        branches = list(Branch.objects.filter(page=self.page)[:CARD_LIMIT])
        if not branches:
            return self._send_text(psid, 'Салбар бүртгэгдээгүй байна.')

        self._send_cards(psid, [branch_card(b) for b in branches], '[салбар]')

    def _add_to_cart(self, psid, product_id):
        product = Product.objects.filter(pk=product_id, page=self.page).first()
        if not product:
            return self._send_text(psid, 'Уучлаарай, бараа олдсонгүй.')

        cart = add_to_cart(self.page, psid, product)
        self._send_text(
            psid,
            f'"{product.name}" сагсанд нэмэгдлээ. Нийт {int(cart.total):,}₮',
        )

    def _show_order(self, psid):
        order = get_open_cart(self.page, psid)
        if not order or not order.items.exists():
            return self._send_text(psid, 'Сагс хоосон байна.')

        self.messenger.send_template(
            self.page.access_token, psid, order_receipt(order),
        )
        self._log_echo(psid, f'[захиалга {order.id}]')

    def _send_cards(self, psid, cards, echo):
        self.messenger.send_generic_template(self.page.access_token, psid, cards)
        self._log_echo(psid, echo)

    def _send_text(self, psid, text):
        self.messenger.send_message(self.page.access_token, psid, text)
        self._log_echo(psid, text)

    def _log_echo(self, psid, text):
        MessengerEvent.objects.create(
            page_facebook_id=self.page.facebook_id,
            psid=psid,
            event_type='echo',
            text=text,
            payload={},
            is_echo=True,
        )
