import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { ApiProvider } from '../api/ApiContext';
import type { CourseApi } from '../api/courseApi';
import { ApiError } from '../api/http';
import { I18nProvider } from '../i18n/I18nContext';
import { makeCourse } from '../test/fixtures';
import { CoursePage, parseCourseId } from './CoursePage';

function renderPage(api: CourseApi, path: string) {
  render(
    <I18nProvider>
      <ApiProvider api={api}>
        <MemoryRouter initialEntries={[path]}>
          <Routes>
            <Route path="/courses/:id" element={<CoursePage />} />
          </Routes>
        </MemoryRouter>
      </ApiProvider>
    </I18nProvider>,
  );
}

function makeApi(get: CourseApi['get']): CourseApi {
  return { list: async () => ({ count: 0, next: null, previous: null, results: [] }), get };
}

describe('parseCourseId', () => {
  it('приймає лише додатні цілі числа', () => {
    expect(parseCourseId('42')).toBe(42);
    for (const raw of ['abc', '0', '-1', '1.5', '1e3', '', ' 7', undefined]) {
      expect(parseCourseId(raw)).toBeNull();
    }
  });
});

describe('CoursePage', () => {
  it('показує курс і позначає посилання, що відкривається в новій вкладці', async () => {
    const get = vi.fn(async () => makeCourse({ id: 7 }));
    renderPage(makeApi(get), '/courses/7');

    expect(await screen.findByRole('heading', { name: 'Python для початківців' })).toBeInTheDocument();
    expect(get).toHaveBeenCalledWith(7);
    expect(
      screen.getByRole('link', { name: 'Перейти на платформу (відкривається в новій вкладці)' }),
    ).toHaveAttribute('target', '_blank');
  });

  it('показує сторінку "не знайдено" для некоректного ідентифікатора без запиту', () => {
    const get = vi.fn(async () => makeCourse());
    renderPage(makeApi(get), '/courses/abc');

    expect(screen.getByRole('heading', { name: 'Сторінку не знайдено' })).toBeInTheDocument();
    expect(get).not.toHaveBeenCalled();
  });

  it('показує сторінку "не знайдено", якщо API повернув 404', async () => {
    renderPage(
      makeApi(async () => {
        throw new ApiError(404, 'not found');
      }),
      '/courses/99',
    );

    expect(await screen.findByRole('heading', { name: 'Сторінку не знайдено' })).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('показує загальну помилку для інших збоїв', async () => {
    renderPage(
      makeApi(async () => {
        throw new ApiError(500, 'server error');
      }),
      '/courses/1',
    );

    expect(await screen.findByRole('alert')).toHaveTextContent('Не вдалося завантажити дані');
  });
});
