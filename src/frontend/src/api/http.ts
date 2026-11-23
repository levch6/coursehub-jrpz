/** Мінімальна абстракція HTTP-клієнта: решта коду не залежить від fetch напряму. */

export type QueryParams = Record<string, string | number | undefined>;

export interface HttpClient {
  get<T>(path: string, params?: QueryParams): Promise<T>;
}

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export class FetchHttpClient implements HttpClient {
  private readonly baseUrl: string;
  private readonly fetchImpl: typeof fetch;

  constructor(baseUrl = '/api', fetchImpl: typeof fetch = (...args) => fetch(...args)) {
    this.baseUrl = baseUrl;
    this.fetchImpl = fetchImpl;
  }

  async get<T>(path: string, params: QueryParams = {}): Promise<T> {
    const search = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== '') {
        search.set(key, String(value));
      }
    }
    const query = search.toString();
    const url = `${this.baseUrl}${path}${query ? `?${query}` : ''}`;
    const response = await this.fetchImpl(url, { headers: { Accept: 'application/json' } });
    if (!response.ok) {
      throw new ApiError(response.status, `Запит ${url} завершився зі статусом ${response.status}`);
    }
    return (await response.json()) as T;
  }
}
