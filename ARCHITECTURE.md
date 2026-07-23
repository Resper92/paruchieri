# Архитектура backend: DDD / Hexagonal

Этот документ объясняет **как** устроен backend и **почему** именно так — в дополнение к README (там просто "как запустить"). Если нужно добавить фичу или разобраться, куда что писать — этот файл для этого.

## Идея одним абзацем

Код разложен на слои так, чтобы бизнес-правила (кто может забронировать, кто владеет салоном, какая роль что может) не были размазаны по роутам и не зависели от того, что мы используем FastAPI, SQLAlchemy или bcrypt. Слой `domain` не импортирует **ничего** из FastAPI/SQLAlchemy — это обычный Python. Всё остальное (`infrastructure`, `api`) зависит от `domain`, но не наоборот. Если завтра Postgres превратится в MongoDB, а FastAPI — в Flask, `domain/` и `application/` не поменяются ни на строчку.

## Правило зависимостей

```
        api  →  application  →  domain
          ↓                        ↑
   infrastructure  ────────────────┘
```

- **domain** ничего не знает ни о ком. Только Python + собственные правила.
- **application** знает про `domain`, но не знает, что `UserRepository` реализован через SQLAlchemy, а `PasswordHasher` — через bcrypt. Он просит абстракцию (порт), а откуда она взялась — не его дело.
- **infrastructure** знает про `domain` (реализует его интерфейсы) и про конкретные технологии (SQLAlchemy, bcrypt, PyJWT).
- **api** знает про всё — это единственное место, где всё это физически связывается вместе (composition root, `app/api/deps.py`).

Если вы правите `app/domain/*` и видите импорт `sqlalchemy` или `fastapi` — это сигнал, что что-то не так спроектировано.

## Слои подробно

### 1. `app/domain/` — бизнес-правила, чистый Python

```
domain/
  entities/           User, Salon, Staff, Service, Appointment — @dataclass
  role.py             Role(str, Enum): SUPERADMIN, PARRUCCHIERE, CLIENT
  repositories/        Protocol-интерфейсы: UserRepository, SalonRepository, ...
  exceptions.py        DomainError, NotFoundError, PermissionDeniedError, ConflictError, InvalidCredentialsError
  policies.py          ensure_role(...), ensure_can_manage_salon(...)
```

**Entities** — просто данные + немного поведения, которое естественно живёт на самой сущности:

```python
# app/domain/entities/salon.py
@dataclass
class Salon:
    id: int | None
    owner_id: int
    name: str
    address: str | None

    def is_owned_by(self, user_id: int) -> bool:
        return self.owner_id == user_id
```

**Repositories** — это **порты** (в терминах hexagonal architecture). Domain объявляет, что ему нужно, но не реализует это:

```python
# app/domain/repositories/salon_repository.py
class SalonRepository(Protocol):
    def get(self, salon_id: int) -> Salon | None: ...
    def get_multi(self, skip: int = 0, limit: int = 100) -> list[Salon]: ...
    def add(self, salon: Salon) -> Salon: ...
```

Это `typing.Protocol`, а не `ABC` — структурная типизация: любой класс с такими методами подходит, явно наследоваться не нужно. Реализация лежит в `infrastructure/`, но domain про неё не знает.

**Policies** — бизнес-правила, которые не принадлежат одной сущности, а касаются взаимодействия (пользователь + салон):

```python
# app/domain/policies.py
def ensure_can_manage_salon(user: User, salon: Salon) -> None:
    if user.role != Role.SUPERADMIN and not salon.is_owned_by(user.id):
        raise PermissionDeniedError("You do not own this salon")
```

**Exceptions** — намеренно немного классов (`NotFoundError`, `PermissionDeniedError`, `ConflictError`, `InvalidCredentialsError`), а не по одному на каждую сущность (`SalonNotFoundError`, `StaffNotFoundError`...). Для API важна *категория* ошибки (404 vs 403 vs 400), а не то, какая именно сущность не найдена — это видно из текста сообщения.

### 2. `app/application/` — use cases, оркестровка

```
application/
  ports.py            PasswordHasher, TokenService — ещё два порта (не про данные, а про технические операции)
  use_cases/          RegisterUserUseCase, CreateSalonUseCase, BookAppointmentUseCase, ...
```

Use case — это один сценарий использования, один класс с методом `execute(...)`. Он принимает порты через конструктор и не знает, что за ними реально стоит:

