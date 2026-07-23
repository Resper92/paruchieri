# Parrucchieri Booking

Сервис записи в парикмахерскую/салон. Backend на FastAPI + PostgreSQL, frontend на Angular.

## Стек

- **Backend**: FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, JWT (OAuth2 password flow), архитектура — DDD/hexagonal (domain → application → infrastructure/api)
- **Frontend**: Angular 22 (standalone-компоненты, signals), Reactive Forms
- **Роли**: `superadmin`, `parrucchiere` (владелец салона), `client`

## Структура репозитория

Backend собран по DDD/hexagonal: domain ничего не знает про FastAPI/SQLAlchemy, infrastructure реализует интерфейсы (порты), которые определяет domain, а api — это просто ещё один адаптер сверху. Подробный разбор слоёв, сквозной пример запроса и шаблон "как добавить фичу" — в [ARCHITECTURE.md](ARCHITECTURE.md).

```
app/
  domain/                      # чистый Python, без зависимостей от фреймворков
    entities/                  # User, Salon, Staff, Service, Appointment — dataclass'ы
    repositories/              # Protocol-интерфейсы (порты): UserRepository и т.д.
    role.py                    # Role enum
    exceptions.py              # NotFoundError, PermissionDeniedError, ConflictError, ...
    policies.py                # ensure_role, ensure_can_manage_salon — бизнес-правила

  application/                 # use cases — оркестрируют domain, не знают про HTTP/SQL
    ports.py                   # PasswordHasher, TokenService — интерфейсы для infrastructure
    use_cases/                 # RegisterUserUseCase, CreateSalonUseCase, BookAppointmentUseCase...

  infrastructure/               # адаптеры: конкретные реализации портов domain/application
    config.py                   # Settings (pydantic-settings)
    security.py                 # BcryptPasswordHasher, JwtTokenService
    db/
      models/                   # SQLAlchemy ORM-модели (persistence, отдельно от domain-сущностей)
      session.py                # engine, SessionLocal, get_db
    repositories/               # SqlAlchemy*Repository — implements domain/repositories/*

  api/                          # presentation-слой: FastAPI поверх use cases
    deps.py                     # composition root — тут всё связывается (DI)
    error_handlers.py           # domain-исключения -> HTTP-статусы
    v1/
      schemas/                  # Pydantic DTO для запросов/ответов
      endpoints/                # роуты — тонкие, только вызывают use case

  scripts/                     # разовые CLI-скрипты (создание superadmin)
  main.py

alembic/               # миграции БД
frontend/              # Angular-приложение
  Dockerfile           # multi-stage: ng build -> nginx (для docker-compose)
  nginx.conf           # SPA fallback (try_files -> index.html)
dockerfile             # backend-образ (uvicorn)
docker-compose.yml     # Postgres + API + Frontend
dev.sh                 # локальный запуск backend+frontend с hot-reload
```

Поток запроса, например создание салона: `endpoint (api/v1/endpoints/salons.py)` достаёт `current_user` через `get_current_user` (JWT), вызывает `CreateSalonUseCase.execute(...)` → use case проверяет `ensure_role` (domain policy), строит `Salon`-сущность, отдаёт в `SalonRepository` (порт) → `deps.py` подставляет туда `SqlAlchemySalonRepository` (адаптер) → тот пишет в Postgres через ORM-модель и возвращает обратно domain-сущность → endpoint сериализует её в `SalonRead` (Pydantic). Domain-исключения (`NotFoundError`, `PermissionDeniedError`, `ConflictError`) ловятся глобально в `api/error_handlers.py` и превращаются в 404/403/400 — эндпоинтам не нужно знать про HTTP-статусы вообще.

## Быстрый старт — два варианта

### Вариант A: всё в Docker (ничего локально ставить не нужно)

```bash
docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python -m app.scripts.create_superadmin --email admin@example.com --password ChangeMe123!
```

- frontend — http://localhost:4200 (Angular, собран и раздаётся через nginx)
- backend — http://localhost:8000 (Swagger: `/docs`)
- Postgres — доступен с хоста на `localhost:5433`

Без hot-reload: если правите код, нужно пересобрать (`docker compose up -d --build <service>`). Для активной разработки удобнее вариант B.

### Вариант B: `./dev.sh` — hot-reload для локальной разработки

```bash
./dev.sh
```

Поднимает Postgres в Docker, создаёт `.venv` и ставит зависимости backend (если ещё нет), прогоняет миграции, ставит зависимости frontend (если ещё нет) и запускает **и backend (`uvicorn --reload`), и frontend (`ng serve`)** одновременно, с live-reload на изменения кода:

- backend — http://localhost:8000 (Swagger: `/docs`)
- frontend — http://localhost:4200

`Ctrl+C` останавливает backend и frontend; Postgres продолжает работать в фоне (данные не теряются). Первый superadmin всё равно нужно завести отдельно — см. §1.6.

Дальше — по шагам, если нужно запускать вручную или разбираться, что происходит внутри `dev.sh`.

## 1. Backend

