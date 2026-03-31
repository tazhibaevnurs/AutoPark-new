from django.contrib import admin
from django.utils.html import format_html
from .models import CookieConsent, Service, HeroMedia, TeamMember, Case, CatalogCar, CatalogCarImage, BlogPost


@admin.register(HeroMedia)
class HeroMediaAdmin(admin.ModelAdmin):
    list_display = ('media_type', 'preview_display')
    list_display_links = ('preview_display',)
    fields = (
        'media_type',
        'image',
        'video',
        'preview',
    )
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.media_type == 'image' and obj.image:
            return format_html(
                '<img src="{}" width="320" height="180" style="object-fit: cover; border-radius: 8px;" />',
                obj.image.url,
            )
        if obj.media_type == 'video' and obj.video:
            return format_html(
                '<p>Видео: <code>{}</code></p>',
                obj.video.name,
            )
        return '—'
    preview.short_description = 'Превью'

    def preview_display(self, obj):
        if obj.media_type == 'image' and obj.image:
            return format_html('<img src="{}" width="80" height="45" style="object-fit: cover;" />', obj.image.url)
        if obj.media_type == 'video' and obj.video:
            return 'Видео'
        return '—'
    preview_display.short_description = 'Превью'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'order', 'media_preview')
    list_editable = ('order', 'media_type')
    list_display_links = ('title',)
    search_fields = ('title',)
    ordering = ('order',)
    fields = ('title', 'description', 'media_type', 'image', 'video', 'order')

    def media_preview(self, obj):
        if obj.media_type == 'image' and obj.image:
            return format_html(
                '<img src="{}" width="80" height="50" style="object-fit: cover;" />',
                obj.image.url,
            )
        if obj.media_type == 'video' and obj.video:
            return format_html('<span>Видео</span>')
        return '—'
    media_preview.short_description = 'Превью'


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'order', 'is_active', 'photo_preview')
    list_editable = ('order', 'is_active')
    list_display_links = ('name',)
    list_filter = ('is_active',)
    search_fields = ('name', 'role')
    ordering = ('order', 'id')
    fields = ('name', 'role', 'photo', 'order', 'is_active', 'preview')
    readonly_fields = ('preview',)

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="40" height="40" style="object-fit:cover;border-radius:50%;" />',
                obj.photo.url,
            )
        return format_html(
            '<span style="display:inline-flex;align-items:center;justify-content:center;'
            'width:40px;height:40px;border-radius:50%;background:#E98733;color:#fff;'
            'font-weight:700;font-size:1rem;">{}</span>',
            obj.initial,
        )
    photo_preview.short_description = 'Фото'

    def preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="120" height="120" style="object-fit:cover;border-radius:12px;" />',
                obj.photo.url,
            )
        return '—'
    preview.short_description = 'Превью'


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'country', 'year', 'engine_type', 'media_type', 'order', 'is_active', 'media_preview')
    list_editable = ('order', 'is_active', 'country', 'media_type')
    list_display_links = ('title',)
    list_filter = ('country', 'is_active', 'media_type')
    search_fields = ('title', 'engine_type', 'description')
    ordering = ('order', '-id')
    fields = ('title', 'country', 'year', 'engine_type', 'description', 'media_type', 'image', 'video', 'order', 'is_active', 'preview')
    readonly_fields = ('preview',)

    def media_preview(self, obj):
        if obj.media_type == 'image' and obj.image:
            return format_html(
                '<img src="{}" width="80" height="50" style="object-fit:cover;border-radius:6px;" />',
                obj.image.url,
            )
        if obj.media_type == 'video' and obj.video:
            return format_html('<span>Видео</span>')
        return '—'
    media_preview.short_description = 'Медиа'

    def preview(self, obj):
        if obj.media_type == 'image' and obj.image:
            return format_html(
                '<img src="{}" width="320" height="200" style="object-fit:cover;border-radius:12px;" />',
                obj.image.url,
            )
        if obj.media_type == 'video' and obj.video:
            return format_html('<p>Видео: <code>{}</code></p>', obj.video.name)
        return '—'
    preview.short_description = 'Превью'


class CatalogCarImageInline(admin.TabularInline):
    model = CatalogCarImage
    extra = 1
    fields = ('image', 'caption', 'order', 'thumb')
    readonly_fields = ('thumb',)
    ordering = ('order', 'id')

    def thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="50" style="object-fit:cover;border-radius:6px;" />',
                obj.image.url,
            )
        return '—'
    thumb.short_description = 'Превью'


@admin.register(CatalogCar)
class CatalogCarAdmin(admin.ModelAdmin):
    list_display = ('title', 'country', 'year', 'price', 'status', 'order', 'is_active', 'photo_thumb')
    list_editable = ('order', 'is_active', 'status', 'country')
    list_display_links = ('title',)
    list_filter = ('country', 'status', 'is_active')
    search_fields = ('title', 'engine_type', 'description')
    ordering = ('order', '-id')
    fieldsets = (
        (None, {'fields': ('title', 'country', 'year', 'engine_type', 'price', 'mileage', 'status')}),
        ('Описание', {'fields': ('description',)}),
        ('Медиа', {'fields': ('image', 'video', 'preview')}),
        ('Настройки', {'fields': ('order', 'is_active')}),
    )
    readonly_fields = ('preview',)
    inlines = [CatalogCarImageInline]

    def photo_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="50" style="object-fit:cover;border-radius:6px;" />',
                obj.image.url,
            )
        return '—'
    photo_thumb.short_description = 'Фото'

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="320" height="200" style="object-fit:cover;border-radius:12px;" />',
                obj.image.url,
            )
        if obj.video:
            return format_html('<p>Видео: <code>{}</code></p>', obj.video.name)
        return '—'
    preview.short_description = 'Превью'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'order', 'created_at', 'media_preview')
    list_editable = ('is_published', 'order')
    list_display_links = ('title',)
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-order', '-created_at')
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'excerpt', 'content')}),
        ('Медиа', {'fields': ('image', 'video', 'preview')}),
        ('Публикация', {'fields': ('is_published', 'order', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('preview', 'created_at', 'updated_at')

    def media_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="50" style="object-fit:cover;border-radius:6px;" />',
                obj.image.url,
            )
        if obj.video:
            return format_html('<span>Видео</span>')
        return '—'
    media_preview.short_description = 'Медиа'

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="320" height="200" style="object-fit:cover;border-radius:12px;" />',
                obj.image.url,
            )
        if obj.video:
            return format_html('<p>Видео: <code>{}</code></p>', obj.video.name)
        return '—'
    preview.short_description = 'Превью'


@admin.register(CookieConsent)
class CookieConsentAdmin(admin.ModelAdmin):
    list_display = ('choice', 'session_key', 'created_at')
    list_filter = ('choice', 'created_at')
    readonly_fields = ('choice', 'session_key', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 50
