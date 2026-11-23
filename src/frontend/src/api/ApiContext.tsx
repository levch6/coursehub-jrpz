import { createContext, useContext } from 'react';
import type { ReactNode } from 'react';
import type { CourseApi } from './courseApi';

const ApiContext = createContext<CourseApi | null>(null);

interface ApiProviderProps {
  api: CourseApi;
  children: ReactNode;
}

/** Надає реалізацію API сторінкам: справжню в main.tsx, підроблену в тестах. */
export function ApiProvider({ api, children }: ApiProviderProps) {
  return <ApiContext.Provider value={api}>{children}</ApiContext.Provider>;
}

export function useCourseApi(): CourseApi {
  const api = useContext(ApiContext);
  if (!api) {
    throw new Error('useCourseApi має використовуватися всередині ApiProvider');
  }
  return api;
}
