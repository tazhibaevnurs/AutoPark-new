from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
import config.admin  # noqa: F401 — кастомизация заголовка и названия админки
from pages import views as pages_views
from leads import views as leads_views
from core import views as core_views

urlpatterns = [
    path('', pages_views.home, name='home'),
    path('uslugi/', pages_views.services, name='services'),
    path('zakaz/', include([
        path('', leads_views.OrderQuizView.as_view(), name='order_quiz'),
        path('success/', leads_views.order_quiz_success_view, name='order_quiz_success'),
    ])),
    path('poisk-avto/', include([
        path('', leads_views.CarSearchView.as_view(), name='car_search'),
        path('success/', leads_views.car_search_success_view, name='car_search_success'),
    ])),
    path('vykup/', include([
        path('', leads_views.BuyoutView.as_view(), name='buyout'),
        path('success/', leads_views.buyout_success_view, name='buyout_success'),
    ])),
    path('dostavka-avto/', include([
        path('', leads_views.DeliveryView.as_view(), name='delivery'),
        path('success/', leads_views.delivery_success_view, name='delivery_success'),
    ])),
    path('prodazha-motociklov/', pages_views.motorcycle_sales, name='motorcycle_sales'),
    path('postanovka-na-uchet/', include([
        path('', leads_views.RegistrationView.as_view(), name='registration'),
        path('success/', leads_views.registration_success_view, name='registration_success'),
    ])),
    path('process/', pages_views.process, name='process'),
    path('about/', pages_views.about, name='about'),
    path('catalog/', pages_views.catalog, name='catalog'),
    path('catalog/<uuid:public_id>/', pages_views.catalog_detail, name='catalog_detail'),
    path('media/catalog/<uuid:public_id>/video/', pages_views.serve_catalog_video, name='serve_catalog_video'),
    path('cases/', pages_views.cases, name='cases'),
    path('team/', pages_views.team, name='team'),
    path('contacts/', pages_views.contacts, name='contacts'),
    path('register/', pages_views.register_view, name='register'),
    path('verify-email/<uidb64>/<token>/', pages_views.verify_email_view, name='verify_email'),
    path('login/', pages_views.login_view, name='login'),
    path('profile/', pages_views.profile_view, name='profile'),
    path('logout/', pages_views.logout_view, name='logout'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(template_name='pages/password_reset_form.html'),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='pages/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='pages/password_reset_confirm.html'),
        name='password_reset_confirm',
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='pages/password_reset_complete.html'),
        name='password_reset_complete',
    ),
    path('video/hero.mp4', pages_views.serve_hero_video, name='hero_video'),
    path('media/service/<uuid:public_id>/video/', pages_views.serve_service_video, name='serve_service_video'),
    path('media/case/<uuid:public_id>/video/', pages_views.serve_case_video, name='serve_case_video'),
    path('blog/', pages_views.blog, name='blog'),
    path('blog/<slug:slug>/', pages_views.blog_detail, name='blog_detail'),
    path('media/blog/<uuid:public_id>/video/', pages_views.serve_blog_video, name='serve_blog_video'),
    path('admin/', admin.site.urls),
    path('api/cookie-consent/', core_views.CookieConsentView.as_view(), name='api_cookie_consent'),
    # Раздача медиа (фото и т.д.) — явный view, работает при DEBUG=False
    path('media/<path:path>', pages_views.serve_media, name='serve_media'),
]
