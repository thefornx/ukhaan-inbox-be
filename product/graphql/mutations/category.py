import graphene
from graphql import GraphQLError

from core.graphql.decorators.login_required import login_required
from core.graphql.decorators.business_required import business_required
from product.graphql.types import CategoryType
from product.models import Category


class CategoryInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    parent_id = graphene.Int()


def _get_parent(business, parent_id):
    if parent_id is None:
        return None
    try:
        return Category.objects.get(pk=parent_id, page=business)
    except Category.DoesNotExist:
        raise GraphQLError('Parent category not found')


class CreateCategoryMutation(graphene.Mutation):
    class Arguments:
        input = CategoryInput(required=True)

    category = graphene.Field(CategoryType)

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, input):
        business = info.context.business
        data = dict(input)
        parent = _get_parent(business, data.pop('parent_id', None))
        category = Category.objects.create(page=business, parent=parent, **data)
        return CreateCategoryMutation(category=category)


class UpdateCategoryMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = CategoryInput(required=True)

    category = graphene.Field(CategoryType)

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, id, input):
        business = info.context.business
        try:
            category = Category.objects.get(pk=id, page=business)
        except Category.DoesNotExist:
            raise GraphQLError('Category not found')

        data = dict(input)
        if 'parent_id' in data:
            category.parent = _get_parent(business, data.pop('parent_id'))
        for key, value in data.items():
            setattr(category, key, value)
        category.save()

        return UpdateCategoryMutation(category=category)


class DeleteCategoryMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    @business_required
    def mutate(root, info, id):
        deleted, _ = Category.objects.filter(pk=id, page=info.context.business).delete()
        return DeleteCategoryMutation(ok=deleted > 0)
