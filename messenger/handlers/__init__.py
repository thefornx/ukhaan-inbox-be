from messenger.handlers.message import handle_message
from messenger.handlers.postback import handle_postback


def dispatch(event, messaging):
    if event.event_type == 'message' and event.text:
        handle_message(event)
    elif event.event_type == 'postback':
        handle_postback(event, messaging)
