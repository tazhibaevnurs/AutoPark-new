from django import forms
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from config.cookies import set_cookie_consent
from core.forms import CookieConsentPayloadForm
from core.models import CookieConsent


@method_decorator(require_http_methods(['POST']), name='dispatch')
@method_decorator(ensure_csrf_cookie, name='dispatch')
class CookieConsentView(View):
    """
    Принимает выбор пользователя (принять/отклонить cookies),
    устанавливает HttpOnly-куки на бэкенде и сохраняет запись для аудита.
    """

    def post(self, request):
        content_type = (request.content_type or '').split(';')[0].strip().lower()
        if content_type != 'application/json':
            return JsonResponse(
                {'ok': False, 'error': 'Content-Type должен быть application/json.'},
                status=415,
            )

        try:
            form = CookieConsentPayloadForm.from_request_body(request.body)
        except forms.ValidationError as exc:
            return JsonResponse({'ok': False, 'error': str(exc.message)}, status=400)

        if not form.is_valid():
            return JsonResponse({'ok': False, 'error': form.errors.get('action', ['Некорректные данные'])[0]}, status=400)

        value = 'accepted' if form.cleaned_data['action'] == 'accept' else 'rejected'

        # Сохраняем в БД для аудита (session_key создаёт сессию при первом обращении)
        session_key = (request.session.session_key or '')[:40]
        CookieConsent.objects.create(choice=value, session_key=session_key)

        response = JsonResponse({'ok': True})
        set_cookie_consent(response, value)
        return response
