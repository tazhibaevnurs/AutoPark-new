# AUTOPARK

Сайт компании по импорту авто (США, Китай, Корея). Django, статика, заявки, админка.

## Локально (без Docker)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # задайте DJANGO_SECRET_KEY и др.
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Docker

```bash
cp .env.example .env
# В .env задайте DJANGO_SECRET_KEY и ALLOWED_HOSTS (через запятую)

docker compose build
docker compose up -d

# Создать суперпользователя
docker compose exec web python manage.py createsuperuser
```

Сайт: http://localhost:8000  
Админка: http://localhost:8000/admin/

## Git

```bash
git init
git add .
git commit -m "Initial: Django Autopark + Docker"
git remote add origin <URL-репозитория>
git push -u origin main
```

## Деплой на сервер

1. Клонировать репозиторий на сервер.
2. Создать `.env` с `DJANGO_SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS=your-domain.com`.
3. Запустить: `docker compose up -d`.
4. При необходимости настроить Nginx как reverse proxy на порт 8000 и SSL.
