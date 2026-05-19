import requests


class Messenger:
    base_url = 'https://graph.facebook.com/v25.0'

    def send_message(self, page_access_token, psid, text, messaging_type='RESPONSE'):
        return self._send(
            page_access_token,
            psid,
            {'text': text},
            messaging_type,
        )

    def send_template(self, page_access_token, psid, payload, messaging_type='RESPONSE'):
        message = {
            'attachment': {
                'type': 'template',
                'payload': payload,
            }
        }
        return self._send(page_access_token, psid, message, messaging_type)

    def send_generic_template(self, page_access_token, psid, elements, messaging_type='RESPONSE'):
        payload = {
            'template_type': 'generic',
            'elements': elements,
        }
        return self.send_template(page_access_token, psid, payload, messaging_type)

    def send_button_template(self, page_access_token, psid, text, buttons, messaging_type='RESPONSE'):
        payload = {
            'template_type': 'button',
            'text': text,
            'buttons': buttons,
        }
        return self.send_template(page_access_token, psid, payload, messaging_type)

    def _send(self, page_access_token, psid, message, messaging_type):
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
