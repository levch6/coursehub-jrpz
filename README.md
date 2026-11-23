# CourseHub

Вебсервіс-агрегатор онлайн-курсів: автоматично збирає публічні метадані курсів з платформ
Udemy, Coursera та edX, зберігає їх в єдиному каталозі та дає змогу шукати, фільтрувати й
порівнювати курси в одному місці.

Репозиторій створено в межах лабораторної роботи №4 «Розробка базової структури коду» з
дисципліни JRPZ. У ньому розміщено каркас системи за архітектурою з лабораторної роботи №2:
класи, модулі та функції з мінімальним функціоналом, тести, документацію та налаштування
командної роботи.

## Технології

| Шар | Технології |
|---|---|
| Серверна частина | Python 3.12, Django 5.2 LTS, Django REST Framework, JWT (simplejwt) |
| Фонові задачі | Celery, Celery Beat, Redis |
| База даних | PostgreSQL 16 (SQLite для тестів) |
| Вебзастосунок | React 19, TypeScript, Vite, React Router |
| Інфраструктура | Docker Compose, nginx, GitHub Actions, Google Cloud (розгортання) |
| Якість коду | pytest, Vitest, Ruff, TypeScript у строгому режимі |

## Структура репозиторію

```text
.
├── README.md                    опис проєкту (цей файл)
├── docker-compose.yml           запуск усього стеку: nginx, web, worker, beat, redis, postgres
├── pyproject.toml               налаштування Ruff і pytest
├── .env.example                 приклад змінних оточення
├── .github/
│   ├── workflows/ci.yml         перевірки: лінтер, тести, збірка
│   └── pull_request_template.md шаблон pull request
├── deploy/                      Dockerfile для серверної частини та nginx, конфігурація nginx
├── docs/                        документація (архітектура, структура, SOLID, робота з Git)
├── src/
│   ├── backend/                 серверна частина (Django)
│   │   ├── config/              налаштування, маршрути, Celery
│   │   ├── apps/
│   │   │   ├── accounts/        користувачі, реєстрація, JWT, ролі
│   │   │   ├── catalog/         моделі каталогу, репозиторій, пошук і фільтрація, REST API
│   │   │   ├── collection/      сценарій збору даних, журнал запусків, Celery-задачі
│   │   │   ├── administration/  кінцеві точки адміністратора: статистика, ручний запуск збору
│   │   │   └── favorites/       обране користувача
│   │   └── collectors/          збирачі платформ (чистий Python, без Django)
│   └── frontend/                вебзастосунок (React + TypeScript)
│       └── src/                 api, components, pages, i18n, types, test
└── tests/
    ├── backend/                 тести серверної частини (pytest)
    └── collectors/              тести збирачів (pytest)
```

Детальний опис модулів і напрямку залежностей наведено в [docs/structure.md](docs/structure.md).

## Команда та ролі

Ролі відповідають таблиці 5.1 специфікації вимог (лабораторна робота №1), а задачі беруться з
Scrum-дошки в Jira (проєкт CH).

| Учасник | Роль | Зона відповідальності в репозиторії | Гілка |
|---|---|---|---|
| Левченко Ренат | Керівник команди, бізнес-аналітик, інфраструктура | `deploy/`, `docker-compose.yml`, `.github/`, `docs/`, `README.md`, модуль адміністрування | `feature/CH-21-deploy-ci` |
| Максименко Роман | Бекенд-розробник | `src/backend/config`, `src/backend/apps`, `tests/backend` | `feature/CH-12-backend-core` |
| Ширинга Андрій | Фронтенд-розробник | `src/frontend` | `feature/CH-23-frontend-skeleton` |
| Міліщук Сергій | Розробник збирачів даних і тестувальник | `src/backend/collectors`, `tests/collectors` | `feature/CH-14-collectors-base` |

Внесок кожного учасника фіксується в історії комітів і pull request своєї гілки. Правила гілок і
рев'ю описано в [docs/git-workflow.md](docs/git-workflow.md).

## Запуск

### Усі сервіси в Docker

```bash
cp .env.example .env        # змініть DJANGO_SECRET_KEY і POSTGRES_PASSWORD
docker compose up --build
```

Застосунок буде доступний на `http://localhost`, перевірка серверної частини за адресою
`http://localhost/api/health/`.

### Локальна розробка без Docker

Серверна частина (потрібен Python 3.12; без змінних бази використовується SQLite):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r src/backend/requirements-dev.txt
cd src/backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver          # http://localhost:8000
```

Вебзастосунок (потрібен Node.js 22):

```bash
cd src/frontend
npm ci
npm run dev                          # http://localhost:5173, запити /api проксуються на :8000
```

## Тести та перевірки

```bash
ruff check .                         # лінтер Python (з кореня репозиторію)
pytest                               # тести серверної частини та збирачів (з кореня)
cd src/frontend && npm run typecheck && npm test && npm run build
```

Ті самі перевірки виконує CI при кожному pull request.

## Основні кінцеві точки API

| Метод і шлях | Призначення | Доступ |
|---|---|---|
| `GET /api/health/` | перевірка доступності | усі |
| `POST /api/auth/register/`, `POST /api/auth/token/` | реєстрація та вхід (JWT) | усі |
| `GET /api/courses/`, `GET /api/courses/{id}/` | каталог із пошуком `q`, фільтрами `platform`, `category`, `max_price`, `min_rating` і сортуванням `ordering` | усі |
| `GET /api/categories/` | категорії | усі |
| `GET /api/favorites/`, `POST /api/favorites/`, `DELETE /api/favorites/{id}/` | обране | авторизовані |
| `GET /api/admin/stats/`, `GET /api/admin/collection/runs/` | статистика й журнал збору | адміністратор |
| `POST /api/admin/collection/{platform}/run/` | ручний запуск збору | адміністратор |
| `PATCH /api/admin/courses/{id}/` | редагування й приховування курсу | адміністратор |

## Документація

- [docs/architecture.md](docs/architecture.md) - огляд архітектури та потоку даних;
- [docs/structure.md](docs/structure.md) - призначення модулів і правила залежностей;
- [docs/solid.md](docs/solid.md) - як у коді застосовано принципи SOLID;
- [docs/git-workflow.md](docs/git-workflow.md) - гілки, pull request, код-рев'ю.
