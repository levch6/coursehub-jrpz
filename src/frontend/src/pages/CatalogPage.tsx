import { useEffect, useState } from 'react';
import { useCourseApi } from '../api/ApiContext';
import { CourseCard } from '../components/CourseCard';
import { SearchBar } from '../components/SearchBar';
import { useI18n } from '../i18n/I18nContext';
import type { Course } from '../types/course';

type State =
  | { status: 'loading' }
  | { status: 'error' }
  | { status: 'ready'; courses: Course[] };

/** Каталог курсів із пошуком за ключовими словами (ФВ-08, ФВ-09). */
export function CatalogPage() {
  const api = useCourseApi();
  const { t } = useI18n();
  const [query, setQuery] = useState('');
  const [state, setState] = useState<State>({ status: 'loading' });

  useEffect(() => {
    let cancelled = false;
    setState({ status: 'loading' });
    api
      .list({ q: query })
      .then((page) => {
        if (!cancelled) setState({ status: 'ready', courses: page.results });
      })
      .catch(() => {
        if (!cancelled) setState({ status: 'error' });
      });
    return () => {
      cancelled = true;
    };
  }, [api, query]);

  return (
    <section>
      <SearchBar onSearch={setQuery} />
      {state.status === 'loading' && <p>{t('loading')}</p>}
      {state.status === 'error' && <p role="alert">{t('loadError')}</p>}
      {state.status === 'ready' && state.courses.length === 0 && <p>{t('empty')}</p>}
      {state.status === 'ready' && (
        <div className="course-list">
          {state.courses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      )}
    </section>
  );
}
