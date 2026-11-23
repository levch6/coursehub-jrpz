import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { I18nProvider } from '../i18n/I18nContext';
import { makeCourse } from '../test/fixtures';
import { CourseCard } from './CourseCard';

function renderCard(course = makeCourse()) {
  render(
    <I18nProvider>
      <MemoryRouter>
        <CourseCard course={course} />
      </MemoryRouter>
    </I18nProvider>,
  );
}

describe('CourseCard', () => {
  it('показує назву, платформу та ціну', () => {
    renderCard();
    expect(screen.getByRole('link', { name: 'Python для початківців' })).toHaveAttribute(
      'href',
      '/courses/1',
    );
    expect(screen.getByText('Udemy')).toBeInTheDocument();
    expect(screen.getByText('19.99 USD')).toBeInTheDocument();
  });

  it('позначає безкоштовні курси', () => {
    renderCard(makeCourse({ price: null }));
    expect(screen.getByText('Безкоштовно')).toBeInTheDocument();
  });

  it('попереджає про недоступний курс', () => {
    renderCard(makeCourse({ is_available: false }));
    expect(screen.getByText('Курс недоступний')).toBeInTheDocument();
  });
});
