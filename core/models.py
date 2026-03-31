from django.db import models
from django.core.exceptions import ValidationError
import uuid
from .validators import validate_uploaded_image, validate_uploaded_video


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


class Service(models.Model):
    """
    Услуга для страницы «Наши услуги». В админке можно выбрать фото или видео.
    """
    class MediaType(models.TextChoices):
        IMAGE = 'image', 'Фото'
        VIDEO = 'video', 'Видео'

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    title = models.CharField('Название', max_length=200)
    description = models.TextField(
        'Описание',
        blank=True,
        help_text='Краткое описание услуги для списка под блоком «Наши услуги».',
    )
    media_type = models.CharField(
        'Тип медиа',
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
    )
    image = models.ImageField(
        'Фото',
        upload_to='services/%Y/%m/',
        blank=True,
        null=True,
        help_text='Используется, если выбран тип «Фото». Рекомендуемый размер: 600×400 px.',
    )
    video = models.FileField(
        'Видео',
        upload_to='services/%Y/%m/',
        blank=True,
        null=True,
        help_text='Формат MP4. Используется, если выбран тип «Видео».',
    )
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title

    def clean(self):
        if self.image:
            validate_uploaded_image(self.image)
        if self.video:
            validate_uploaded_video(self.video)
        if self.media_type == self.MediaType.IMAGE and self.video:
            raise ValidationError({'video': 'Для типа "Фото" загрузка видео не допускается.'})
        if self.media_type == self.MediaType.VIDEO and self.image:
            raise ValidationError({'image': 'Для типа "Видео" загрузка изображения не допускается.'})


