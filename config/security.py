import random
import json
import logging
from dataclasses import dataclass

from django.core.cache import cache


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after_seconds: int


security_logger = logging.getLogger("security.audit")


def get_client_ip(request):
    forwarded = (request.META.get("HTTP_X_FORWARDED_FOR") or "").strip()
    if forwarded:
        return forwarded.split(",")[0].strip()
    return (request.META.get("REMOTE_ADDR") or "").strip() or "unknown"


def _cache_key(scope, identity):
    return f"ratelimit:{scope}:{identity}"


def check_rate_limit(scope, identity, limit, window_seconds):
    key = _cache_key(scope, identity)
    count = cache.get(key, 0)
    if count >= limit:
        return RateLimitResult(
            allowed=False,
            remaining=0,
            retry_after_seconds=window_seconds,
        )
    if not cache.add(key, 1, timeout=window_seconds):
        try:
            count = cache.incr(key)
        except ValueError:
            count = 1
            cache.set(key, count, timeout=window_seconds)
    else:
        count = 1
    remaining = max(0, limit - count)
    return RateLimitResult(
        allowed=True,
        remaining=remaining,
        retry_after_seconds=window_seconds,
    )


def clear_rate_limit(scope, identity):
    cache.delete(_cache_key(scope, identity))


def ensure_math_captcha(request, session_prefix):
    q_key = f"{session_prefix}_captcha_question"
    a_key = f"{session_prefix}_captcha_answer"
    question = request.session.get(q_key)
    answer = request.session.get(a_key)
    if question and answer is not None:
        return question, str(answer)
    left = random.randint(1, 9)
    right = random.randint(1, 9)
    request.session[q_key] = f"{left} + {right}"
    request.session[a_key] = left + right
    return request.session[q_key], str(request.session[a_key])


def log_security_event(event_type, **payload):
    message = {
        "event_type": event_type,
        **payload,
    }
    security_logger.info(json.dumps(message, ensure_ascii=False, sort_keys=True))
