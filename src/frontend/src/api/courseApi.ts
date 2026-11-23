import type { Course, CourseQuery, Page } from '../types/course';
import type { HttpClient, QueryParams } from './http';

/** Інтерфейс доступу до каталогу. Сторінки залежать від нього, а не від HTTP. */
export interface CourseApi {
  list(query?: CourseQuery): Promise<Page<Course>>;
  get(id: number): Promise<Course>;
}

export class HttpCourseApi implements CourseApi {
  private readonly http: HttpClient;

  constructor(http: HttpClient) {
    this.http = http;
  }

  list(query: CourseQuery = {}): Promise<Page<Course>> {
    return this.http.get<Page<Course>>('/courses/', { ...query } as QueryParams);
  }

  get(id: number): Promise<Course> {
    return this.http.get<Course>(`/courses/${id}/`);
  }
}
