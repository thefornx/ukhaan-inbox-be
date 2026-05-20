from account.models import Page
from core.services.assistant import Assistant


def handle_postback(event, messaging):
    payload = (messaging.get('postback') or {}).get('payload', '')
    if not payload:
        return
    page = Page.objects.filter(facebook_id=event.page_facebook_id).first()
    if not page:
        return
    try:
        Assistant(page).handle_postback(event.psid, payload)
    except Exception as exc:
        print(f'[messenger.handlers.postback] {exc}')
