import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from config.cookies import set_cookie_consent
from core.models import CookieConsent


@method_decorator(require_http_methods(['POST']), name='dispatch')
@method_decorator(ensure_csrf_cookie, name='dispatch')
class CookieConsentView(View):
    """
    Принимает выбор пользователя (принять/отклонить cookies),
    устанавливает HttpOnly-куки на бэкенде и сохраняет запись для аудита.
    """

    def post(self, request):
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

        action = (body.get('action') or '').strip().lower()
        if action == 'accept':
            value = 'accepted'
        elif action == 'reject':
            value = 'rejected'
        else:
            return JsonResponse({'ok': False, 'error': 'action must be "accept" or "reject"'}, status=400)

        # Сохраняем в БД для аудита (session_key создаёт сессию при первом обращении)
        session_key = (request.session.session_key or '')[:40]
        CookieConsent.objects.create(choice=value, session_key=session_key)

        response = JsonResponse({'ok': True})
        set_cookie_consent(response, value)
        return response
