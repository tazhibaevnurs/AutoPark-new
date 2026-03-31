"""
Безопасная работа с куки (Cookies) для управления согласием пользователя.
"""
from django.conf import settings

# ---------- Согласие на cookies (принимается на фронте, дублируется на бэкенде) ----------

COOKIE_CONSENT_NAME = 'cookie_consent_backend'
COOKIE_CONSENT_MAX_AGE = 365 * 24 * 60 * 60  # 1 год
COOKIE_CONSENT_VALUES = ('accepted', 'rejected')


def set_cookie_consent(response, value):
    """
    Устанавливает HttpOnly-куки с выбором пользователя (accepted/rejected).
    Вызывается только после явного согласия/отказа на фронте.
    """
    if value not in COOKIE_CONSENT_VALUES:
        return response
    secure = not getattr(settings, 'DEBUG', True)
    response.set_cookie(
        COOKIE_CONSENT_NAME,
        value,
        max_age=COOKIE_CONSENT_MAX_AGE,
        path='/',
        httponly=True,
        samesite='Lax',
        secure=secure,
    )
    return response


def get_cookie_consent(request):
    """Возвращает 'accepted', 'rejected' или None."""
    raw = request.COOKIES.get(COOKIE_CONSENT_NAME) or ''
    return raw if raw in COOKIE_CONSENT_VALUES else None


def delete_cookie_consent(response):
    """Удаляет куки согласия (например при сбросе настроек)."""
    secure = not getattr(settings, 'DEBUG', True)
    response.set_cookie(
        COOKIE_CONSENT_NAME,
        '',
        max_age=0,
        path='/',
        httponly=True,
        samesite='Lax',
        secure=secure,
        expires='Thu, 01 Jan 1970 00:00:00 GMT',
    )
    return response