```python
# app/application/use_cases/staff.py
class CreateStaffUseCase:
    def __init__(self, staff_repository: StaffRepository, salon_repository: SalonRepository) -> None:
        self._staff = staff_repository
        self._salons = salon_repository

    def execute(self, current_user: User, salon_id: int, name: str) -> Staff:
        ensure_role(current_user, Role.PARRUCCHIERE, Role.SUPERADMIN)

        salon = self._salons.get(salon_id)
        if salon is None:
            raise NotFoundError("Salon not found")
        ensure_can_manage_salon(current_user, salon)

        return self._staff.add(Staff(id=None, salon_id=salon_id, name=name))
```

Обратите внимание: **проверка прав — здесь**, не в роуте. Это ключевая мысль всего рефакторинга: `ensure_role` и `ensure_can_manage_salon` — часть бизнес-правила "кто может завести сотрудника", а не HTTP-обвязки. Можно вызвать этот use case из CLI-скрипта, из другого API, из тестов — правило сработает одинаково, без FastAPI.

### 3. `app/infrastructure/` — адаптеры, конкретные технологии

```
infrastructure/
  config.py                    Settings (pydantic-settings, читает .env)
  security.py                  BcryptPasswordHasher, JwtTokenService — реализуют application/ports.py
  db/
    models/                    SQLAlchemy ORM: UserModel, SalonModel, ... (persistence, НЕ domain-сущности)
    session.py                 engine, SessionLocal, get_db
  repositories/                SqlAlchemyUserRepository и т.д. — реализуют domain/repositories/*
```

Важно: **ORM-модель и domain-сущность — это два разных класса**, даже если поля совпадают. `UserModel` (SQLAlchemy) знает про таблицу `users`, колонки, `relationship`. `User` (domain) — просто dataclass. Репозиторий — это клей между ними:

```python
# app/infrastructure/repositories/salon_repository.py
class SqlAlchemySalonRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, salon: Salon) -> Salon:
        model = SalonModel(owner_id=salon.owner_id, name=salon.name, address=salon.address)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)   # ORM-модель -> domain-сущность

    @staticmethod
    def _to_entity(model: SalonModel) -> Salon:
        return Salon(id=model.id, owner_id=model.owner_id, name=model.name, address=model.address)
```

Да, для пяти сущностей это ощущается как дублирование (два похожих класса на каждую сущность). Это осознанная плата full-DDD подхода: entity никогда не "утекает" наружу как ORM-объект, привязанный к сессии SQLAlchemy — только чистые данные.

### 4. `app/api/` — presentation, тонкий слой сверху

```
api/
  deps.py               composition root: тут use case собирается из конкретных репозиториев/портов
  error_handlers.py     domain-исключение -> HTTP-статус
  v1/
    schemas/            Pydantic DTO для запросов/ответов (НЕ domain-сущности)
    endpoints/           роуты — только: взять юзера из токена, вызвать use case, сериализовать ответ
```

`deps.py` — самое важное файл с точки зрения "как это всё связано". Это единственное место, где `application` физически получает свои зависимости из `infrastructure`:

```python
# app/api/deps.py
def get_create_staff_use_case(db: Session = Depends(get_db)) -> CreateStaffUseCase:
    return CreateStaffUseCase(SqlAlchemyStaffRepository(db), SqlAlchemySalonRepository(db))
```

Эндпоинт после этого — тонкий и без бизнес-логики:

```python
# app/api/v1/endpoints/staff.py
@router.post("/", response_model=StaffRead, status_code=status.HTTP_201_CREATED)
def create_staff(
    staff_in: StaffCreate,
    current_user: User = Depends(get_current_user),
    use_case: CreateStaffUseCase = Depends(get_create_staff_use_case),
) -> StaffRead:
    staff = use_case.execute(current_user=current_user, salon_id=staff_in.salon_id, name=staff_in.name)
    return StaffRead.model_validate(staff)
```

Роут не проверяет права, не знает про 403 — если что-то не так, use case выбросит `PermissionDeniedError`, а `error_handlers.py` превратит это в HTTP-ответ:

```python
# app/api/error_handlers.py
@app.exception_handler(PermissionDeniedError)
async def handle_permission_denied(request: Request, exc: PermissionDeniedError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)})
```

