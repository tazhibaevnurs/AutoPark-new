"""Общая защита форм заявок: honeypot, минимальное время на странице (сессия)."""
import re
import time

from django import forms
from django.conf import settings

# Не принимать POST раньше N секунд после GET (боты шлют мгновенно)
MIN_SECONDS_AFTER_PAGE_LOAD = 2
SESSION_TS_KEY = 'lead_form_started_at'


def _min_seconds_after_page_load():
    return int(
        getattr(settings, 'LEAD_FORM_MIN_SECONDS_AFTER_PAGE_LOAD', MIN_SECONDS_AFTER_PAGE_LOAD)
    )


def validate_person_name(value: str) -> str:
    v = (value or '').strip()
    if len(v) < 2:
        raise forms.ValidationError('Укажите корректное имя (не менее 2 символов).')
    if len(v) > 200:
        raise forms.ValidationError('Имя слишком длинное.')
    if re.search(r'https?://', v, re.I):
        raise forms.ValidationError('Имя не должно содержать ссылки.')
    return v


class LeadAntiSpamMixin(forms.Form):
    """
    hp_company — скрытое поле (не заполнять). Боты часто подставляют значение.
    Проверка времени: в сессии должен быть lead_form_started_at (ставится при GET).
    """

    hp_company = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(
            attrs={
                'class': 'hp-field',
                'tabindex': '-1',
                'autocomplete': 'off',
                'aria-hidden': 'true',
            }
        ),
    )

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        self.fields['hp_company'].widget.attrs.setdefault(
            'style',
            'position:absolute;left:-9999px;width:1px;height:1px;opacity:0;overflow:hidden;',
        )

    def clean(self):
        cleaned = super().clean()
        hp = (cleaned.get('hp_company') or '').strip()
        if hp:
            raise forms.ValidationError(
                'Обнаружена автоматическая отправка. Обновите страницу и отправьте заявку ещё раз.',
                code='honeypot',
            )
        req = self.request
        if req is not None:
            ts = req.session.get(SESSION_TS_KEY)
            if ts is None:
                raise forms.ValidationError(
                    'Сессия формы устарела. Обновите страницу и отправьте заявку снова.',
                    code='no_session',
                )
            if time.time() - float(ts) < _min_seconds_after_page_load():
                raise forms.ValidationError(
                    'Подождите пару секунд перед отправкой — так мы отсекаем автоматические заявки.',
                    code='too_fast',
                )
        return cleaned
