from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    captcha_answer = forms.CharField(required=True, label="Сколько будет?")

    def __init__(self, *args, expected_captcha=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_captcha = (expected_captcha or "").strip()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        # Новые пользователи активируются только после email-верификации.
        user.is_active = False
        if commit:
            user.save()
        return user

    def clean_captcha_answer(self):
        answer = (self.cleaned_data.get("captcha_answer") or "").strip()
        if not self.expected_captcha or answer != self.expected_captcha:
            raise forms.ValidationError("Неверный ответ CAPTCHA.")
        return answer
