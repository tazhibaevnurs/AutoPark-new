import re
from django import forms
from .models import Lead, CarSearchRequest, BuyoutRequest, DeliveryRequest, RegistrationRequest

MAX_COMMENT_LENGTH = 2000
MAX_MESSAGE_LENGTH = 2000


class LeadForm(forms.ModelForm):
    """Форма заявки «Заказать авто» с валидацией телефона и бюджета."""

    country = forms.ChoiceField(
        label='Страна',
        choices=[('', 'Выберите страну')] + list(Lead.Country.choices),
        required=True,
    )

    captcha_answer = forms.CharField(required=True, label='Сколько будет?')

    def __init__(self, *args, expected_captcha=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_captcha = (expected_captcha or '').strip()

    class Meta:
        model = Lead
        fields = [
            'country', 'budget', 'body_type', 'urgency',
            'name', 'phone', 'contact', 'comment',
        ]
        widgets = {
            'country': forms.Select(attrs={'id': 'id_country'}),
            'budget': forms.TextInput(attrs={
                'id': 'id_budget',
                'placeholder': 'Например: 3 000 000',
            }),
            'body_type': forms.Select(attrs={'id': 'id_body_type'}),
            'urgency': forms.Select(attrs={'id': 'id_urgency'}),
            'name': forms.TextInput(attrs={'id': 'id_name'}),
            'phone': forms.TextInput(attrs={
                'id': 'id_phone',
                'type': 'tel',
                'placeholder': '+7 (999) 123-45-67',
            }),
            'contact': forms.TextInput(attrs={
                'id': 'id_contact',
                'placeholder': '@username или номер',
            }),
            'comment': forms.Textarea(attrs={
                'id': 'id_comment',
                'rows': 3,
                'placeholder': 'Марка, модель, год — если уже есть пожелания',
            }),
        }

    def clean_phone(self):
        value = self.cleaned_data.get('phone') or ''
        digits = re.sub(r'\D', '', value)
        if len(digits) < 10:
            raise forms.ValidationError('Введите корректный номер телефона.')
        if digits.startswith('8'):
            digits = '7' + digits[1:]
        elif not digits.startswith('7'):
            digits = '7' + digits
        return '+7' + digits[-10:].rjust(10, '0')

    def clean_budget(self):
        value = self.cleaned_data.get('budget') or ''
        return value.strip() or '—'

    def clean_comment(self):
        value = (self.cleaned_data.get('comment') or '').strip()
        if len(value) > MAX_COMMENT_LENGTH:
            raise forms.ValidationError(f'Комментарий слишком длинный (максимум {MAX_COMMENT_LENGTH} символов).')
        return value

    def clean_captcha_answer(self):
        value = (self.cleaned_data.get('captcha_answer') or '').strip()
        if not self.expected_captcha or value != self.expected_captcha:
            raise forms.ValidationError('Неверный ответ CAPTCHA.')
        return value


class CarSearchForm(forms.ModelForm):
    """Форма заявки на поиск автомобиля."""

    class Meta:
        model = CarSearchRequest
        fields = ['name', 'phone', 'email', 'message', 'consent']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Ваше имя',
                'autocomplete': 'name',
            }),
            'phone': forms.TextInput(attrs={
                'type': 'tel',
                'placeholder': '+7 (999) 123-45-67',
                'autocomplete': 'tel',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email (необязательно)',
                'autocomplete': 'email',
            }),
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Опишите желаемый автомобиль: марка, модель, год, бюджет, комплектация, страна (США/Китай/Корея)...',
            }),
            'consent': forms.CheckboxInput(attrs={'required': True}),
        }
        labels = {
            'name': 'Имя',
            'phone': 'Телефон',
            'email': 'Email',
            'message': 'Опишите желаемый автомобиль',
            'consent': 'Я соглашаюсь с политикой конфиденциальности',
        }

    def clean_phone(self):
        value = self.cleaned_data.get('phone') or ''
        digits = re.sub(r'\D', '', value)
        if len(digits) < 10:
            raise forms.ValidationError('Введите корректный номер телефона.')
        if digits.startswith('8'):
            digits = '7' + digits[1:]
        elif not digits.startswith('7'):
            digits = '7' + digits
        return '+7' + digits[-10:].rjust(10, '0')

    def clean_message(self):
        value = (self.cleaned_data.get('message') or '').strip()
        if not value:
            raise forms.ValidationError('Опишите желаемый автомобиль.')
        if len(value) > MAX_MESSAGE_LENGTH:
            raise forms.ValidationError(f'Сообщение слишком длинное (максимум {MAX_MESSAGE_LENGTH} символов).')
        return value


