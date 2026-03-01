"""
Безопасная работа с куки (Cookies) для управления сессией пользователя.

Используются флаги:
- httponly: куки недоступны из JavaScript → защита от XSS (кража сессии через скрипт).
- samesite='Lax': куки не отправляются при cross-site POST (переход по ссылке с другого сайта) → снижает риск CSRF.
- secure: куки передаются только по HTTPS → защита от перехвата по незашифрованному каналу.
"""
import uuid
from django.conf import settings

# Имя куки сессии (единое для установки, чтения и удаления)
SESSION_COOKIE_NAME = 'session_token'

# Срок жизни сессии: 30 дней (в секундах)
SESSION_COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 дней


def set_session_cookie(response, value=None):
    """
    Устанавливает куки сессии в ответ (HttpResponse).

    - value: если не передан, генерируется случайный UUID.
    - httponly=True: куки недоступны из document.cookie (защита от XSS).
    - samesite='Lax': куки не уходят при cross-site POST (защита от CSRF).
    - secure: только по HTTPS; в DEBUG отключаем, чтобы работало по http в разработке.
    - max_age: время жизни в секундах (30 дней).
    """
    if value is None:
        value = str(uuid.uuid4())
    # В продакшене (не DEBUG) принудительно только HTTPS
    secure = not getattr(settings, 'DEBUG', True)
    response.set_cookie(
        SESSION_COOKIE_NAME,
        value,
        max_age=SESSION_COOKIE_MAX_AGE,
        httponly=True,   # недоступно из JS → защита от XSS
        samesite='Lax',  # не отправляется при cross-site POST → защита от CSRF
        secure=secure,   # только HTTPS → защита от перехвата по http
    )
    return response


def get_session_cookie(request):
    """
    Безопасное извлечение значения session_token из входящего запроса.

    Возвращает строку токена или None, если куки нет или значение пустое.
    Не выполняет логику валидации токена (это можно добавить отдельно).
    """
    return request.COOKIES.get(SESSION_COOKIE_NAME) or None


def delete_session_cookie(response):
    """
    Корректное удаление куки при выходе (logout).

    Устанавливаем пустое значение и max_age=0 с теми же флагами
    (path, httponly, samesite, secure), что и при установке —
    иначе браузер может не удалить куки.
    """
    secure = not getattr(settings, 'DEBUG', True)
    response.set_cookie(
        SESSION_COOKIE_NAME,
        '',
        max_age=0,
        path='/',
        httponly=True,
        samesite='Lax',
        secure=secure,
        expires='Thu, 01 Jan 1970 00:00:00 GMT',
    )
    return response


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
