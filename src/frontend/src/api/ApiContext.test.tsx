import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { makeFakeApi } from '../test/fixtures';
import { ApiProvider, useCourseApi } from './ApiContext';

function Probe() {
  const api = useCourseApi();
  return <p>{typeof api.list}</p>;
}

describe('ApiContext', () => {
  it('віддає реалізацію API з ApiProvider', () => {
    render(
      <ApiProvider api={makeFakeApi([])}>
        <Probe />
      </ApiProvider>,
    );
    expect(screen.getByText('function')).toBeInTheDocument();
  });

  it('кидає зрозумілу помилку без ApiProvider', () => {
    // React логує помилку рендерингу в консоль: приглушуємо, щоб не засмічувати вивід
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
    expect(() => render(<Probe />)).toThrow('ApiProvider');
    spy.mockRestore();
  });
});
