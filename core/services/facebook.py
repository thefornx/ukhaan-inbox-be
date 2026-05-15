from django.conf import settings
import requests

class Facebook:
    base_url = 'https://graph.facebook.com/v25.0'
    redirect_uri = 'http://localhost:3000/callback'

    def __init__(self):
        self.app_id = settings.FACEBOOK.get('APP_ID')
        self.app_secret = settings.FACEBOOK.get('APP_SECRET')

    def get_access_token(self, code):
        params = {
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "redirect_uri": self.redirect_uri,
            "code": code
        }

        response = requests.get(self.base_url + '/oauth/access_token', params=params)

        print(response.json())

        return response.json()['access_token']

    def get_user_info(self, access_token):
        params = {
            "fields": "id,name,picture",
            "access_token": access_token
        }

        response = requests.get(self.base_url + '/me', params=params)

        return response.json()

    def get_user_accounts(self, access_token):
        params = {
            "fields": "id,name,picture,access_token",
            "access_token": access_token,
            "limit": 20
        }

        response = requests.get(self.base_url + '/me/accounts', params=params)

        return response.json()