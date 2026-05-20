from account.models import Page
from core.services.assistant import Assistant


def handle_message(event):
    page = Page.objects.filter(facebook_id=event.page_facebook_id).first()
    if not page:
        return

    quick_reply = (event.payload.get('message') or {}).get('quick_reply') or {}
    payload = quick_reply.get('payload')

    try:
        assistant = Assistant(page)
        if payload:
            assistant.handle_postback(event.psid, payload)
        else:
            assistant.respond(event.psid, event.text)
    except Exception as exc:
        print(f'[messenger.handlers.message] {exc}')
