import graphene
from graphene_django import DjangoObjectType

from order.models import Order, OrderItem


class OrderItemType(DjangoObjectType):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderType(DjangoObjectType):
    items = graphene.List(OrderItemType)

    class Meta:
        model = Order
        fields = '__all__'

    @staticmethod
    def resolve_items(parent, info):
        return parent.items.all()
