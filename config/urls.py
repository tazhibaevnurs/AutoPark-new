from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
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
    path('process/', pages_views.process, name='process'),
    path('about/', pages_views.about, name='about'),
    path('cases/', pages_views.cases, name='cases'),
    path('team/', pages_views.team, name='team'),
    path('contacts/', pages_views.contacts, name='contacts'),
    path('login/', pages_views.login_view, name='login'),
    path('profile/', pages_views.profile_view, name='profile'),
    path('logout/', pages_views.logout_view, name='logout'),
    path('admin/', admin.site.urls),
    path('api/cookie-consent/', core_views.CookieConsentView.as_view(), name='api_cookie_consent'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