class TeamMember(models.Model):
    """Сотрудник компании для страницы «Команда»."""
    name = models.CharField('Имя', max_length=150)
    role = models.CharField('Должность', max_length=300)
    photo = models.ImageField(
        'Фото',
        upload_to='team/%Y/%m/',
        blank=True,
        null=True,
        help_text='Рекомендуемый размер: 400×400 px. Если не задано — отображается первая буква имени.',
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Отображать', default=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['order', 'id']

    def __str__(self):
        return self.name

    @property
    def initial(self):
        return self.name[0].upper() if self.name else '?'

    def clean(self):
        if self.photo:
            validate_uploaded_image(self.photo)


class Case(models.Model):
    """Кейс (реализованный проект) для страницы «Наши кейсы»."""
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    class Country(models.TextChoices):
        KOREA = 'korea', 'Корея'
        CHINA = 'china', 'Китай'
        USA = 'usa', 'США'
        OTHER = 'other', 'Другое'

    class MediaType(models.TextChoices):
        IMAGE = 'image', 'Фото'
        VIDEO = 'video', 'Видео'

    title = models.CharField(
        'Марка и модель', max_length=200,
        help_text='Например: Kia Sorento, Toyota RAV4',
    )
    country = models.CharField(
        'Страна', max_length=20,
        choices=Country.choices, default=Country.KOREA,
    )
    year = models.PositiveIntegerField('Год выпуска', blank=True, null=True)
    engine_type = models.CharField(
        'Тип двигателя', max_length=100, blank=True,
        help_text='Например: дизель, бензин, электро, гибрид',
    )
    description = models.CharField(
        'Краткое описание', max_length=300, blank=True,
        help_text='Доп. текст: «под ключ», «подбор, доставка, оформление» и т.д.',
    )
    media_type = models.CharField(
        'Тип медиа', max_length=10,
        choices=MediaType.choices, default=MediaType.IMAGE,
    )
    image = models.ImageField(
        'Фото автомобиля',
        upload_to='cases/%Y/%m/',
        blank=True, null=True,
        help_text='Рекомендуемый размер: 800×500 px. Используется при типе «Фото».',
    )
    video = models.FileField(
        'Видео',
        upload_to='cases/%Y/%m/',
        blank=True, null=True,
        help_text='Формат MP4. Используется при типе «Видео».',
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Отображать', default=True)

    class Meta:
        verbose_name = 'Кейс'
        verbose_name_plural = 'Кейсы'
        ordering = ['order', '-id']

    def __str__(self):
        return f'{self.title} ({self.get_country_display()})'

    @property
    def meta_line(self):
        parts = []
        if self.year:
            parts.append(str(self.year))
        if self.engine_type:
            parts.append(self.engine_type)
        line = ', '.join(parts)
        if self.description:
            line = f'{line} · {self.description}' if line else self.description
        return line

    def clean(self):
        if self.image:
            validate_uploaded_image(self.image)
        if self.video:
            validate_uploaded_video(self.video)
        if self.media_type == self.MediaType.IMAGE and self.video:
            raise ValidationError({'video': 'Для типа "Фото" загрузка видео не допускается.'})
        if self.media_type == self.MediaType.VIDEO and self.image:
            raise ValidationError({'image': 'Для типа "Видео" загрузка изображения не допускается.'})


class CatalogCar(models.Model):
    """Автомобиль в каталоге — доступные для заказа авто."""
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    class Country(models.TextChoices):
        KOREA = 'korea', 'Корея'
        CHINA = 'china', 'Китай'
        USA = 'usa', 'США'
        OTHER = 'other', 'Другое'

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'В наличии'
        IN_TRANSIT = 'in_transit', 'В пути'
        ON_ORDER = 'on_order', 'Под заказ'
        SOLD = 'sold', 'Продано'

    title = models.CharField(
        'Марка и модель', max_length=200,
        help_text='Например: Kia K5, Hyundai Santa Fe',
    )
    country = models.CharField(
        'Страна', max_length=20,
        choices=Country.choices, default=Country.KOREA,
    )
    year = models.PositiveIntegerField('Год выпуска', blank=True, null=True)
    engine_type = models.CharField(
        'Тип двигателя', max_length=100, blank=True,
        help_text='дизель, бензин, электро, гибрид',
    )
    price = models.CharField(
        'Цена', max_length=100, blank=True,
        help_text='Например: 2 850 000 ₽ или от 2.5 млн ₽',
    )
    mileage = models.CharField(
        'Пробег', max_length=100, blank=True,
        help_text='Например: 25 000 км или Новый',
    )
    status = models.CharField(
        'Статус', max_length=20,
        choices=Status.choices, default=Status.AVAILABLE,
    )
    description = models.TextField(
        'Описание', blank=True,
        help_text='Подробности: комплектация, особенности и т.д.',
    )
    image = models.ImageField(
        'Главное фото', upload_to='catalog/%Y/%m/',
        blank=True, null=True,
        help_text='Главное фото для карточки и детальной страницы. 800×500 px.',
    )
    video = models.FileField(
        'Видео', upload_to='catalog/%Y/%m/',
        blank=True, null=True,
        help_text='Формат MP4. Видеообзор автомобиля.',
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Отображать', default=True)

    class Meta:
        verbose_name = 'Авто в каталоге'
        verbose_name_plural = 'Каталог авто'
        ordering = ['order', '-id']

    def __str__(self):
        return f'{self.title} ({self.get_country_display()})'

    @property
    def specs_line(self):
        parts = []
        if self.year:
            parts.append(str(self.year))
        if self.engine_type:
            parts.append(self.engine_type)
        if self.mileage:
            parts.append(self.mileage)
        return ', '.join(parts)

    def clean(self):
        if self.image:
            validate_uploaded_image(self.image)
        if self.video:
            validate_uploaded_video(self.video)


class CatalogCarImage(models.Model):
    """Фото галереи для автомобиля в каталоге."""
    car = models.ForeignKey(
        CatalogCar, on_delete=models.CASCADE,
        related_name='gallery', verbose_name='Автомобиль',
    )
    image = models.ImageField('Фото', upload_to='catalog/gallery/%Y/%m/')
    caption = models.CharField('Подпись', max_length=200, blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Фото галереи'
        verbose_name_plural = 'Галерея фото'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.car.title} — фото #{self.order}'

    def clean(self):
        if self.image:
            validate_uploaded_image(self.image)


class HeroMedia(models.Model):
    """
    Фон главного экрана (hero): в админке можно выбрать фото или видео.
    Только одна запись — настройка «по умолчанию» для всего сайта.
    """
    class MediaType(models.TextChoices):
        IMAGE = 'image', 'Фото'
        VIDEO = 'video', 'Видео'

    media_type = models.CharField(
        'Тип',
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.VIDEO,
    )
    image = models.ImageField(
        'Фото',
        upload_to='hero/%Y/%m/',
        blank=True,
        null=True,
        help_text='Используется, если выбран тип «Фото»',
    )
    video = models.FileField(
        'Видео',
        upload_to='hero/%Y/%m/',
        blank=True,
        null=True,
        help_text='Формат MP4. Используется, если выбран тип «Видео»',
    )

    class Meta:
        verbose_name = 'Фон главного экрана (Hero)'
        verbose_name_plural = 'Фон главного экрана (Hero)'

    def __str__(self):
        return f'Hero — {self.get_media_type_display()}'

    def clean(self):
        if self.image:
            validate_uploaded_image(self.image)
        if self.video:
            validate_uploaded_video(self.video)
        if self.media_type == self.MediaType.IMAGE and self.video:
            raise ValidationError({'video': 'Для типа "Фото" загрузка видео не допускается.'})
        if self.media_type == self.MediaType.VIDEO and self.image:
            raise ValidationError({'image': 'Для типа "Видео" загрузка изображения не допускается.'})


class BlogPost(models.Model):
    """Статья блога: заголовок, контент, главное фото, опциональное видео, публикация."""
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    title = models.CharField('Заголовок', max_length=300)
    slug = models.SlugField('URL', max_length=200, unique=True, allow_unicode=True)
    excerpt = models.CharField(
        'Краткое описание',
        max_length=400,
        blank=True,
        help_text='Показывается в карточке и в превью.',
    )
    content = models.TextField(
        'Текст статьи',
        help_text='Основной текст. Поддерживаются переносы строк.',
    )
    image = models.ImageField(
        'Главное фото',
        upload_to='blog/%Y/%m/',
        blank=True,
        null=True,
        help_text='Рекомендуемый размер: 800×500 px.',
    )
    video = models.FileField(
        'Видео',
        upload_to='blog/%Y/%m/',
        blank=True,
        null=True,
        help_text='Формат MP4. Опционально.',
    )
    is_published = models.BooleanField('Опубликовано', default=False)
    order = models.PositiveIntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Статья блога'
        verbose_name_plural = 'Блог'
        ordering = ['-order', '-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        if self.image:
            validate_uploaded_image(self.image)
        if self.video:
            validate_uploaded_video(self.video)
