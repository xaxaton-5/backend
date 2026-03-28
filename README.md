# Backend

Проект запускается в Docker Compose и состоит из двух сервисов:

- `web` - Django API на порту `8000`
- `messaging` - FastAPI/WebSocket messaging service на порту `5001`

## Что нужно

- Docker
- Docker Compose

## Быстрый запуск

Из корня проекта:

```bash
docker compose up --build
```

После запуска будут доступны:

- Django API: [http://localhost:8000](http://localhost:8000)
- Django admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- Messaging service docs: [http://localhost:5001/docs](http://localhost:5001/docs)
- WebSocket endpoint: `ws://localhost:5001/ws?access_token=<token>`

## Как это работает

При старте контейнера `web` автоматически выполняются команды:

```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Это значит:

- миграции применяются автоматически
- сид-данные создаются через миграции автоматически

Если вы перезапускаете сервис через `docker compose up`, данные могут быть пересозданы.

## Данные для входа

После применения миграций создаются тестовые пользователи. Для всех аккаунтов пароль одинаковый:

- Пароль: `password123`

Взрослые аккаунты (родители), которые создаются по умолчанию:

- `ivan.petrov@example.com`
- `maria.sokolova@example.com`
- `sergey.ivanov@example.com`
- `elena.smirnova@example.com`

Детские аккаунты, которые создаются по умолчанию:

- `alexey.petrov@example.com`
- `olga.sokolova@example.com`
- `nikita.ivanov@example.com`
- `alina.smirnova@example.com`
- `egor.kozlov@example.com`
- `polina.fedorova@example.com`
- `maksim.novikov@example.com`
- `sofia.orlova@example.com`

Если нужен вход именно под ребёнком, используйте любой email из блока детских аккаунтов.
Если нужен вход именно под взрослым, используйте любой email из блока взрослых аккаунтов.

Примеры логинов (`username`), которые создаются по умолчанию:

- взрослые: `МаминКодер`, `СуперКодер`, `Сергей Иванов`, `Елена Смирнова`
- дети: `Программист2000`, `КодикОгонь`, `Никита Иванов`, `Алина Смирнова`, `Полина Федорова`, `София Орлова`

Если база уже была создана раньше, для повторного применения сидов обычно нужно пересоздать том базы данных и заново выполнить миграции.

## Основные команды

Запуск в фоне:

```bash
docker compose up -d --build
```

Остановка:

```bash
docker compose down
```

Остановка с удалением томов:

```bash
docker compose down -v
```

Просмотр логов:

```bash
docker compose logs -f
```

Пересобрать только один сервис:

```bash
docker compose build web
docker compose build messaging
```

## Тома Docker

В проекте используются volume'ы:

- `django_sqlite_data` - SQLite база Django в `/app/data/db.sqlite3`
- `messaging_logs` - логи messaging service в `/app/log`

## Переменные окружения

### `web`

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `MESSAGING_SERVICE_URL`
- `EMAIL_SENDER`
- `EMAIL_PASSWORD`

### `messaging`

- `CORE_URL`
- `MESSAGING_HOST`
- `MESSAGING_PORT`
- `MESSAGING_DEBUG`
- `MESSAGING_UVICORN_WORKERS`
- `LOG_LEVEL`

Сейчас все нужные значения уже заданы в `docker-compose.yml`.

## Полезные API-эндпоинты

### Django

- `GET /api/users/list/`
- `GET /api/user/detail/<user_id>/`
- `POST /api/register/`
- `POST /api/login/`
- `GET /api/auth/`
- `GET /api/achievements/list/`
- `GET /api/messages/list/`
- `POST /api/messages/send/`

### Messaging service

- `POST /notify/send`
- `POST /message/send`
- `POST /users/list`
- `WS /ws?access_token=<token>`

## Структура проекта

```text
.
|-- docker-compose.yml
|-- prog_game/           # Django-приложение
`-- messaging_service/   # FastAPI/WebSocket сервис
```
