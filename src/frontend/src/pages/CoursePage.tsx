import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useCourseApi } from '../api/ApiContext';
import { ApiError } from '../api/http';
import { useI18n } from '../i18n/I18nContext';
import type { Course } from '../types/course';
import { NotFoundPage } from './NotFoundPage';

type State =
  | { status: 'loading' }
  | { status: 'not-found' }
  | { status: 'error' }
  | { status: 'ready'; course: Course };

/** Перетворює параметр маршруту на ідентифікатор курсу або null, якщо він некоректний. */
export function parseCourseId(raw: string | undefined): number | null {
  if (raw === undefined || !/^\d+$/.test(raw)) return null;
  const id = Number(raw);
  return Number.isInteger(id) && id > 0 ? id : null;
}

/** Сторінка курсу з переходом на платформу-джерело (ФВ-12). */
export function CoursePage() {
  const { id: rawId } = useParams();
  const id = parseCourseId(rawId);
  const api = useCourseApi();
  const { t } = useI18n();
  const [state, setState] = useState<State>({ status: 'loading' });

  useEffect(() => {
    // некоректний ідентифікатор не надсилаємо на сервер
    if (id === null) return;
    let cancelled = false;
    setState({ status: 'loading' });
    api
      .get(id)
      .then((course) => {
        if (!cancelled) setState({ status: 'ready', course });
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        const notFound = error instanceof ApiError && error.status === 404;
        setState({ status: notFound ? 'not-found' : 'error' });
      });
    return () => {
      cancelled = true;
    };
  }, [api, id]);

  if (id === null || state.status === 'not-found') return <NotFoundPage />;
  if (state.status === 'error') return <p role="alert">{t('loadError')}</p>;
  if (state.status === 'loading') {
    return (
      <p role="status" aria-live="polite">
        {t('loading')}
      </p>
    );
  }

  const { course } = state;
  return (
    <article>
      <Link to="/">{t('back')}</Link>
      <h1>{course.title}</h1>
      <p>{course.platform.name}</p>
      <p>{course.description}</p>
      {!course.is_available && <p>{t('unavailable')}</p>}
      <a href={course.url} target="_blank" rel="noopener noreferrer">
        {t('openOnPlatform')}{' '}
        <span className="visually-hidden">{t('opensInNewTab')}</span>
      </a>
    </article>
  );
}
