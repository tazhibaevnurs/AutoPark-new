from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from .security import check_rate_limit, get_client_ip, log_security_event


class AuthRequiredMiddleware:
    """
    Принудительно проверяет аутентификацию на защищённых маршрутах.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.protected_prefixes = tuple(
            getattr(settings, 'AUTH_PROTECTED_PATH_PREFIXES', ('/profile/',))
        )

    def __call__(self, request):
        path = request.path or '/'
        is_protected = any(path.startswith(prefix) for prefix in self.protected_prefixes)
        if is_protected and not request.user.is_authenticated:
            login_url = getattr(settings, 'LOGIN_URL', '/login/')
            return redirect(f'{login_url}?next={path}')
        return self.get_response(request)


class AbuseProtectionMiddleware:
    """
    Глобальная защита API от злоупотреблений и ограничение размеров request body.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.api_rate_limit = int(getattr(settings, "API_RATE_LIMIT_PER_MINUTE", 100))
        self.api_window = 60
        self.api_body_limit = int(getattr(settings, "API_BODY_SIZE_LIMIT_BYTES", 1024 * 1024))
        self.upload_body_limit = int(getattr(settings, "UPLOAD_BODY_SIZE_LIMIT_BYTES", 10 * 1024 * 1024))
        self.suspicious_4xx_limit = int(getattr(settings, "SUSPICIOUS_4XX_PER_IP_10MIN", 30))
        self.anomaly_requests_per_minute = int(getattr(settings, "ANOMALY_REQUESTS_PER_MINUTE", 1500))
        self.allowed_origins = set(getattr(settings, "CORS_ALLOWED_ORIGINS", []))
        self.csp_policy = getattr(settings, "CONTENT_SECURITY_POLICY", "")

    def __call__(self, request):
        content_length = int((request.META.get("CONTENT_LENGTH") or "0") or 0)
        path = request.path or "/"
        content_type = (request.META.get("CONTENT_TYPE") or "").lower()
        ip = get_client_ip(request)
        origin = (request.META.get("HTTP_ORIGIN") or "").strip()

        if path.startswith("/api/") and content_length > self.api_body_limit:
            log_security_event(
                "api_body_too_large",
                path=path,
                ip=ip,
                content_length=content_length,
            )
            return JsonResponse(
                {"ok": False, "error": "Слишком большой API-запрос. Максимум 1MB."},
                status=413,
            )

        if "multipart/form-data" in content_type and content_length > self.upload_body_limit:
            log_security_event(
                "upload_body_too_large",
                path=path,
                ip=ip,
                content_length=content_length,
            )
            return HttpResponse("Слишком большой upload-запрос. Максимум 10MB.", status=413)

        # CORS: только для /api/ — иначе www/apex и моб. браузеры с Origin на GET ломают HTML-страницы.
        if (
            path.startswith("/api/")
            and origin
            and self.allowed_origins
            and origin not in self.allowed_origins
        ):
            log_security_event("cors_blocked_origin", path=path, ip=ip, origin=origin)
            return JsonResponse({"ok": False, "error": "Origin not allowed."}, status=403)

        if path.startswith("/api/"):
            user = getattr(request, "user", None)
            if user and user.is_authenticated:
                identity = f"user:{user.pk}"
            else:
                identity = f"ip:{ip}"
            result = check_rate_limit("api_per_user", identity, self.api_rate_limit, self.api_window)
            if not result.allowed:
                log_security_event("api_rate_limited", path=path, ip=ip, identity=identity)
                response = JsonResponse(
                    {"ok": False, "error": "Слишком много запросов. Повторите позже."},
                    status=429,
                )
                response["Retry-After"] = str(result.retry_after_seconds)
                return response

        minute_rate = check_rate_limit("anomaly_req", ip, self.anomaly_requests_per_minute, 60)
        if not minute_rate.allowed:
            log_security_event(
                "traffic_anomaly_detected",
                path=path,
                ip=ip,
                threshold=self.anomaly_requests_per_minute,
            )

        response = self.get_response(request)
        if origin and origin in self.allowed_origins:
            response["Access-Control-Allow-Origin"] = origin
            response["Vary"] = "Origin"
            response["Access-Control-Allow-Credentials"] = "true"

        if self.csp_policy:
            response["Content-Security-Policy"] = self.csp_policy
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        status_code = getattr(response, "status_code", 200)
        if path.startswith("/api/") and status_code >= 400:
            log_security_event("api_error", path=path, ip=ip, status_code=status_code)

        if status_code in (401, 403):
            suspicious = check_rate_limit("suspicious_4xx", ip, self.suspicious_4xx_limit, 600)
            if not suspicious.allowed:
                log_security_event(
                    "suspicious_4xx_burst",
                    path=path,
                    ip=ip,
                    threshold=self.suspicious_4xx_limit,
                )

        return response
