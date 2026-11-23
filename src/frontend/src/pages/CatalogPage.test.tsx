import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { ApiProvider } from '../api/ApiContext';
import type { CourseApi } from '../api/courseApi';
import { I18nProvider } from '../i18n/I18nContext';
import { makeCourse, makeFakeApi } from '../test/fixtures';
import { CatalogPage } from './CatalogPage';

function renderPage(api: CourseApi, initialEntries: string[] = ['/']) {
  render(
    <I18nProvider>
      <ApiProvider api={api}>
        <MemoryRouter initialEntries={initialEntries}>
          <Routes>
            <Route index element={<CatalogPage />} />
          </Routes>
          <LocationProbe />
        </MemoryRouter>
      </ApiProvider>
    </I18nProvider>,
  );
}

/** Показує поточний рядок запиту адреси, щоб перевіряти синхронізацію з URL. */
function LocationProbe() {
  const location = useLocation();
  return <p data-testid="location-search">{location.search}</p>;
}

function emptyPage() {
  return { count: 0, next: null, previous: null, results: [] };
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

  it('має заголовок першого рівня', async () => {
    renderPage(makeFakeApi([]));
    expect(screen.getByRole('heading', { level: 1, name: 'Каталог курсів' })).toBeInTheDocument();
    await screen.findByText('Курсів за вашим запитом не знайдено.');
  });

  it('оголошує стан завантаження та порожній результат через role="status"', async () => {
    renderPage(makeFakeApi([]));
    expect(screen.getByRole('status')).toHaveTextContent('Завантаження...');
    await waitFor(() =>
      expect(screen.getByRole('status')).toHaveTextContent('Курсів за вашим запитом не знайдено.'),
    );
    expect(document.querySelector('.course-list')).toBeNull();
  });

  it('зберігає пошуковий запит в адресі', async () => {
    renderPage({ list: vi.fn(async () => emptyPage()), get: async () => makeCourse() });
    await screen.findByText('Курсів за вашим запитом не знайдено.');

    await userEvent.type(screen.getByRole('searchbox'), 'python');
    await userEvent.click(screen.getByRole('button', { name: 'Шукати' }));

    expect(screen.getByTestId('location-search')).toHaveTextContent('?q=python');
  });

  it('бере запит з адреси та підставляє його в поле пошуку', async () => {
    const list = vi.fn(async () => emptyPage());
    renderPage({ list, get: async () => makeCourse() }, ['/?q=django']);
    await screen.findByText('Курсів за вашим запитом не знайдено.');

    expect(list).toHaveBeenCalledWith({ q: 'django' });
    expect(screen.getByRole('searchbox')).toHaveValue('django');
  });

  it('повторює той самий запит після помилки', async () => {
    const list = vi
      .fn<CourseApi['list']>()
      .mockRejectedValueOnce(new Error('network'))
      .mockResolvedValueOnce({ ...emptyPage(), count: 1, results: [makeCourse()] });
    renderPage({ list, get: async () => makeCourse() }, ['/?q=python']);

    await screen.findByRole('alert');
    await userEvent.click(screen.getByRole('button', { name: 'Спробувати знову' }));

    expect(await screen.findByText('Python для початківців')).toBeInTheDocument();
    expect(list).toHaveBeenCalledTimes(2);
    expect(list).toHaveBeenLastCalledWith({ q: 'python' });
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('повторний пошук з тим самим запитом теж перезапускає завантаження', async () => {
    const list = vi
      .fn<CourseApi['list']>()
      .mockRejectedValueOnce(new Error('network'))
      .mockResolvedValue(emptyPage());
    renderPage({ list, get: async () => makeCourse() }, ['/?q=python']);

    await screen.findByRole('alert');
    await userEvent.click(screen.getByRole('button', { name: 'Шукати' }));

    expect(await screen.findByText('Курсів за вашим запитом не знайдено.')).toBeInTheDocument();
    expect(list).toHaveBeenCalledTimes(2);
  });
});
