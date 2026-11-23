import { Link } from 'react-router-dom';
import { useI18n } from '../i18n/I18nContext';

export function NotFoundPage() {
  const { t } = useI18n();
  return (
    <section>
      <h1>{t('notFoundTitle')}</h1>
      <Link to="/">{t('back')}</Link>
    </section>
  );
}
