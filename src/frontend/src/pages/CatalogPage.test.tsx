import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { ApiProvider } from '../api/ApiContext';
import type { CourseApi } from '../api/courseApi';
import { I18nProvider } from '../i18n/I18nContext';
import { makeCourse, makeFakeApi } from '../test/fixtures';
import { CatalogPage } from './CatalogPage';

function renderPage(api: CourseApi) {
  render(
    <I18nProvider>
      <ApiProvider api={api}>
        <MemoryRouter>
          <CatalogPage />
        </MemoryRouter>
      </ApiProvider>
    </I18nProvider>,
  );
}

describe('CatalogPage', () => {
  it('показує курси, отримані з API', async () => {
    renderPage(makeFakeApi([makeCourse(), makeCourse({ id: 2, title: 'Django' })]));
    expect(await screen.findByText('Django')).toBeInTheDocument();
    expect(screen.getByText('Python для початківців')).toBeInTheDocument();
  });

  it('показує повідомлення, якщо курсів немає', async () => {
    renderPage(makeFakeApi([]));
    expect(await screen.findByText('Курсів за вашим запитом не знайдено.')).toBeInTheDocument();
  });

  it('показує помилку, якщо API недоступний', async () => {
    const api: CourseApi = {
      list: async () => {
        throw new Error('network');
      },
      get: async () => {
        throw new Error('network');
      },
    };
    renderPage(api);
    expect(await screen.findByRole('alert')).toHaveTextContent('Не вдалося завантажити дані');
  });

  it('передає пошуковий запит в API', async () => {
    const list = vi.fn(async () => ({ count: 0, next: null, previous: null, results: [] }));
    renderPage({ list, get: async () => makeCourse() });
    await screen.findByText('Курсів за вашим запитом не знайдено.');

    await userEvent.type(screen.getByRole('searchbox'), 'python');
    await userEvent.click(screen.getByRole('button', { name: 'Шукати' }));

    expect(list).toHaveBeenLastCalledWith({ q: 'python' });
  });
});
