from django.db import models


class TimeStampedModel(models.Model):
    """
    Абстрактная модель с полями created/updated для единообразия по проекту.
    """
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        abstract = True


class CookieConsent(models.Model):
    """
    Запись о выборе пользователя по cookies (для аудита и соответствия).
    Создаётся при принятии или отклонении баннера на сайте.
    """
    class Choice(models.TextChoices):
        ACCEPTED = 'accepted', 'Принято'
        REJECTED = 'rejected', 'Отклонено'

    choice = models.CharField(
        'Выбор',
        max_length=20,
        choices=Choice.choices,
    )
    session_key = models.CharField(
        'Ключ сессии',
        max_length=40,
        blank=True,
        db_index=True,
    )
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Согласие на cookies'
        verbose_name_plural = 'Согласия на cookies'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_choice_display()} — {self.created_at}'
