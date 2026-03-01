from django.contrib import admin
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'country', 'budget', 'urgency', 'created_at')
    list_filter = ('country', 'urgency', 'created_at')
    search_fields = ('name', 'phone', 'contact', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25
    list_display_links = ('name', 'phone')
