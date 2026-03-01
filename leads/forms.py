import re
from django import forms
from .models import Lead


class LeadForm(forms.ModelForm):
    """Форма заявки «Заказать авто» с валидацией телефона и бюджета."""

    country = forms.ChoiceField(
        label='Страна',
        choices=[('', 'Выберите страну')] + list(Lead.Country.choices),
        required=True,
    )

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
