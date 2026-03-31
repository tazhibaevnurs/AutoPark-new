import hmac
import hashlib
import time


def verify_hmac_sha256_signature(raw_body, provided_signature, secret):
    if not provided_signature or not secret:
        return False
    expected = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, provided_signature)


def verify_stripe_signature(raw_body, stripe_signature, secret):
    """
    Проверка Stripe-Signature в формате: t=timestamp,v1=signature.
    Для production endpoint'а всё равно рекомендуется stripe.Webhook.construct_event().
    """
    if not stripe_signature or not secret:
        return False
    parts = {}
    for segment in stripe_signature.split(","):
        if "=" not in segment:
            continue
        key, value = segment.split("=", 1)
        parts.setdefault(key.strip(), []).append(value.strip())

    timestamp_values = parts.get("t") or []
    signature_values = parts.get("v1") or []
    if not timestamp_values or not signature_values:
        return False

    try:
        timestamp = int(timestamp_values[0])
    except ValueError:
        return False

    # Базовая защита от replay: 5 минут.
    if abs(int(time.time()) - timestamp) > 300:
        return False

    signed_payload = f"{timestamp}.{raw_body.decode('utf-8')}".encode("utf-8")
    expected = hmac.new(
        secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    return any(hmac.compare_digest(expected, candidate) for candidate in signature_values)


def verify_telegram_secret_token(received_token, expected_token):
    if not received_token or not expected_token:
        return False
    return hmac.compare_digest(received_token, expected_token)