class DeliveryForm(forms.ModelForm):
    """Форма заявки на доставку автомобиля."""

    class Meta:
        model = DeliveryRequest
        fields = ['name', 'phone', 'message', 'consent']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Ваше имя *',
                'autocomplete': 'name',
            }),
            'phone': forms.TextInput(attrs={
                'type': 'tel',
                'placeholder': 'Телефон *',
                'autocomplete': 'tel',
            }),
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Комментарий к заявке...',
            }),
            'consent': forms.CheckboxInput(attrs={'required': True}),
        }
        labels = {
            'name': 'Имя',
            'phone': 'Телефон',
            'message': 'Комментарий',
            'consent': 'Я соглашаюсь с политикой конфиденциальности',
        }

    def clean_phone(self):
        value = self.cleaned_data.get('phone') or ''
        digits = re.sub(r'\D', '', value)
        if len(digits) < 10:
            raise forms.ValidationError('Введите корректный номер телефона.')
        if digits.startswith('8'):
            digits = '7' + digits[1:]
        elif not digits.startswith('7'):
            digits = '7' + digits
        return '+7' + digits[-10:].rjust(10, '0')

    def clean_message(self):
        value = (self.cleaned_data.get('message') or '').strip()
        if len(value) > MAX_MESSAGE_LENGTH:
            raise forms.ValidationError(f'Комментарий слишком длинный (максимум {MAX_MESSAGE_LENGTH} символов).')
        return value


class RegistrationForm(forms.ModelForm):
    """Форма заявки на постановку на учёт."""

    class Meta:
        model = RegistrationRequest
        fields = ['name', 'phone', 'message', 'consent']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Ваше имя *',
                'autocomplete': 'name',
            }),
            'phone': forms.TextInput(attrs={
                'type': 'tel',
                'placeholder': 'Телефон *',
                'autocomplete': 'tel',
            }),
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Комментарий к заявке...',
            }),
            'consent': forms.CheckboxInput(attrs={'required': True}),
        }
        labels = {
            'name': 'Имя',
            'phone': 'Телефон',
            'message': 'Комментарий',
            'consent': 'Я соглашаюсь с политикой конфиденциальности',
        }

    def clean_phone(self):
        value = self.cleaned_data.get('phone') or ''
        digits = re.sub(r'\D', '', value)
        if len(digits) < 10:
            raise forms.ValidationError('Введите корректный номер телефона.')
        if digits.startswith('8'):
            digits = '7' + digits[1:]
        elif not digits.startswith('7'):
            digits = '7' + digits
        return '+7' + digits[-10:].rjust(10, '0')

    def clean_message(self):
        value = (self.cleaned_data.get('message') or '').strip()
        if len(value) > MAX_MESSAGE_LENGTH:
            raise forms.ValidationError(f'Комментарий слишком длинный (максимум {MAX_MESSAGE_LENGTH} символов).')
        return value


class BuyoutForm(forms.ModelForm):
    """Форма заявки на выкуп автомобиля."""

    class Meta:
        model = BuyoutRequest
        fields = ['name', 'phone', 'message', 'consent']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Ваше имя *',
                'autocomplete': 'name',
            }),
            'phone': forms.TextInput(attrs={
                'type': 'tel',
                'placeholder': 'Телефон *',
                'autocomplete': 'tel',
            }),
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Комментарий к заявке...',
            }),
            'consent': forms.CheckboxInput(attrs={'required': True}),
        }
        labels = {
            'name': 'Имя',
            'phone': 'Телефон',
            'message': 'Комментарий',
            'consent': 'Я соглашаюсь с политикой конфиденциальности',
        }

    def clean_phone(self):
        value = self.cleaned_data.get('phone') or ''
        digits = re.sub(r'\D', '', value)
        if len(digits) < 10:
            raise forms.ValidationError('Введите корректный номер телефона.')
        if digits.startswith('8'):
            digits = '7' + digits[1:]
        elif not digits.startswith('7'):
            digits = '7' + digits
        return '+7' + digits[-10:].rjust(10, '0')

    def clean_message(self):
        value = (self.cleaned_data.get('message') or '').strip()
        if len(value) > MAX_MESSAGE_LENGTH:
            raise forms.ValidationError(f'Комментарий слишком длинный (максимум {MAX_MESSAGE_LENGTH} символов).')
        return value