### 1.1 Требования

- Python 3.12+
- Docker (для Postgres) — либо свой локальный Postgres

### 1.2 Установка зависимостей

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 1.3 Конфигурация (`.env`)

Файл `.env` в корне репозитория уже содержит рабочие значения для локальной разработки:

```
DB_USER=user
DB_PASSWORD=qwerty
DB_HOST=localhost:5433
DB_NAME=booking_db
```

Порт `5433` (а не стандартный `5432`) — намеренно: если у вас уже крутится другой локальный Postgres на 5432 (частый случай), `docker-compose up db` не будет с ним конфликтовать. Внутри docker-сети сервисы всё равно видят друг друга по имени (`db:5432`) — это меняет только порт, видимый с хоста.

Для выпуска JWT используется `SECRET_KEY` (см. `app/infrastructure/config.py`) — если не задать, используется дефолтный dev-ключ. Для чего-то серьёзнее локальной разработки добавьте в `.env`:

```
SECRET_KEY=<длинная случайная строка>
```

### 1.4 Поднять базу данных

```bash
docker-compose up -d db
```

Поднимет Postgres 16, доступный с хоста на `localhost:5433` (см. `docker-compose.yml`).

### 1.5 Прогнать миграции

```bash
alembic upgrade head
```

Создаст все таблицы (`users`, `salons`, `salon_staff`, `services`, `appointments`) и добавит enum/CHECK-ограничение на `users.role`.

### 1.6 Завести первого superadmin

Через `/auth/register` роль `superadmin` создать нельзя — это заблокировано специально (иначе кто угодно мог бы зарегистрироваться администратором). Первого superadmin создаём напрямую в БД скриптом:

```bash
python -m app.scripts.create_superadmin --email admin@example.com --password ChangeMe123!
```

Скрипт идемпотентен: если пользователь с таким email уже существует — он получит роль `superadmin` и новый пароль; если нет — будет создан.

Дальше новых superadmin'ов можно назначать через самого этого superadmin: залогиниться и вызвать `PATCH /api/v1/admin/users/{id}/role` (или через страницу **Admin** в интерфейсе).

### 1.7 Запустить API

```bash
uvicorn app.main:app --reload
```

Swagger UI: http://localhost:8000/docs
Health-check: http://localhost:8000/health

### 1.8 Альтернатива: всё через docker-compose

```bash
docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python -m app.scripts.create_superadmin --email admin@example.com --password ChangeMe123!
```

Поднимет Postgres, API (`http://localhost:8000`) и frontend (`http://localhost:4200`, см. §2) одной командой. Миграции и сид superadmin внутри контейнера не выполняются автоматически при старте — прогонять их нужно вручную (команды выше), один раз на новую базу.

## 2. Frontend

Локально с hot-reload:

```bash
cd frontend
npm install
npx ng serve
```

Приложение поднимется на http://localhost:4200 и будет ходить на backend по адресу из `frontend/src/environments/environment.ts` (по умолчанию `http://localhost:8000/api/v1`). Если backend крутится на другом хосте/порту — поменяйте `apiUrl` там.

Либо в Docker (без hot-reload, production-style build через nginx — см. `frontend/Dockerfile`):

```bash
docker compose up -d --build frontend
```

## 3. Роли и доступы

| Действие                                   | client | parrucchiere              | superadmin |
|---------------------------------------------|--------|----------------------------|------------|
| Просмотр салонов/услуг                      | ✅     | ✅                          | ✅          |
| Создание салона                             | ❌     | ✅ (становится владельцем)  | ✅          |
| Управление staff/services своего салона     | ❌     | ✅ (только своих салонов)   | ✅ (любых)  |
| Бронирование appointment                    | ✅ (себе) | ❌ (интерфейс скрыт)     | —          |
| Просмотр appointments                       | только свои | только своего салона  | все        |
| Управление пользователями (`/admin/users`)  | ❌     | ❌                          | ✅          |

Права проверяются не на уровне роутов, а внутри use cases (`app/application/use_cases/`) через `ensure_role` / `ensure_can_manage_salon` (`app/domain/policies.py`) — это часть бизнес-правил, а не HTTP-обвязки: `api/` только достаёт текущего пользователя из JWT и передаёт его в use case, дальше решение о доступе принимает domain. Frontend дополнительно скрывает недоступные разделы через `roleGuard` и условную вёрстку — это только UX, реальная защита всегда на backend.

## 4. Быстрая проверка сценария

1. `./dev.sh`, либо `docker compose up -d --build` (вариант A выше).
2. Завести superadmin скриптом из §1.6 (локально) или через `docker compose exec api ...` (в Docker).
3. Открыть http://localhost:4200/login, зайти под superadmin.
4. На `/register` зарегистрировать пользователя с ролью `parrucchiere` — под ним создать салон, staff, services.
5. Зарегистрировать пользователя с ролью `client` — под ним забронировать appointment на созданную услугу.
6. Под superadmin открыть `/admin` — увидеть всех пользователей, поменять кому-нибудь роль.
