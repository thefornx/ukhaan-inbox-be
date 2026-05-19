import graphene

from core.graphql.decorators.login_required import login_required
from core.graphql.decorators.business_required import business_required
from store.graphql.mutations.brand import (
    CreateBrandMutation,
    UpdateBrandMutation,
    DeleteBrandMutation,
)
from store.graphql.mutations.branch import (
    CreateBranchMutation,
    UpdateBranchMutation,
    DeleteBranchMutation,
)
from store.graphql.resolvers import (
    resolve_brand,
    resolve_brands,
    resolve_branch,
    resolve_branches,
)
from store.graphql.types import BrandType, BranchType


class Query(graphene.ObjectType):
    brands = graphene.List(BrandType)
    brand = graphene.Field(BrandType, id=graphene.Int(required=True))
    branches = graphene.List(BranchType)
    branch = graphene.Field(BranchType, id=graphene.Int(required=True))

    @staticmethod
    @login_required
    @business_required
    def resolve_brands(_root, info):
        return resolve_brands(info.context.business)

    @staticmethod
    @login_required
    @business_required
    def resolve_brand(_root, info, id):
        return resolve_brand(info.context.business, id)

    @staticmethod
    @login_required
    @business_required
    def resolve_branches(_root, info):
        return resolve_branches(info.context.business)

    @staticmethod
    @login_required
    @business_required
    def resolve_branch(_root, info, id):
        return resolve_branch(info.context.business, id)


class Mutation(graphene.ObjectType):
    create_brand = CreateBrandMutation.Field()
    update_brand = UpdateBrandMutation.Field()
    delete_brand = DeleteBrandMutation.Field()

    create_branch = CreateBranchMutation.Field()
    update_branch = UpdateBranchMutation.Field()
    delete_branch = DeleteBranchMutation.Field()
