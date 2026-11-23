/** Тексти інтерфейсу двома мовами (НФВ-15). */

export type Locale = 'uk' | 'en';

export const LOCALES: Locale[] = ['uk', 'en'];

const uk = {
  appName: 'CourseHub',
  navCatalog: 'Каталог',
  navLogin: 'Увійти',
  searchPlaceholder: 'Пошук курсів за ключовими словами',
  searchButton: 'Шукати',
  loading: 'Завантаження...',
  loadError: 'Не вдалося завантажити дані. Спробуйте пізніше.',
  empty: 'Курсів за вашим запитом не знайдено.',
  free: 'Безкоштовно',
  unavailable: 'Курс недоступний',
  openOnPlatform: 'Перейти на платформу',
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
  searchPlaceholder: 'Search courses by keywords',
  searchButton: 'Search',
  loading: 'Loading...',
  loadError: 'Failed to load data. Please try again later.',
  empty: 'No courses match your query.',
  free: 'Free',
  unavailable: 'Course unavailable',
  openOnPlatform: 'Open on platform',
  back: 'Back to catalog',
  notFoundTitle: 'Page not found',
  loginTitle: 'Sign in',
  loginStub: 'The sign-in form will be implemented in a separate task.',
};

export const messages: Record<Locale, Record<MessageKey, string>> = { uk, en };
