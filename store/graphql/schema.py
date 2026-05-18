import graphene

from core.graphql.decorators.login_required import login_required
from store.graphql.mutations.create_brand import CreateBrandMutation
from store.graphql.mutations.update_brand import UpdateBrandMutation
from store.graphql.mutations.delete_brand import DeleteBrandMutation
from store.graphql.mutations.create_branch import CreateBranchMutation
from store.graphql.mutations.update_branch import UpdateBranchMutation
from store.graphql.mutations.delete_branch import DeleteBranchMutation
from store.graphql.resolvers import (
    resolve_brand,
    resolve_brands,
    resolve_branch,
    resolve_branches,
)
from store.graphql.types import BrandType, BranchType


class Query(graphene.ObjectType):
    brands = graphene.List(BrandType, page_id=graphene.ID())
    brand = graphene.Field(BrandType, id=graphene.ID(required=True))

    branches = graphene.List(BranchType, page_id=graphene.ID())
    branch = graphene.Field(BranchType, id=graphene.ID(required=True))

    @staticmethod
    @login_required
    def resolve_brands(root, info, page_id=None, **kwargs):
        return resolve_brands(root, info, page_id=page_id, **kwargs)

    @staticmethod
    @login_required
    def resolve_brand(root, info, id, **kwargs):
        return resolve_brand(root, info, id=id, **kwargs)

    @staticmethod
    @login_required
    def resolve_branches(root, info, page_id=None, **kwargs):
        return resolve_branches(root, info, page_id=page_id, **kwargs)

    @staticmethod
    @login_required
    def resolve_branch(root, info, id, **kwargs):
        return resolve_branch(root, info, id=id, **kwargs)


class Mutation(graphene.ObjectType):
    create_brand = CreateBrandMutation.Field()
    update_brand = UpdateBrandMutation.Field()
    delete_brand = DeleteBrandMutation.Field()

    create_branch = CreateBranchMutation.Field()
    update_branch = UpdateBranchMutation.Field()
    delete_branch = DeleteBranchMutation.Field()
