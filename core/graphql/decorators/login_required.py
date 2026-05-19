from functools import wraps

from graphql import GraphQLError

from account.models import User
from core.services.authentication import Authentication


def login_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        request = info.context

        header = request.META.get('HTTP_AUTHORIZATION', '')
        scheme, _, token = header.partition(' ')

        if scheme.lower() != 'bearer' or not token:
            raise GraphQLError('Authentication required')

        user_id = Authentication().verify(token)
        if user_id is None:
            raise GraphQLError('Invalid or expired token')

        try:
            request.user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise GraphQLError('User not found')

        return func(root, info, *args, **kwargs)

    return wrapper
