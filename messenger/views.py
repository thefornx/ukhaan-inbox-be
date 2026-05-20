import json

from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from messenger.models import MessengerLog
from messenger.webhook import Webhook


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def webhook(request):
    pipeline = Webhook()

    if request.method == 'GET':
        challenge = pipeline.verify_subscription(
            request.GET.get('hub.mode'),
            request.GET.get('hub.verify_token'),
            request.GET.get('hub.challenge'),
        )
        if challenge is None:
            return HttpResponseForbidden()
        return HttpResponse(challenge, content_type='text/plain')

    raw = request.body
    sig_header = request.headers.get('X-Hub-Signature-256', '')
    is_valid = pipeline.verify_signature(raw, sig_header)

    try:
        body = json.loads(raw or b'{}')
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON')

    MessengerLog.objects.create(body=body, signature=sig_header, is_valid=is_valid)

    if is_valid:
        pipeline.process(body)

    return JsonResponse({'ok': True})
