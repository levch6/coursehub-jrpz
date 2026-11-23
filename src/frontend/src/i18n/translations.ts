/** Тексти інтерфейсу двома мовами (НФВ-15). */

export type Locale = 'uk' | 'en';

export const LOCALES: Locale[] = ['uk', 'en'];

/** Назви мов їхньою власною мовою: однакові незалежно від поточної мови інтерфейсу. */
export const LOCALE_NAMES: Record<Locale, string> = {
  uk: 'Українська',
  en: 'English',
};

const uk = {
  appName: 'CourseHub',
  navCatalog: 'Каталог',
  navLogin: 'Увійти',
  languageLabel: 'Мова інтерфейсу',
  catalogTitle: 'Каталог курсів',
  searchPlaceholder: 'Пошук курсів за ключовими словами',
  searchButton: 'Шукати',
  loading: 'Завантаження...',
  loadError: 'Не вдалося завантажити дані. Спробуйте пізніше.',
  retry: 'Спробувати знову',
  empty: 'Курсів за вашим запитом не знайдено.',
  free: 'Безкоштовно',
  rating: 'Рейтинг',
  unavailable: 'Курс недоступний',
  openOnPlatform: 'Перейти на платформу',
  opensInNewTab: '(відкривається в новій вкладці)',
  back: 'Назад до каталогу',
  notFoundTitle: 'Сторінку не знайдено',
  loginTitle: 'Вхід',
  loginStub: 'Форма входу буде реалізована в окремій задачі.',
} as const;

export type MessageKey = keyof typeof uk;

const en: Record<MessageKey, string> = {
  appName: 'CourseHub',
  navCatalog: 'Catalog',
  navLogin: 'Sign in',
  languageLabel: 'Interface language',
  catalogTitle: 'Course catalog',
  searchPlaceholder: 'Search courses by keywords',
  searchButton: 'Search',
  loading: 'Loading...',
  loadError: 'Failed to load data. Please try again later.',
  retry: 'Try again',
  empty: 'No courses match your query.',
  free: 'Free',
  rating: 'Rating',
  unavailable: 'Course unavailable',
  openOnPlatform: 'Open on platform',
  opensInNewTab: '(opens in a new tab)',
  back: 'Back to catalog',
  notFoundTitle: 'Page not found',
  loginTitle: 'Sign in',
  loginStub: 'The sign-in form will be implemented in a separate task.',
};

export const messages: Record<Locale, Record<MessageKey, string>> = { uk, en };
