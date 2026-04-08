import re
from django import forms
from .antispam import LeadAntiSpamMixin, validate_person_name
from .models import (
    Lead,
    CarSearchRequest,
    BuyoutRequest,
    DeliveryRequest,
    RegistrationRequest,
    ExpertQuestionRequest,
    MotorcycleSalesRequest,
)

MAX_COMMENT_LENGTH = 2000
MAX_MESSAGE_LENGTH = 2000


class LeadForm(LeadAntiSpamMixin, forms.ModelForm):
    """Форма заявки «Заказать авто» с валидацией телефона и бюджета."""

    country = forms.ChoiceField(
        label='Страна',
        choices=[('', 'Выберите страну')] + list(Lead.Country.choices),
        required=True,
    )

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, request=request, **kwargs)
        self.fields['vehicle_type'].required = False
        self.fields['name'].required = True
        self.fields['phone'].required = True
        # Явно в разметку: BoundField иногда не проставляет required для кастомных attrs
        self.fields['name'].widget.attrs['required'] = 'required'
        self.fields['name'].widget.attrs['aria-required'] = 'true'
        self.fields['phone'].widget.attrs['required'] = 'required'
        self.fields['phone'].widget.attrs['aria-required'] = 'true'
        # CharField(max_length=30) подставляет maxlength=30; для маски достаточно 18
        self.fields['phone'].widget.attrs['maxlength'] = '18'

    class Meta:
        model = Lead
        fields = [
            'country', 'budget', 'body_type', 'urgency',
            'name', 'phone', 'contact', 'comment', 'vehicle_type',
        ]
        widgets = {
            'country': forms.Select(attrs={'id': 'id_country'}),
            'budget': forms.TextInput(attrs={
                'id': 'id_budget',
                'placeholder': 'Например: 3 000 000',
            }),
            'body_type': forms.Select(attrs={'id': 'id_body_type'}),
            'urgency': forms.Select(attrs={'id': 'id_urgency'}),
            'name': forms.TextInput(attrs={
                'id': 'id_name',
                'autocomplete': 'name',
                'placeholder': 'Ваше имя *',
            }),
            'phone': forms.TextInput(attrs={
                'id': 'id_phone',
                'type': 'tel',
                'inputmode': 'tel',
                'autocomplete': 'tel',
                'placeholder': '+7 (___) ___-__-__ *',
                'maxlength': '18',
                'data-phone-mask': '+7 (___) ___-__-__',
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
            'vehicle_type': forms.HiddenInput(),
        }

    def clean_name(self):
        value = (self.cleaned_data.get('name') or '').strip()
        if not value:
            raise forms.ValidationError('Укажите имя.')
        return validate_person_name(value)

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

class CarSearchForm(LeadAntiSpamMixin, forms.ModelForm):
    """Форма заявки на поиск автомобиля."""

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, request=request, **kwargs)
        self.fields['vehicle_type'].required = False

    class Meta:
        model = CarSearchRequest
        fields = ['name', 'phone', 'email', 'message', 'consent', 'vehicle_type']
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
            'vehicle_type': forms.HiddenInput(),
        }
        labels = {
            'name': 'Имя',
            'phone': 'Телефон',
            'email': 'Email',
            'message': 'Опишите желаемый автомобиль',
            'consent': 'Я соглашаюсь с политикой конфиденциальности',
            'vehicle_type': 'Тип транспорта',
        }

    def clean_name(self):
        return validate_person_name(self.cleaned_data.get('name'))

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


class DeliveryForm(LeadAntiSpamMixin, forms.ModelForm):
    """Форма заявки на доставку автомобиля."""

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, request=request, **kwargs)
        self.fields['vehicle_type'].required = False

    class Meta:
        model = DeliveryRequest
        fields = ['name', 'phone', 'message', 'consent', 'vehicle_type']
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
            'vehicle_type': forms.HiddenInput(),
        }
        labels = {
            'name': 'Имя',
            'phone': 'Телефон',
            'message': 'Комментарий',
            'consent': 'Я соглашаюсь с политикой конфиденциальности',
            'vehicle_type': 'Тип транспорта',
        }

    def clean_name(self):
        return validate_person_name(self.cleaned_data.get('name'))

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


class RegistrationForm(LeadAntiSpamMixin, forms.ModelForm):
    """Форма заявки на постановку на учёт."""

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, request=request, **kwargs)
        self.fields['vehicle_type'].required = False

    class Meta:
        model = RegistrationRequest
        fields = ['name', 'phone', 'message', 'consent', 'vehicle_type']
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
            'vehicle_type': forms.HiddenInput(),
        }
        labels = {
            'name': 'Имя',
            'phone': 'Телефон',
            'message': 'Комментарий',
            'consent': 'Я соглашаюсь с политикой конфиденциальности',
            'vehicle_type': 'Тип транспорта',
        }

    def clean_name(self):
        return validate_person_name(self.cleaned_data.get('name'))

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


