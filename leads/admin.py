from django.contrib import admin
from .models import (
    Lead,
    CarSearchRequest,
    BuyoutRequest,
    DeliveryRequest,
    RegistrationRequest,
    ExpertQuestionRequest,
    MotorcycleSalesRequest,
)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'country', 'vehicle_type', 'budget', 'urgency', 'created_at')
    list_filter = ('country', 'vehicle_type', 'urgency', 'created_at')
    search_fields = ('name', 'phone', 'contact', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25
    list_display_links = ('name', 'phone')


@admin.register(CarSearchRequest)
class CarSearchRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'vehicle_type', 'created_at')
    list_filter = ('vehicle_type', 'created_at')
    search_fields = ('name', 'phone', 'message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25


@admin.register(BuyoutRequest)
class BuyoutRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'vehicle_type', 'created_at')
    list_filter = ('vehicle_type', 'created_at')
    search_fields = ('name', 'phone', 'message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25


@admin.register(DeliveryRequest)
class DeliveryRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'vehicle_type', 'created_at')
    list_filter = ('vehicle_type', 'created_at')
    search_fields = ('name', 'phone', 'message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25


@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'vehicle_type', 'created_at')
    list_filter = ('vehicle_type', 'created_at')
    search_fields = ('name', 'phone', 'message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25


@admin.register(ExpertQuestionRequest)
class ExpertQuestionRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'vehicle_type', 'question_type', 'subject', 'created_at')
    list_filter = ('vehicle_type', 'question_type', 'created_at')
    search_fields = ('name', 'phone', 'subject', 'message', 'car_brand', 'car_model')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25


@admin.register(MotorcycleSalesRequest)
class MotorcycleSalesRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'vehicle_type', 'city', 'brand', 'created_at')
    list_filter = ('vehicle_type', 'created_at')
    search_fields = ('name', 'phone', 'city', 'brand', 'message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25
