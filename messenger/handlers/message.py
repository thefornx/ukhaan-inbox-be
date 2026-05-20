from account.models import Page
from core.services.assistant import Assistant


def handle_message(event):
    page = Page.objects.filter(facebook_id=event.page_facebook_id).first()
    if not page:
        return
    try:
        Assistant(page).respond(event.psid, event.text)
    except Exception as exc:
        print(f'[messenger.handlers.message] {exc}')
