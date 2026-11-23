import type { CourseApi } from '../api/courseApi';
import type { Course } from '../types/course';

export function makeCourse(overrides: Partial<Course> = {}): Course {
  return {
    id: 1,
    title: 'Python для початківців',
    description: 'Основи мови програмування',
    url: 'https://example.com/python',
    platform: { slug: 'udemy', name: 'Udemy', base_url: '' },
    category: null,
    price: '19.99',
    currency: 'USD',
    rating: '4.70',
    language: 'uk',
    level: 'beginner',
    is_available: true,
    updated_at: '2026-11-01T10:00:00Z',
    ...overrides,
  };
}

/** Підроблена реалізація API для тестів компонентів. */
export function makeFakeApi(courses: Course[]): CourseApi {
  return {
    list: async () => ({ count: courses.length, next: null, previous: null, results: courses }),
    get: async (id) => {
      const found = courses.find((course) => course.id === id);
      if (!found) throw new Error('not found');
      return found;
    },
  };
}
