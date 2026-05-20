import graphene

from core.graphql.decorators.login_required import login_required
from core.graphql.decorators.business_required import business_required
from order.graphql.mutations.order import (
    CreateOrderMutation,
    UpdateOrderMutation,
    DeleteOrderMutation,
)
from order.graphql.resolvers import resolve_orders, resolve_order
from order.graphql.types import OrderType


class Query(graphene.ObjectType):
    orders = graphene.List(OrderType, status=graphene.String())
    order = graphene.Field(OrderType, id=graphene.Int(required=True))

    @staticmethod
    @login_required
    @business_required
    def resolve_orders(_root, info, status=None):
        return resolve_orders(info.context.business, status=status)

    @staticmethod
    @login_required
    @business_required
    def resolve_order(_root, info, id):
        return resolve_order(info.context.business, id)


class Mutation(graphene.ObjectType):
    create_order = CreateOrderMutation.Field()
    update_order = UpdateOrderMutation.Field()
    delete_order = DeleteOrderMutation.Field()
