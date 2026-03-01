from django.shortcuts import render, redirect
from config.cookies import (
    set_session_cookie,
    get_session_cookie,
    delete_session_cookie,
)


def home(request):
    return render(request, 'pages/home.html')


def services(request):
    return render(request, 'pages/services.html')


def process(request):
    return render(request, 'pages/process.html')


def about(request):
    return render(request, 'pages/about.html')


def cases(request):
    return render(request, 'pages/cases.html')


def team(request):
    return render(request, 'pages/team.html')


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
