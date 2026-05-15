import graphene

from account.graphql.types import UserType
from account.models import Page, User, UserPages
from core.services.authentication import Authentication
from core.services.facebook import Facebook

class AuthenticateMutation(graphene.Mutation):
    class Arguments:
        code = graphene.String(required=True)

    me = graphene.Field(UserType)
    access_token = graphene.String()

    @classmethod
    def mutate(cls, root, info, code, **kwargs):
        provider = Facebook()

        fb_access_token = provider.get_access_token(code)
        user_info = provider.get_user_info(fb_access_token)

        # Create or update user
        user, created = User.objects.update_or_create(
            facebook_id=user_info['id'],
            defaults={
                'name': user_info['name'],
                'picture_url': user_info['picture']['data']['url']
            }
        )

        user.refresh_from_db()

        # Sync user's Facebook pages
        accounts = provider.get_user_accounts(fb_access_token)
        for account in accounts.get('data', []):
            page, _ = Page.objects.update_or_create(
                facebook_id=account['id'],
                defaults={
                    'access_token': account['access_token'],
                    'name': account['name'],
                    'picture_url': account['picture']['data']['url'],
                }
            )
            UserPages.objects.get_or_create(user=user, page=page)

        access_token = Authentication().generate(user.id)

        return AuthenticateMutation(me=user, access_token=access_token)
