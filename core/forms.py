import json

from django import forms


class CookieConsentPayloadForm(forms.Form):
    action = forms.ChoiceField(
        choices=(("accept", "accept"), ("reject", "reject")),
        required=True,
        error_messages={
            "required": 'Поле "action" обязательно.',
            "invalid_choice": 'Поле "action" должно быть "accept" или "reject".',
        },
    )

    @classmethod
    def from_request_body(cls, body_bytes):
        if not body_bytes:
            return cls({})
        try:
            payload = json.loads(body_bytes)
        except json.JSONDecodeError:
            raise forms.ValidationError("Невалидный JSON в теле запроса.")
        if not isinstance(payload, dict):
            raise forms.ValidationError("JSON-тело должно быть объектом.")
        if set(payload.keys()) - {"action"}:
            raise forms.ValidationError('Разрешено только поле "action".')
        return cls(payload)