Это регистрируется один раз в `main.py` (`register_exception_handlers(app)`) и работает для всех роутов сразу — не нужно писать `try/except` в каждом эндпоинте.

## Сквозной пример: `POST /api/v1/staff/`

Полный путь запроса "parrucchiere создаёт сотрудника в своём салоне", через все слои:

1. **api/endpoints/staff.py** — FastAPI парсит тело в `StaffCreate` (Pydantic DTO), `get_current_user` достаёт `User`-сущность из JWT (декодирует токен через `TokenService`, ищет пользователя через `UserRepository`).
2. **api/deps.py** — собирает `CreateStaffUseCase(SqlAlchemyStaffRepository(db), SqlAlchemySalonRepository(db))`.
3. **application/use_cases/staff.py** — `CreateStaffUseCase.execute(...)`:
   - `ensure_role(current_user, PARRUCCHIERE, SUPERADMIN)` — иначе `PermissionDeniedError`.
   - `salon_repository.get(salon_id)` — если `None`, `NotFoundError`.
   - `ensure_can_manage_salon(current_user, salon)` — если чужой салон и не superadmin, `PermissionDeniedError`.
   - Строит `Staff`-сущность (domain), отдаёт в `staff_repository.add(...)`.
4. **infrastructure/repositories/staff_repository.py** — `SqlAlchemyStaffRepository.add(...)` создаёт `StaffModel` (ORM), коммитит в Postgres, конвертирует обратно в domain `Staff` и возвращает.
5. Обратно в **api/endpoints/staff.py** — `StaffRead.model_validate(staff)` сериализует domain-сущность в JSON-ответ.

Если на шаге 3 вылетит `PermissionDeniedError` — она долетит до **api/error_handlers.py**, которое отдаст `403 {"detail": "You do not own this salon"}`. Ни один из промежуточных слоёв не знает про HTTP вообще (кроме `api/`).

## Как добавить новую фичу (шаблон)

Допустим, нужно добавить возможность парикмахеру отменять appointment. Порядок:

1. **domain**: если нужно новое правило — добавить в `policies.py` (например `ensure_can_cancel_appointment`). Если нужен новый метод у репозитория — добавить в `domain/repositories/appointment_repository.py` (Protocol).
2. **application**: новый use case `CancelAppointmentUseCase` в `application/use_cases/appointments.py`, использующий порт `AppointmentRepository` и правило из `policies.py`.
3. **infrastructure**: реализовать новый метод в `SqlAlchemyAppointmentRepository` (если добавляли метод в порт).
4. **api**: фабрика `get_cancel_appointment_use_case` в `deps.py`, роут `PATCH /appointments/{id}/cancel` в `endpoints/appointments.py`, который просто вызывает use case.

Бизнес-правило ("кто может отменить") тестируется юнит-тестом на `domain`/`application` без БД и без FastAPI — это и есть главная практическая выгода такой раскладки.

## Что упрощено осознанно (не абсолютная чистота)

Полный DDD может уйти очень глубоко (агрегаты, доменные события, value objects на каждое поле). Для проекта такого размера (5 сущностей) это было бы избыточно, поэтому:

- **Нет отдельных value objects** для email/цены/времени — это просто типы Python (`str`, `Decimal`, `datetime`) в полях entity. Если появятся собственные правила валидации (например, "цена не может быть отрицательной") — тогда есть смысл выделить `Money`/`Price`.
- **`Appointment.status`** — просто `str`, не enum. Сейчас нет ограничений на допустимые статусы ни в БД, ни в domain. Если появится бизнес-логика вокруг статусов (переходы confirmed → cancelled → completed) — стоит завести `AppointmentStatus` enum и правила переходов.
- **Аутентификация через JWT** (декодирование токена, `get_current_user`) сделана в `api/deps.py`, а не через domain-исключение — это чисто транспортный вопрос ("как HTTP-запрос идентифицирует пользователя"), а не бизнес-правило, поэтому она осталась в API-слое, а не в `domain/application`.
- **CLI-скрипт `create_superadmin`** намеренно работает через репозиторий напрямую, а не через `RegisterUserUseCase` — потому что этот use case намеренно запрещает регистрировать superadmin (это и есть бизнес-правило), а скрипту нужно его обойти. Это единственное место в проекте, где инфраструктурный код сознательно обходит domain-правило — и это видно прямо в коде скрипта, не спрятано.
