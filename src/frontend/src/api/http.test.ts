import { describe, expect, it, vi } from 'vitest';
import { ApiError, FetchHttpClient } from './http';

function mockFetch(body: unknown, status = 200) {
  return vi.fn(async () => new Response(JSON.stringify(body), { status }));
}

describe('FetchHttpClient', () => {
  it('додає лише непорожні параметри до адреси', async () => {
    const fetchMock = mockFetch({ ok: true });
    const client = new FetchHttpClient('/api', fetchMock as unknown as typeof fetch);

    await client.get('/courses/', { q: 'python', platform: undefined, page: 2, ordering: '' });

    expect(fetchMock).toHaveBeenCalledWith('/api/courses/?q=python&page=2', expect.anything());
  });

  it('повертає розібране тіло відповіді', async () => {
    const client = new FetchHttpClient('/api', mockFetch({ count: 3 }) as unknown as typeof fetch);
    await expect(client.get<{ count: number }>('/courses/')).resolves.toEqual({ count: 3 });
  });

  it('кидає ApiError для відповіді з помилкою', async () => {
    const client = new FetchHttpClient('/api', mockFetch({}, 404) as unknown as typeof fetch);
    await expect(client.get('/courses/99/')).rejects.toBeInstanceOf(ApiError);
  });
});
