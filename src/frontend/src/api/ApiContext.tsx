import { createContext, useContext } from 'react';
import type { ReactNode } from 'react';
import { HttpCourseApi } from './courseApi';
import type { CourseApi } from './courseApi';
import { FetchHttpClient } from './http';

const defaultApi: CourseApi = new HttpCourseApi(new FetchHttpClient());

const ApiContext = createContext<CourseApi>(defaultApi);

interface ApiProviderProps {
  api: CourseApi;
  children: ReactNode;
}

/** Дає змогу підставити іншу реалізацію API, наприклад підроблену в тестах. */
export function ApiProvider({ api, children }: ApiProviderProps) {
  return <ApiContext.Provider value={api}>{children}</ApiContext.Provider>;
}

export function useCourseApi(): CourseApi {
  return useContext(ApiContext);
}
