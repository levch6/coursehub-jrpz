import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
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
  // запит зберігається в адресі, щоб не губитися при переході «Назад»
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get('q') ?? '';
  // лічильник повторних спроб: зміна значення перезапускає завантаження з тим самим запитом
  const [attempt, setAttempt] = useState(0);
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
  }, [api, query, attempt]);

  const retry = () => setAttempt((value) => value + 1);

  const search = (next: string) => {
    if (next === query) {
      retry();
    } else {
      setSearchParams(next ? { q: next } : {});
    }
  };

  return (
    <section>
      <h1 className="visually-hidden">{t('catalogTitle')}</h1>
      {/* key оновлює поле пошуку, коли запит змінюється через історію браузера */}
      <SearchBar key={query} initialValue={query} onSearch={search} />
      {state.status === 'loading' && (
        <p role="status" aria-live="polite">
          {t('loading')}
        </p>
      )}
      {state.status === 'error' && (
        <div>
          <p role="alert">{t('loadError')}</p>
          <button type="button" onClick={retry}>
            {t('retry')}
          </button>
        </div>
      )}
      {state.status === 'ready' && state.courses.length === 0 && (
        <p role="status" aria-live="polite">
          {t('empty')}
        </p>
      )}
      {state.status === 'ready' && state.courses.length > 0 && (
        <div className="course-list">
          {state.courses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      )}
    </section>
  );
}
