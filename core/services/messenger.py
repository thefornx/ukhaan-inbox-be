import requests


class Messenger:
    base_url = 'https://graph.facebook.com/v25.0'

    def send_message(self, page_access_token, psid, text, quick_replies=None, messaging_type='RESPONSE'):
        return self._send(page_access_token, psid, {'text': text}, quick_replies, messaging_type)

    def send_template(self, page_access_token, psid, payload, quick_replies=None, messaging_type='RESPONSE'):
        message = {'attachment': {'type': 'template', 'payload': payload}}
        return self._send(page_access_token, psid, message, quick_replies, messaging_type)

    def send_generic_template(self, page_access_token, psid, elements, quick_replies=None, messaging_type='RESPONSE'):
        return self.send_template(
            page_access_token, psid,
            {'template_type': 'generic', 'elements': elements},
            quick_replies=quick_replies, messaging_type=messaging_type,
        )

    def send_button_template(self, page_access_token, psid, text, buttons, quick_replies=None, messaging_type='RESPONSE'):
        return self.send_template(
            page_access_token, psid,
            {'template_type': 'button', 'text': text, 'buttons': buttons},
            quick_replies=quick_replies, messaging_type=messaging_type,
        )

    def _send(self, page_access_token, psid, message, quick_replies, messaging_type):
        if quick_replies:
            message = {**message, 'quick_replies': quick_replies}
        response = requests.post(
            self.base_url + '/me/messages',
            params={'access_token': page_access_token},
            json={
                'recipient': {'id': psid},
                'message': message,
                'messaging_type': messaging_type,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
