import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from config.cookies import (
    set_session_cookie,
    get_session_cookie,
    delete_session_cookie,
)

# Путь к hero-видео по умолчанию (статическая папка)
def _get_static_hero_video_path():
    from pathlib import Path
    bases = [Path(settings.STATIC_ROOT)] + [Path(d) for d in settings.STATICFILES_DIRS]
    for base in bases:
        path = base / 'video' / 'hero.mp4'
        if path.exists():
            return path
    return None


def serve_hero_video(request):
    """Раздаёт hero-видео: из админки (HeroMedia) или static/video/hero.mp4. С поддержкой Range."""
    from pathlib import Path
    from core.models import HeroMedia

    file_path = None
    hero = HeroMedia.objects.first()
    if hero and hero.media_type == 'video' and hero.video:
        file_path = Path(hero.video.path) if hero.video else None
        if file_path and not file_path.is_file():
            file_path = None
    if not file_path:
        file_path = _get_static_hero_video_path()
    if not file_path:
        raise Http404('Hero video not found. Add video in admin (Hero) or static/video/hero.mp4.')

    size = os.path.getsize(file_path)
    content_type = 'video/mp4'
    range_header = request.META.get('HTTP_RANGE')
    if range_header:
        try:
            byte_range = range_header.replace('bytes=', '').strip().split('-')
            start = int(byte_range[0]) if byte_range[0] else 0
            end = int(byte_range[1]) if len(byte_range) > 1 and byte_range[1] else size - 1
            end = min(end, size - 1)
            length = end - start + 1
            with open(file_path, 'rb') as f:
                f.seek(start)
                content = f.read(length)
            response = HttpResponse(content, status=206, content_type=content_type)
            response['Content-Range'] = f'bytes {start}-{end}/{size}'
            response['Accept-Ranges'] = 'bytes'
            response['Content-Length'] = str(length)
            return response
        except (ValueError, IndexError):
            pass
    response = FileResponse(open(file_path, 'rb'), content_type=content_type)
    response['Content-Length'] = str(size)
    response['Accept-Ranges'] = 'bytes'
    return response


def home(request):
    from core.models import HeroMedia
    hero_media = HeroMedia.objects.first()
    return render(request, 'pages/home.html', {'hero_media': hero_media})


def _serve_video_with_range(request, file_path):
    """Раздаёт видео-файл с поддержкой Range."""
    from pathlib import Path
    path = Path(file_path) if file_path else None
    if not path or not path.is_file():
        return None
    size = os.path.getsize(path)
    content_type = 'video/mp4'
    range_header = request.META.get('HTTP_RANGE')
    if range_header:
        try:
            byte_range = range_header.replace('bytes=', '').strip().split('-')
            start = int(byte_range[0]) if byte_range[0] else 0
            end = int(byte_range[1]) if len(byte_range) > 1 and byte_range[1] else size - 1
            end = min(end, size - 1)
            length = end - start + 1
            with open(path, 'rb') as f:
                f.seek(start)
                content = f.read(length)
            response = HttpResponse(content, status=206, content_type=content_type)
            response['Content-Range'] = f'bytes {start}-{end}/{size}'
            response['Accept-Ranges'] = 'bytes'
            response['Content-Length'] = str(length)
            return response
        except (ValueError, IndexError):
            pass
    response = FileResponse(open(path, 'rb'), content_type=content_type)
    response['Content-Length'] = str(size)
    response['Accept-Ranges'] = 'bytes'
    return response


def serve_service_video(request, pk):
    """Раздаёт видео услуги с поддержкой Range (для воспроизведения в карточке)."""
    from core.models import Service
    service = Service.objects.filter(pk=pk).first()
    if not service or service.media_type != 'video' or not service.video:
        raise Http404('Video not found')
    return _serve_video_with_range(request, service.video.path)


def _service_detail_url(service, request):
    """Возвращает URL страницы услуги или заказа (по умолчанию)."""
    from django.urls import reverse
    title = (service.title or '').strip()
    if title in ('Подбор авто на аукционах', 'Поиск авто'):
        return reverse('car_search')
    if title == 'Выкуп':
        return reverse('buyout')
    if title in ('Доставка авто', 'Доставка', 'Логистика', 'Логистические услуги') or service.id == 3:
        return reverse('delivery')
    if title in ('Продажа мотоциклов', 'Мотоциклы', 'Продажа мото') or service.id == 5:
        return reverse('motorcycle_sales')
    if title in ('Постановка на учет', 'Постановка на учёт', 'Оформление') or service.id == 4:
        return reverse('registration')
    return reverse('order_quiz')


def services(request):
    from core.models import Service
    service_list = list(Service.objects.all())
    services_with_urls = []
    has_motorcycle_service = False
    for s in service_list:
        if (s.title or '').strip().lower() in ('продажа мотоциклов', 'мотоциклы', 'продажа мото'):
            has_motorcycle_service = True
        services_with_urls.append({
            'service': s,
            'detail_url': _service_detail_url(s, request),
        })
    return render(request, 'pages/services.html', {
        'services_with_urls': services_with_urls,
        'has_motorcycle_service': has_motorcycle_service,
    })


def motorcycle_sales(request):
    return render(request, 'pages/motorcycle_sales.html')


