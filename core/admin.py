from django.contrib import admin
from .models import CookieConsent


@admin.register(CookieConsent)
class CookieConsentAdmin(admin.ModelAdmin):
    list_display = ('choice', 'session_key', 'created_at')
    list_filter = ('choice', 'created_at')
    readonly_fields = ('choice', 'session_key', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 50
