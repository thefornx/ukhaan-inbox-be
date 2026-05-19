from functools import wraps

from graphql import GraphQLError

from account.models import Page


def business_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        request = info.context

        business_id = request.META.get('HTTP_X_BUSINESS_ID', '')
        if not business_id:
            raise GraphQLError('Business required')

        try:
            page = Page.objects.get(pk=business_id, is_active=True, is_verified=True)
        except Page.DoesNotExist:
            raise GraphQLError('Business not found')

        request.business = page

        return func(root, info, *args, **kwargs)

    return wrapper
