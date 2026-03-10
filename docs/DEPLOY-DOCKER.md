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

- Сайт: `http://IP_ВАШЕГО_СЕРВЕРА` (порт 80) или `http://IP_ВАШЕГО_СЕРВЕРА:8000`
- Админка: `http://IP_ВАШЕГО_СЕРВЕРА/admin/` или `http://IP_ВАШЕГО_СЕРВЕРА:8000/admin/`

Войдите под созданным суперпользователем.

### Шаг 3.6. Доступ без порта в URL (порт 80)

Чтобы сайт открывался по адресу `http://IP/` без `:8000`, в `docker-compose.yml` проброшен порт **80**. На сервере откройте порт 80 в файрволе:

```bash
sudo ufw allow 80/tcp
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

После обновления кода с новым `docker-compose.yml` пересоберите и перезапустите: `docker compose up -d`.

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

### Деплой на VPS Beget

- **Конфигурация:** минимум 2 ядра, 2 ГБ RAM, 30 ГБ NVMe.
- **ОС:** выберите **Ubuntu 22.04** или готовое решение «Docker».
- **Доступ:** укажите пароль root или добавьте SSH-ключ; после создания сервера придёт письмо с IP и паролем.

Дальше выполняйте шаги из **Части 2** (SSH, установка Docker) и **Части 3** (клонирование, `.env`, `docker compose build` и `up -d`).

### Деплой на любой другой VPS

1. Клонировать репозиторий на сервер.
2. Создать `.env` с `DJANGO_SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS=ip-или-домен`.
3. Запустить: `docker compose build` и `docker compose up -d`.
4. При необходимости настроить Nginx как reverse proxy на порт 8000 и SSL.

### Домен и HTTPS

Чтобы открывать сайт по домену и по HTTPS:

1. В панели регистратора домена создайте A-запись на IP вашего VPS.
2. На сервере установите Nginx и Certbot (Let's Encrypt).
3. Настройте Nginx как reverse proxy на `127.0.0.1:8000` и выдайте сертификат для домена.

Отдельная инструкция по Nginx + SSL может быть добавлена в этот документ по запросу.

---

## Если сайт не открывается (ERR_CONNECTION_REFUSED)

Подключитесь по SSH и выполните по шагам.

### 1. Контейнер запущен?

```bash
cd /opt/autopark   # или ваш путь к проекту
docker compose ps
```

Должен быть контейнер `autopark-web` (или `web`) в состоянии **Up**. Если **Exited** — смотрите логи:

```bash
docker compose logs web
```

Исправьте ошибки (миграции, статика, `DJANGO_SECRET_KEY` в `.env`) и перезапустите:

```bash
docker compose up -d
```

### 2. Порт 8000 слушается на сервере?

```bash
ss -tlnp | grep 8000
# или
sudo netstat -tlnp | grep 8000
```

Должна быть строка с `0.0.0.0:8000` или `*:8000`. Если пусто — контейнер не пробросил порт или упал.

### 3. Файрвол разрешает порт 8000?

На Ubuntu часто включён **ufw**. Разрешите входящий доступ на 8000 и при необходимости включите ufw:

```bash
sudo ufw allow 8000/tcp
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

После этого снова откройте в браузере: `http://155.212.211.206:8000` (обязательно с портом **:8000**).

### 4. Порт указан в адресе?

Сайт слушает порт **8000**. Открывать нужно именно:

- `http://155.212.211.206:8000`

а не `http://155.212.211.206` (без порта браузер подставляет 80, и соединение будет отклонено).

### 5. Файрвол хостинга (Beget и др.)

В панели управления VPS проверьте правила входящего трафика (Firewall / Security groups). Должен быть разрешён входящий TCP на порт **8000** с любого IP (0.0.0.0/0 или «все»).

### 6. ALLOWED_HOSTS

Если соединение уже устанавливается, но Django отдаёт 400 Bad Request — добавьте IP сервера в `.env`:

```env
ALLOWED_HOSTS=155.212.211.206,localhost,127.0.0.1
```

Затем перезапустите контейнеры:

```bash
docker compose up -d
```

---

## Синхронизация БД: данные с локальной машины на сервер

Чтобы на сервере отображались те же данные, что и локально (услуги, кейсы, команда, каталог авто и т.д.), нужно один раз или по необходимости скопировать локальную базу SQLite на сервер в контейнер.

### Вариант 1: Локально проект запущен без Docker

База лежит в корне проекта: `db.sqlite3`. Дальше — по шагам ниже (скрипт или вручную).

### Вариант 2: Локально проект в Docker

Сначала вытащите БД из контейнера в папку проекта:

```powershell
docker cp autopark-web:/data/db.sqlite3 .\db.sqlite3
```

После этого в корне появится `db.sqlite3` — с ним выполняйте шаги ниже.

### Загрузка БД на сервер вручную

1. **Скопировать файл на сервер** (из корня проекта, где лежит `db.sqlite3`):

   ```powershell
   scp db.sqlite3 USER@155.212.211.206:/opt/autopark/
   ```
   Подставьте `USER` (например, `root` или `ubuntu`) и при необходимости путь к ключу: `-i C:\path\to\key`.

2. **На сервере** по SSH:

   ```bash
   cd /opt/autopark
   docker cp db.sqlite3 autopark-web:/data/db.sqlite3
   docker compose restart web
   ```

После этого сайт на сервере будет отдавать те же данные, что и локальная БД.

### Загрузка БД скриптом (Windows)

В корне проекта есть скрипт `scripts/sync-db-to-server.ps1`. Перед первым запуском задайте в нём (или в переменных окружения) хост и пользователя сервера. Запуск:

```powershell
.\scripts\sync-db-to-server.ps1
```

Скрипт копирует локальный `db.sqlite3` на сервер и перезапускает контейнер `web`.

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
| Выгрузить локальную БД на сервер | Локально: `.\scripts\sync-db-to-server.ps1` (задать DEPLOY_HOST, DEPLOY_USER) |
