import { useI18n } from '../i18n/I18nContext';
import { LOCALE_NAMES, LOCALES } from '../i18n/translations';
import type { Locale } from '../i18n/translations';

/** Перемикач мови інтерфейсу (НФВ-15). */
export function LanguageSwitcher() {
  const { locale, setLocale, t } = useI18n();
  return (
    <select
      aria-label={t('languageLabel')}
      value={locale}
      onChange={(event) => setLocale(event.target.value as Locale)}
    >
      {LOCALES.map((item) => (
        <option key={item} value={item} lang={item}>
          {LOCALE_NAMES[item]}
        </option>
      ))}
    </select>
  );
}