def _catalog_car_description(car):
    """Возвращает описание авто: из БД или сгенерированное по данным."""
    if car.description and car.description.strip():
        return car.description.strip()

    country = car.get_country_display()
    parts = [f'{car.title} из {country}.']
    details = []
    if car.year:
        details.append(f'Год: {car.year}')
    if car.engine_type:
        details.append(f'Двигатель: {car.engine_type}')
    if car.mileage:
        details.append(f'Пробег: {car.mileage}')
    if details:
        parts.append(' '.join(details) + '.')
    parts.append('Подбор, проверка, доставка и оформление под ключ.')
    return ' '.join(parts)


def process(request):
    return render(request, 'pages/process.html')


def about(request):
    return render(request, 'pages/about.html')


def catalog(request):
    from core.models import CatalogCar
    cars = list(CatalogCar.objects.filter(is_active=True))
    for car in cars:
        car.ui_description = _catalog_car_description(car)
    countries = [('all', 'Все')]
    for code, label in CatalogCar.Country.choices:
        if any(c.country == code for c in cars):
            countries.append((code, label))
    statuses = [('all', 'Все')]
    for code, label in CatalogCar.Status.choices:
        if any(c.status == code for c in cars):
            statuses.append((code, label))
    return render(request, 'pages/catalog.html', {
        'cars': cars,
        'countries': countries,
        'statuses': statuses,
    })


def catalog_detail(request, pk):
    from core.models import CatalogCar
    from django.shortcuts import get_object_or_404
    car = get_object_or_404(CatalogCar, pk=pk, is_active=True)
    car.ui_description = _catalog_car_description(car)
    gallery = car.gallery.all()
    related = list(CatalogCar.objects.filter(is_active=True).exclude(pk=pk)[:3])
    for item in related:
        item.ui_description = _catalog_car_description(item)
    return render(request, 'pages/catalog_detail.html', {
        'car': car, 'gallery': gallery, 'related': related,
    })


def serve_catalog_video(request, pk):
    """Раздаёт видео авто из каталога с поддержкой Range."""
    from core.models import CatalogCar
    car = CatalogCar.objects.filter(pk=pk).first()
    if not car or not car.video:
        raise Http404('Video not found')
    return _serve_video_with_range(request, car.video.path)


def cases(request):
    from core.models import Case
    case_list = Case.objects.filter(is_active=True)
    return render(request, 'pages/cases.html', {'cases': case_list})


def serve_case_video(request, pk):
    """Раздаёт видео кейса с поддержкой Range."""
    from core.models import Case
    case = Case.objects.filter(pk=pk).first()
    if not case or case.media_type != 'video' or not case.video:
        raise Http404('Video not found')
    return _serve_video_with_range(request, case.video.path)


def blog(request):
    from core.models import BlogPost
    posts = BlogPost.objects.filter(is_published=True)
    return render(request, 'pages/blog.html', {'posts': posts})


def blog_detail(request, slug):
    from core.models import BlogPost
    from django.shortcuts import get_object_or_404
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    related = BlogPost.objects.filter(is_published=True).exclude(pk=post.pk)[:3]
    return render(request, 'pages/blog_detail.html', {'post': post, 'related': related})


def serve_blog_video(request, pk):
    """Раздаёт видео статьи блога с поддержкой Range."""
    from core.models import BlogPost
    post = BlogPost.objects.filter(pk=pk).first()
    if not post or not post.video:
        raise Http404('Video not found')
    return _serve_video_with_range(request, post.video.path)


def team(request):
    from core.models import TeamMember
    members = TeamMember.objects.filter(is_active=True)
    return render(request, 'pages/team.html', {'members': members})


def contacts(request):
    return render(request, 'pages/contacts.html')


# ---------- Пример маршрутов с куки-сессией ----------

def login_view(request):
    """Устанавливает session_token в куки и перенаправляет на профиль."""
    response = redirect('profile')
    set_session_cookie(response)
    return response


def profile_view(request):
    """
    Страница профиля: доступна только при наличии валидной куки session_token.
    Если куки нет — перенаправление на /login/ (для API можно вернуть 401).
    """
    token = get_session_cookie(request)
    if not token:
        # Для API: return HttpResponse(status=401)
        return redirect('login')
    return render(request, 'pages/profile.html', {'session_token': token[:8] + '…'})


def logout_view(request):
    """Выход: удаляет куки session_token и перенаправляет на главную."""
    response = redirect('home')
    delete_session_cookie(response)
    return response


def serve_media(request, path):
    """
    Раздача медиа-файлов (фото, видео из media/) при любом DEBUG.
    В production встроенный static(DEBUG) может не отдавать файлы — этот view всегда отдаёт.
    """
    from pathlib import Path

    media_root = Path(settings.MEDIA_ROOT).resolve()
    file_path = (media_root / path).resolve()
    if not file_path.is_file():
        raise Http404
    if not str(file_path).startswith(str(media_root)):
        raise Http404
    content_type = None
    if path.lower().endswith(('.jpg', '.jpeg')):
        content_type = 'image/jpeg'
    elif path.lower().endswith('.png'):
        content_type = 'image/png'
    elif path.lower().endswith('.gif'):
        content_type = 'image/gif'
    elif path.lower().endswith('.webp'):
        content_type = 'image/webp'
    elif path.lower().endswith('.mp4'):
        content_type = 'video/mp4'
    return FileResponse(open(file_path, 'rb'), content_type=content_type or 'application/octet-stream')
