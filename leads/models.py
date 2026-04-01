from django.db import models
from core.models import TimeStampedModel


class Lead(TimeStampedModel):
    """Заявка с формы «Заказать авто» (квиз)."""

    class Country(models.TextChoices):
        CHINA = 'china', 'Китай'
        KOREA = 'korea', 'Корея'
        USA = 'usa', 'США'

    class BodyType(models.TextChoices):
        ANY = '', 'Любой'
        SEDAN = 'sedan', 'Седан'
        SUV = 'suv', 'Внедорожник'
        COUPE = 'coupe', 'Купе'
        MINIVAN = 'minivan', 'Минивэн'
        PICKUP = 'pickup', 'Пикап'
        HATCHBACK = 'hatchback', 'Хэтчбек'

    class Urgency(models.TextChoices):
        NORMAL = 'normal', 'Обычная'
        FAST = 'fast', 'Срочно'

    country = models.CharField(
        'Страна',
        max_length=20,
        choices=Country.choices,
    )
    budget = models.CharField('Бюджет (₽)', max_length=50)
    body_type = models.CharField(
        'Тип кузова',
        max_length=20,
        choices=BodyType.choices,
        default=BodyType.ANY,
        blank=True,
    )
    urgency = models.CharField(
        'Срочность',
        max_length=20,
        choices=Urgency.choices,
        default=Urgency.NORMAL,
    )
    name = models.CharField('Имя', max_length=255)
    phone = models.CharField('Телефон', max_length=30)
    contact = models.CharField(
        'Telegram',
        max_length=255,
        blank=True,
    )
    comment = models.TextField('Комментарий', blank=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.phone} ({self.get_country_display()})'


class CarSearchRequest(TimeStampedModel):
    """Заявка на поиск автомобиля со страницы «Поиск авто»."""

    name = models.CharField('Имя', max_length=255)
    phone = models.CharField('Телефон', max_length=30)
    email = models.EmailField('Email', blank=True)
    message = models.TextField(
        'Опишите желаемый автомобиль',
        help_text='Марка, модель, год, бюджет, пожелания',
    )
    consent = models.BooleanField(
        'Согласие с политикой конфиденциальности',
        default=False,
    )

    class Meta:
        verbose_name = 'Заявка на поиск авто'
        verbose_name_plural = 'Заявки на поиск авто'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.phone}'


class BuyoutRequest(TimeStampedModel):
    """Заявка на выкуп автомобиля со страницы «Выкуп»."""

    name = models.CharField('Имя', max_length=255)
    phone = models.CharField('Телефон', max_length=30)
    message = models.TextField(
        'Комментарий к заявке',
        blank=True,
        help_text='Комментарий или пожелания по выкупу',
    )
    consent = models.BooleanField(
        'Согласие с политикой конфиденциальности',
        default=False,
    )

    class Meta:
        verbose_name = 'Заявка на выкуп'
        verbose_name_plural = 'Заявки на выкуп'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.phone}'


class DeliveryRequest(TimeStampedModel):
    """Заявка на доставку автомобиля со страницы «Доставка авто»."""

    name = models.CharField('Имя', max_length=255)
    phone = models.CharField('Телефон', max_length=30)
    message = models.TextField(
        'Комментарий к заявке',
        blank=True,
        help_text='Комментарий или пожелания по доставке',
    )
    consent = models.BooleanField(
        'Согласие с политикой конфиденциальности',
        default=False,
    )

    class Meta:
        verbose_name = 'Заявка на доставку'
        verbose_name_plural = 'Заявки на доставку'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.phone}'


class RegistrationRequest(TimeStampedModel):
    """Заявка на постановку на учёт со страницы «Постановка на учёт»."""

    name = models.CharField('Имя', max_length=255)
    phone = models.CharField('Телефон', max_length=30)
    message = models.TextField(
        'Комментарий к заявке',
        blank=True,
        help_text='Комментарий или пожелания по постановке на учёт',
    )
    consent = models.BooleanField(
        'Согласие с политикой конфиденциальности',
        default=False,
    )

    class Meta:
        verbose_name = 'Заявка на постановку на учёт'
        verbose_name_plural = 'Заявки на постановку на учёт'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.phone}'
