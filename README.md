## Справочник организаций — REST API (FastAPI)

Приложение для работы со справочником Организаций, Зданий и Видов деятельности. 
Стэк: FastAPI + Pydantic + SQLAlchemy + Alembic. Деятельности образуют дерево вложенности до 3 уровней.

### Возможности
- Получение списка организаций в конкретном здании
- Получение списка организаций по виду деятельности (включая дочерние до 3 уровней)
- Поиск организаций: по названию, по зданию, по виду деятельности, по гео (радиус/прямоугольник)
- Получение организации по идентификатору
- Списки зданий и деятельностей
- Авторизация по статическому API ключу в заголовке `X-API-KEY`

### Требования
- Python 3.11+
- Docker и Docker Compose (для контейнерного запуска)
- PostgreSQL 15 (локально — опционально, если запускаете через Docker Compose, БД поднимется автоматически)

### Структура проекта (основное)
```
app/
  api/routers/ (роуты FastAPI)
  core/config.py (настройки и переменные окружения)
  db/session.py (движок БД и Base)
  models/ (SQLAlchemy модели)
  schemas/ (Pydantic-схемы)
  main.py (инициализация FastAPI)
  seed.py (заполнение тестовыми данными)
alembic/ (настройки миграций)
alembic.ini
docker-compose.yml
Dockerfile
requirements.txt
```

### Переменные окружения
- `API_KEY` — статический ключ для доступа к API (по умолчанию `secret-key`)
- `DATABASE_URL` — строка подключения SQLAlchemy, по умолчанию (в контейнере):
  `postgresql+psycopg2://postgres:postgres@db:5432/secunda_orgs`

### Запуск в Docker
```bash
docker-compose up --build
```

После запуска:
- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`
- Health-check: `http://localhost:8000/health`

Все запросы требуют заголовок авторизации:
```
X-API-KEY: secret-key
```

Наполнить БД тестовыми данными (если нужно вручную):
```bash
docker-compose run --rm web python -m app.seed
```

### Локальный запуск (без Docker)
1) Подготовить окружение и зависимости
```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
```
2) Настроить переменные окружения (Windows PowerShell пример)
```bash
$env:API_KEY = "secret-key"
$env:DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/secunda_orgs"
```
3) Применить миграции и/или выполнить сидинг (опционально)
```bash
alembic upgrade head
python -m app.seed
```
4) Запустить сервер разработки
```bash
uvicorn app.main:app --reload
```

### Миграции Alembic
- Сгенерировать новую миграцию после изменения моделей:
```bash
alembic revision --autogenerate -m "message"
alembic upgrade head
```

### Модели данных (кратко)
- Здание (`Building`): `address`, `latitude`, `longitude`
- Деятельность (`Activity`): `name`, `parent_id` (дерево до 3 уровней)
- Организация (`Organization`): `name`, `building_id`, связи many-to-many с `Activity`, телефоны (`Phone`)

### Эндпоинты (основные)
Базовый префикс: `/api/v1`

- Организации:
  - `GET /organizations/{id}` — организация по ID
  - `GET /organizations/by-building/{building_id}` — список в конкретном здании
  - `GET /organizations/by-activity/{activity_id}` — список по виду деятельности и его потомкам (≤3 уровня)
  - `GET /organizations/search` — поиск с фильтрами:
    - `name` — подстрочный поиск по названию
    - `building_id` — фильтр по зданию
    - `activity_id` или `activity_name` — вид деятельности с учетом потомков (≤3 уровня)
    - Геопоиск:
      - Радиус: `lat`, `lon`, `radius_km`
      - Прямоугольник: `min_lat`, `max_lat`, `min_lon`, `max_lon`
    - Пагинация: `skip`, `limit`

- Здания:
  - `GET /buildings/` — список зданий

- Деятельности:
  - `GET /activities/` — список деятельностей
  - `GET /activities/{activity_id}` — деятельность по ID

### Примеры запросов (curl)
Получить организации по деятельности «Еда» (по имени, включая потомков):
```bash
curl -H "X-API-KEY: secret-key" "http://localhost:8000/api/v1/organizations/search?activity_name=%D0%95%D0%B4%D0%B0"
```

Поиск по названию (подстрока):
```bash
curl -H "X-API-KEY: secret-key" "http://localhost:8000/api/v1/organizations/search?name=%D0%9E%D0%9E%D0%9E"
```

Геопоиск по радиусу 2 км от точки (lat=55.7558, lon=37.6176):
```bash
curl -H "X-API-KEY: secret-key" "http://localhost:8000/api/v1/organizations/search?lat=55.7558&lon=37.6176&radius_km=2"
```

Геопоиск по прямоугольнику:
```bash
curl -H "X-API-KEY: secret-key" "http://localhost:8000/api/v1/organizations/search?min_lat=55.70&max_lat=55.80&min_lon=37.55&max_lon=37.65"
```

Организация по ID:
```bash
curl -H "X-API-KEY: secret-key" "http://localhost:8000/api/v1/organizations/1"
```

### Swagger / Документация
- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`

### Замечания по геопоиску
Текущая реализация использует приближение через ограничивающий прямоугольник для радиуса (1° широты ≈ 111 км, долготы — с учетом cos(lat)). Для боевого использования можно заменить на PostGIS или точную реализацию Haversine/Great-circle с индексами.



