import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useCourseApi } from '../api/ApiContext';
import { useI18n } from '../i18n/I18nContext';
import type { Course } from '../types/course';

/** Сторінка курсу з переходом на платформу-джерело (ФВ-12). */
export function CoursePage() {
  const { id } = useParams();
  const api = useCourseApi();
  const { t } = useI18n();
  const [course, setCourse] = useState<Course | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setCourse(null);
    setFailed(false);
    api
      .get(Number(id))
      .then((data) => {
        if (!cancelled) setCourse(data);
      })
      .catch(() => {
        if (!cancelled) setFailed(true);
      });
    return () => {
      cancelled = true;
    };
  }, [api, id]);

  if (failed) return <p role="alert">{t('loadError')}</p>;
  if (!course) return <p>{t('loading')}</p>;

  return (
    <article>
      <Link to="/">{t('back')}</Link>
      <h1>{course.title}</h1>
      <p>{course.platform.name}</p>
      <p>{course.description}</p>
      {!course.is_available && <p>{t('unavailable')}</p>}
      <a href={course.url} target="_blank" rel="noopener noreferrer">
        {t('openOnPlatform')}
      </a>
    </article>
  );
}
