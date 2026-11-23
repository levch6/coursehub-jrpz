/** Типи відповідей REST API серверної частини (див. src/backend/apps/catalog/serializers.py). */

export interface Platform {
  slug: string;
  name: string;
  base_url: string;
}

export interface Category {
  slug: string;
  name: string;
}

export interface Course {
  id: number;
  title: string;
  description: string;
  url: string;
  platform: Platform;
  category: Category | null;
  price: string | null;
  currency: string;
  rating: string | null;
  language: string;
  level: string;
  is_available: boolean;
  updated_at: string;
}

export interface Page<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/** Параметри пошуку, фільтрації та сортування (ФВ-09, ФВ-10, ФВ-11). */
export interface CourseQuery {
  q?: string;
  platform?: string;
  category?: string;
  max_price?: number;
  ordering?: string;
  page?: number;
}
