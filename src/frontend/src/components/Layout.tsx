import { Link, Outlet } from 'react-router-dom';
import { useI18n } from '../i18n/I18nContext';
import { LanguageSwitcher } from './LanguageSwitcher';

/** Спільна оболонка сторінок: шапка з навігацією та вміст маршруту. */
export function Layout() {
  const { t } = useI18n();
  return (
    <>
      <header className="site-header">
        <Link to="/" className="site-header__logo">
          {t('appName')}
        </Link>
        <nav>
          <Link to="/">{t('navCatalog')}</Link>
          <Link to="/login">{t('navLogin')}</Link>
          <LanguageSwitcher />
        </nav>
      </header>
      <main className="container">
        <Outlet />
      </main>
    </>
  );
}
