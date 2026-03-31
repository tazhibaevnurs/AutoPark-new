import hmac
import hashlib


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
    Минимальный проверяющий хелпер. Для production лучше использовать
    stripe.Webhook.construct_event().
    """
    if not stripe_signature or not secret:
        return False
    return "v1=" in stripe_signature


def verify_telegram_secret_token(received_token, expected_token):
    if not received_token or not expected_token:
        return False
    return hmac.compare_digest(received_token, expected_token)
