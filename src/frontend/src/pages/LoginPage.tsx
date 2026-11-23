import { useI18n } from '../i18n/I18nContext';

/** Заглушка сторінки входу (ФВ-15): повна реалізація буде в окремій задачі. */
export function LoginPage() {
  const { t } = useI18n();
  return (
    <section>
      <h1>{t('loginTitle')}</h1>
      <p>{t('loginStub')}</p>
    </section>
  );
}
