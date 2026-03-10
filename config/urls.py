from django.urls import path, include
from django.conf import settings
from django.contrib import admin
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
    path('postanovka-na-uchet/', include([
        path('', leads_views.RegistrationView.as_view(), name='registration'),
        path('success/', leads_views.registration_success_view, name='registration_success'),
    ])),
    path('process/', pages_views.process, name='process'),
    path('about/', pages_views.about, name='about'),
    path('catalog/', pages_views.catalog, name='catalog'),
    path('catalog/<int:pk>/', pages_views.catalog_detail, name='catalog_detail'),
    path('media/catalog/<int:pk>/video/', pages_views.serve_catalog_video, name='serve_catalog_video'),
    path('cases/', pages_views.cases, name='cases'),
    path('team/', pages_views.team, name='team'),
    path('contacts/', pages_views.contacts, name='contacts'),
    path('login/', pages_views.login_view, name='login'),
    path('profile/', pages_views.profile_view, name='profile'),
    path('logout/', pages_views.logout_view, name='logout'),
    path('video/hero.mp4', pages_views.serve_hero_video, name='hero_video'),
    path('media/service/<int:pk>/video/', pages_views.serve_service_video, name='serve_service_video'),
    path('media/case/<int:pk>/video/', pages_views.serve_case_video, name='serve_case_video'),
    path('blog/', pages_views.blog, name='blog'),
    path('blog/<slug:slug>/', pages_views.blog_detail, name='blog_detail'),
    path('media/blog/<int:pk>/video/', pages_views.serve_blog_video, name='serve_blog_video'),
    path('admin/', admin.site.urls),
    path('api/cookie-consent/', core_views.CookieConsentView.as_view(), name='api_cookie_consent'),
    # Раздача медиа (фото и т.д.) — явный view, работает при DEBUG=False
    path('media/<path:path>', pages_views.serve_media, name='serve_media'),
]
