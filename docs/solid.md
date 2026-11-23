# Принципи SOLID у коді

У таблиці наведено, де саме в репозиторії застосовано кожен принцип і чим це підтверджується.

## S: принцип єдиної відповідальності

Кожен клас або модуль має одну причину для змін.

| Клас або модуль | Єдина відповідальність |
|---|---|
| `collectors/dto.py`, `CourseDTO` | формат і перевірка запису про курс |
| `collectors/parsing.py` | розбір цін, рівнів і мов із сирих даних |
| `collectors/fetching.py`, `RequestsFetcher` | отримання JSON по HTTP |
| `apps/catalog/normalization.py` | нормалізація тексту та відбиток назви |
| `apps/catalog/repositories.py`, `DjangoCourseRepository` | збереження курсів у базі |
| `apps/collection/services.py`, `CollectionService` | запуск і облік одного збору даних |
| `apps/accounts/permissions.py`, `IsAdminRole` | перевірка ролі адміністратора |
| `src/frontend/src/api/http.ts` | виконання HTTP-запитів і обробка помилок |

## O: принцип відкритості та закритості

Нова платформа додається новим підкласом `PagedJsonCollector` і реєстрацією в реєстрі, без змін у
`CollectionService`, репозиторії чи API. Тест
`tests/collectors/test_registry.py::test_new_platform_needs_no_changes_in_existing_code`
реєструє нового збирача, не змінюючи наявного коду. Так само нова мова інтерфейсу додається
записом у `i18n/translations.ts`.

## L: принцип підстановки Лісков

Усі збирачі успадковують `CourseCollector` і повертають `CourseDTO`, тому будь-який із них можна
підставити замість іншого. Тест
`tests/collectors/test_collectors.py::test_every_registered_collector_honors_the_common_contract`
перевіряє цю властивість для кожної зареєстрованої платформи.

## I: принцип розділення інтерфейсів

Інтерфейси вузькі й описують лише те, що потрібно клієнту:

- `Fetcher` має єдиний метод `get_json`;
- `CourseSource` вимагає лише `platform` і `fetch()`;
- `SourceProvider` вимагає лише `names()` і `get()`;
- `CourseRecord` описує тільки поля, які потрібні каталогу;
- на фронтенді `CourseApi` містить лише `list` і `get`.

## D: принцип інверсії залежностей

Модулі вищого рівня залежать від абстракцій:

- `CollectionService` отримує `CourseRepository` та `SourceProvider` через конструктор і не знає
  ні про Django ORM, ні про конкретних збирачів;
- застосунок `collection` не імпортує пакет `collectors`: реєстр збирачів будується за шляхом
  `COLLECTION_SOURCES_FACTORY` із налаштувань, а в тестах підставляється підроблений;
- збирачі залежать від `Fetcher`, а не від бібліотеки `requests`;
- сторінки вебзастосунку працюють з `CourseApi` через контекст, а в тестах отримують підроблену
  реалізацію.

Усі тести перелічених модулів працюють без мережі та зовнішніх сервісів саме завдяки цим
абстракціям.
