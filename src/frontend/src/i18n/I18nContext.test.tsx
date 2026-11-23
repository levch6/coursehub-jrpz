import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it } from 'vitest';
import { I18nProvider, useI18n } from './I18nContext';
import { LOCALES, messages } from './translations';

function Probe() {
  const { t, setLocale } = useI18n();
  return (
    <>
      <p>{t('navCatalog')}</p>
      <button onClick={() => setLocale('en')}>en</button>
    </>
  );
}

describe('i18n', () => {
  beforeEach(() => {
    // вибрана мова зберігається між тестами: починаємо з мови за замовчуванням
    window.localStorage.clear();
  });

  it('має однаковий набір ключів для всіх мов', () => {
    const [first, ...rest] = LOCALES.map((locale) => Object.keys(messages[locale]).sort());
    for (const keys of rest) {
      expect(keys).toEqual(first);
    }
  });

  it('перемикає мову інтерфейсу', async () => {
    render(
      <I18nProvider>
        <Probe />
      </I18nProvider>,
    );
    expect(screen.getByText('Каталог')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'en' }));
    expect(screen.getByText('Catalog')).toBeInTheDocument();
  });

  it('синхронізує атрибут lang документа з мовою інтерфейсу', async () => {
    document.documentElement.lang = 'xx';
    render(
      <I18nProvider>
        <Probe />
      </I18nProvider>,
    );
    expect(document.documentElement.lang).toBe('uk');
    await userEvent.click(screen.getByRole('button', { name: 'en' }));
    expect(document.documentElement.lang).toBe('en');
  });
});
