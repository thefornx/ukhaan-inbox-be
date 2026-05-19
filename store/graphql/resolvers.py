from graphql import GraphQLError

from store.models import Brand, Branch


def resolve_brands(business):
    return Brand.objects.filter(page=business)


def resolve_brand(business, id):
    try:
        return Brand.objects.get(pk=id, page=business)
    except Brand.DoesNotExist:
        raise GraphQLError('Brand not found')


def resolve_branches(business):
    return Branch.objects.filter(page=business)


def resolve_branch(business, id):
    try:
        return Branch.objects.get(pk=id, page=business)
    except Branch.DoesNotExist:
        raise GraphQLError('Branch not found')
