import json

from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from messenger.models import MessengerLog


@csrf_exempt
@require_POST
def webhook(request):
    try:
        body = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON')

    MessengerLog.objects.create(body=body)
    return JsonResponse({'ok': True})
