import { useI18n } from '../i18n/I18nContext';
import { LOCALES } from '../i18n/translations';
import type { Locale } from '../i18n/translations';

/** Перемикач мови інтерфейсу (НФВ-15). */
export function LanguageSwitcher() {
  const { locale, setLocale } = useI18n();
  return (
    <select
      aria-label="Language"
      value={locale}
      onChange={(event) => setLocale(event.target.value as Locale)}
    >
      {LOCALES.map((item) => (
        <option key={item} value={item}>
          {item.toUpperCase()}
        </option>
      ))}
    </select>
  );
}
