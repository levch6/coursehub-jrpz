import { Link } from 'react-router-dom';
import { useI18n } from '../i18n/I18nContext';
import type { Course } from '../types/course';

interface CourseCardProps {
  course: Course;
}

/** Картка курсу у списку каталогу (ФВ-08). */
export function CourseCard({ course }: CourseCardProps) {
  const { t } = useI18n();
  const price = course.price === null || Number(course.price) === 0
    ? t('free')
    : `${course.price} ${course.currency}`;

  return (
    <article className="course-card">
      <h2>
        <Link to={`/courses/${course.id}`}>{course.title}</Link>
      </h2>
      <p className="course-card__meta">
        <span>{course.platform.name}</span>
        {course.rating !== null && (
          <span>
            <span aria-hidden="true">★</span>
            <span className="visually-hidden">{t('rating')}:</span> {course.rating}
          </span>
        )}
        <span>{price}</span>
      </p>
      {!course.is_available && <p className="course-card__warning">{t('unavailable')}</p>}
    </article>
  );
}