class BuyoutForm(LeadAntiSpamMixin, forms.ModelForm):
    """Форма заявки на выкуп автомобиля."""

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, request=request, **kwargs)
        self.fields['vehicle_type'].required = False

    class Meta:
        model = BuyoutRequest
        fields = ['name', 'phone', 'message', 'consent', 'vehicle_type']
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
            'vehicle_type': forms.HiddenInput(),
        }
        labels = {
            'name': 'Имя',
            'phone': 'Телефон',
            'message': 'Комментарий',
            'consent': 'Я соглашаюсь с политикой конфиденциальности',
            'vehicle_type': 'Тип транспорта',
        }

    def clean_name(self):
        return validate_person_name(self.cleaned_data.get('name'))

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


class ExpertQuestionForm(LeadAntiSpamMixin, forms.ModelForm):
    """Форма страницы «Связаться с нами» (в стиле экспертной консультации)."""

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, request=request, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'ct-field'
        self.fields['phone'].widget.attrs.update({
            'class': 'ct-field',
            'id': 'id_expert_phone',
            'inputmode': 'tel',
            'maxlength': '18',
            'placeholder': '+7 (___) ___-__-__',
            'data-phone-mask': '+7 (___) ___-__-__',
        })
        self.fields['subject'].widget.attrs['class'] = 'ct-field'
        self.fields['car_brand'].widget.attrs['class'] = 'ct-field'
        self.fields['car_model'].widget.attrs['class'] = 'ct-field'
        self.fields['message'].widget.attrs['class'] = 'ct-area'
        self.fields['vehicle_type'].widget = forms.HiddenInput()
        self.fields['vehicle_type'].required = False

    class Meta:
        model = ExpertQuestionRequest
        fields = [
            'name', 'phone', 'subject', 'question_type',
            'car_brand', 'car_model', 'message', 'consent', 'vehicle_type',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ваше имя *', 'autocomplete': 'name'}),
            'phone': forms.TextInput(attrs={'type': 'tel', 'placeholder': 'Телефон *', 'autocomplete': 'tel'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Тема обращения *'}),
            'question_type': forms.RadioSelect(),
            'car_brand': forms.TextInput(attrs={'placeholder': 'Марка авто/мото'}),
            'car_model': forms.TextInput(attrs={'placeholder': 'Модель авто/мото'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Опишите ваш вопрос подробнее...'}),
            'consent': forms.CheckboxInput(attrs={'required': True}),
            'vehicle_type': forms.HiddenInput(),
        }
        labels = {
            'name': 'Имя',
            'phone': 'Телефон',
            'subject': 'Тема обращения',
            'question_type': 'Тип вопроса',
            'car_brand': 'Марка авто/мото',
            'car_model': 'Модель авто/мото',
            'message': 'Описание вопроса',
            'consent': 'Я соглашаюсь с политикой конфиденциальности',
            'vehicle_type': 'Тип транспорта',
        }

    def clean_name(self):
        return validate_person_name(self.cleaned_data.get('name'))

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

    def clean_subject(self):
        value = (self.cleaned_data.get('subject') or '').strip()
        if not value:
            raise forms.ValidationError('Укажите тему обращения.')
        return value

    def clean_message(self):
        value = (self.cleaned_data.get('message') or '').strip()
        if not value:
            raise forms.ValidationError('Опишите ваш вопрос.')
        if len(value) > MAX_MESSAGE_LENGTH:
            raise forms.ValidationError(f'Сообщение слишком длинное (максимум {MAX_MESSAGE_LENGTH} символов).')
        return value


class MotorcycleSalesForm(LeadAntiSpamMixin, forms.ModelForm):
    """Форма заявки на подбор/покупку мотоцикла."""

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, request=request, **kwargs)
        self.fields['vehicle_type'].required = False

    class Meta:
        model = MotorcycleSalesRequest
        fields = ['name', 'phone', 'city', 'brand', 'message', 'consent', 'vehicle_type']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ваше имя *', 'autocomplete': 'name'}),
            'phone': forms.TextInput(attrs={'type': 'tel', 'placeholder': '+7 (999) 123-45-67', 'autocomplete': 'tel'}),
            'city': forms.TextInput(attrs={'placeholder': 'Город'}),
            'brand': forms.TextInput(attrs={'placeholder': 'Интересующая марка (например, Honda, Yamaha)'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Опишите пожелания: модель, бюджет, сроки, пробег...'}),
            'consent': forms.CheckboxInput(attrs={'required': True}),
            'vehicle_type': forms.HiddenInput(),
        }
        labels = {
            'name': 'Имя',
            'phone': 'Телефон',
            'city': 'Город',
            'brand': 'Марка',
            'message': 'Комментарий',
            'consent': 'Я соглашаюсь с политикой конфиденциальности',
            'vehicle_type': 'Тип транспорта',
        }

    def clean_name(self):
        return validate_person_name(self.cleaned_data.get('name'))

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
