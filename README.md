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

## Деплой на сервер через Docker

**Пошаговое руководство:** [docs/DEPLOY-DOCKER.md](docs/DEPLOY-DOCKER.md) — от подготовки проекта и Git до запуска контейнеров на VPS и обновления кода.

---

## Деплой на VPS Beget

### 1. Настройка сервера в панели Beget

- **Конфигурация:** минимум 2 ядра, 2 ГБ RAM, 30 ГБ NVMe (достаточно для Django + Docker).
- **Готовое решение:** выберите **Ubuntu 22.04** (бесплатно) — на нём удобно ставить Docker и управлять контейнерами. Вариант «Docker» из готовых решений тоже подойдёт, если Beget уже установил Docker.
- **Аутентификация:** укажите пароль или добавьте SSH-ключ — пароль потом придёт на email, если не задали.

Дождитесь создания сервера и письма с IP и паролем (или используйте SSH-ключ).

### 2. Подключение по SSH

```bash
ssh root@IP_ВАШЕГО_СЕРВЕРА
# или: ssh ubuntu@IP_ВАШЕГО_СЕРВЕРА  — если логин не root
```

Введите пароль из письма или используйте ключ.

### 3. Установка Docker на Ubuntu (если выбрали Ubuntu 22.04)

```bash
apt-get update && apt-get install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Проверка: `docker --version` и `docker compose version`.

### 4. Клонирование проекта и запуск

На сервере:

```bash
cd /opt
git clone https://github.com/ВАШ_ЛОГИН/autopark.git
cd autopark
```

Создайте `.env`:

```bash
cp .env.example .env
nano .env
```

Заполните (обязательно):

- `DJANGO_SECRET_KEY` — длинная случайная строка (можно сгенерировать: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`).
- `DEBUG=False`
- `ALLOWED_HOSTS=IP_СЕРВЕРА,ваш-домен.ru` — через запятую, без пробелов.

Запуск:

```bash
docker compose build
docker compose up -d
```

Создание суперпользователя для админки:

```bash
docker compose exec web python manage.py createsuperuser
```

Сайт будет доступен по адресу: **http://IP_ВАШЕГО_СЕРВЕРА:8000**

### 5. Домен и HTTPS (по желанию)

Если у вас есть домен (например, на Beget или другом регистраторе):

1. Направьте A-запись домена на IP вашего VPS.
2. На сервере поставьте Nginx и Certbot, настройте reverse proxy на `127.0.0.1:8000` и получите сертификат Let's Encrypt.

Либо используйте встроенные возможности Beget по привязке домена к VPS, если они есть в панели.

---

## Деплой на любой сервер (кратко)

1. Клонировать репозиторий на сервер.
2. Создать `.env` с `DJANGO_SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS=your-domain.com`.
3. Запустить: `docker compose up -d`.
4. При необходимости настроить Nginx как reverse proxy на порт 8000 и SSL.
