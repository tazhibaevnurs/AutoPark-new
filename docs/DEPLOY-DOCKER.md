# Пошаговое руководство: загрузка на сервер через Docker

Полная последовательность от репозитория до работающего сайта на VPS.

---

## Часть 1. Подготовка проекта на компьютере

### Шаг 1.1. Проверка файлов проекта

Убедитесь, что в корне проекта есть:

- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`
- `.env.example`
- Папки: `config/`, `core/`, `leads/`, `pages/`, `templates/`, `static/`

### Шаг 1.2. Инициализация Git и загрузка в репозиторий

```bash
cd /путь/к/Autopark-new

# Если репозиторий ещё не создан
git init
git add .
git commit -m "Initial: Django Autopark + Docker"

# Подключите удалённый репозиторий (GitHub, GitLab, Beget Git и т.д.)
git remote add origin https://github.com/ВАШ_ЛОГИН/autopark.git
git branch -M main
git push -u origin main
```

Если репозиторий уже есть — просто сделайте `git push`, чтобы все последние изменения были на GitHub/GitLab.

### Шаг 1.3. Что должно быть в репозитории

В репозитории должны быть: весь код приложения, `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `.env.example`. Файл `.env` в репозиторий не класть (он в `.gitignore`).

---

## Часть 2. Подготовка сервера (VPS)

### Шаг 2.1. Подключение по SSH

Используйте IP-адрес и пароль (или SSH-ключ), которые выдал хостинг после создания сервера.

```bash
ssh root@IP_АДРЕС_СЕРВЕРА
```

Либо, если логин другой (например, `ubuntu`):

```bash
ssh ubuntu@IP_АДРЕС_СЕРВЕРА
```

Введите пароль при запросе. Вы окажетесь в консоли сервера.

### Шаг 2.2. Установка Docker (если ещё не установлен)

Для **Ubuntu 22.04** выполните по порядку:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl

sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Проверка:

```bash
docker --version
docker compose version
```

Должны вывести версии без ошибок.

### Шаг 2.3. Установка Git (если нет)

```bash
sudo apt-get update
sudo apt-get install -y git
git --version
```

---

## Часть 3. Загрузка проекта на сервер и запуск контейнеров

### Шаг 3.1. Клонирование репозитория

На сервере выберите каталог для проекта (например, `/opt` или домашний каталог):

```bash
sudo mkdir -p /opt
cd /opt
sudo git clone https://github.com/ВАШ_ЛОГИН/autopark.git
cd autopark
```

Замените URL на адрес вашего репозитория. Если доступ по HTTPS запрашивает логин/пароль — используйте токен или настройте SSH-ключ и клонируйте по SSH (`git@github.com:...`).

Если клонировали под `root`, права обычно уже подходящие. Если под другим пользователем:

```bash
sudo chown -R $USER:$USER /opt/autopark
```

### Шаг 3.2. Создание файла .env

Файл `.env` не хранится в Git. Его нужно создать на сервере вручную:

```bash
cd /opt/autopark
cp .env.example .env
nano .env
```

Заполните переменные (сохраните: `Ctrl+O`, Enter, выход: `Ctrl+X`):

```env
DJANGO_SECRET_KEY=ваш-длинный-секретный-ключ-минимум-50-символов
DEBUG=False
ALLOWED_HOSTS=IP_ВАШЕГО_СЕРВЕРА,ваш-домен.ru
DATABASE_PATH=/data/db.sqlite3
```

- **DJANGO_SECRET_KEY** — случайная строка. Сгенерировать можно так (на сервере или локально):
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(50))"
  ```
- **ALLOWED_HOSTS** — через запятую без пробелов: IP сервера и домен (если есть).
- **DATABASE_PATH** — для Docker оставьте `/data/db.sqlite3`.

### Шаг 3.3. Сборка и запуск контейнеров

В каталоге проекта на сервере:

```bash
cd /opt/autopark
docker compose build
docker compose up -d
```

- `build` — собирает образ по `Dockerfile`.
- `up -d` — запускает контейнер в фоне.

Проверка:

```bash
docker compose ps
```

Должен быть запущен сервис `web` на порту 8000.

### Шаг 3.4. Создание суперпользователя (админка)

Чтобы заходить в админ-панель:

```bash
docker compose exec web python manage.py createsuperuser
```

Введите логин, email и пароль по запросу.

### Шаг 3.5. Проверка работы сайта

В браузере откройте:

- Сайт: `http://IP_ВАШЕГО_СЕРВЕРА:8000`
- Админка: `http://IP_ВАШЕГО_СЕРВЕРА:8000/admin/`

Войдите под созданным суперпользователем.

---

## Часть 4. Дальнейшие действия

### Обновление кода на сервере

После изменений в репозитории:

```bash
cd /opt/autopark
git pull origin main
docker compose build
docker compose up -d
```

При изменении моделей может понадобиться:

```bash
docker compose exec web python manage.py migrate
```

### Просмотр логов

```bash
docker compose logs -f web
```

Выход из логов: `Ctrl+C`.

### Остановка и удаление контейнеров

```bash
cd /opt/autopark
docker compose down
```

Данные в томах (БД, медиа) сохранятся. Полное удаление с томами:

```bash
docker compose down -v
```

### Домен и HTTPS

Чтобы открывать сайт по домену и по HTTPS:

1. В панели регистратора домена создайте A-запись на IP вашего VPS.
2. На сервере установите Nginx и Certbot (Let's Encrypt).
3. Настройте Nginx как reverse proxy на `127.0.0.1:8000` и выдайте сертификат для домена.

Отдельная инструкция по Nginx + SSL может быть добавлена в этот документ по запросу.

---

## Краткая шпаргалка команд

| Действие | Команда |
|----------|--------|
| Подключиться к серверу | `ssh root@IP_СЕРВЕРА` |
| Зайти в папку проекта | `cd /opt/autopark` |
| Собрать образы | `docker compose build` |
| Запустить контейнеры | `docker compose up -d` |
| Остановить | `docker compose down` |
| Логи | `docker compose logs -f web` |
| Суперпользователь | `docker compose exec web python manage.py createsuperuser` |
| Обновить код | `git pull` → `docker compose build` → `docker compose up -d` |
