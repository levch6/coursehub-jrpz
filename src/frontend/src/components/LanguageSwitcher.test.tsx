import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it } from 'vitest';
import { I18nProvider } from '../i18n/I18nContext';
import { LanguageSwitcher } from './LanguageSwitcher';

describe('LanguageSwitcher', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('має перекладений підпис і назви мов з атрибутом lang', async () => {
    render(
      <I18nProvider>
        <LanguageSwitcher />
      </I18nProvider>,
    );

    const select = screen.getByRole('combobox', { name: 'Мова інтерфейсу' });
    expect(screen.getByRole('option', { name: 'Українська' })).toHaveAttribute('lang', 'uk');
    expect(screen.getByRole('option', { name: 'English' })).toHaveAttribute('lang', 'en');

    await userEvent.selectOptions(select, 'en');
    expect(screen.getByRole('combobox', { name: 'Interface language' })).toHaveValue('en');
  });
});
