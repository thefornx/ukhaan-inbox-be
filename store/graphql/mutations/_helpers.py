from graphql import GraphQLError

from account.models import Page


def get_user_page(user, page_id):
    page = Page.objects.filter(pk=page_id, users=user).first()
    if page is None:
        raise GraphQLError('Page not found')
    return page


def get_owned_or_raise(model, user, pk):
    obj = model.objects.filter(
        pk=pk,
        page__users=user,
    ).first()
    if obj is None:
        raise GraphQLError(f'{model.__name__} not found')
    return obj
