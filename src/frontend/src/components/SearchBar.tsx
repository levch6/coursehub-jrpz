import { useState } from 'react';
import type { FormEvent } from 'react';
import { useI18n } from '../i18n/I18nContext';

interface SearchBarProps {
  initialValue?: string;
  onSearch: (query: string) => void;
}

/** Рядок пошуку за ключовими словами (ФВ-09). */
export function SearchBar({ initialValue = '', onSearch }: SearchBarProps) {
  const { t } = useI18n();
  const [value, setValue] = useState(initialValue);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    onSearch(value.trim());
  };

  return (
    <form className="search-bar" role="search" onSubmit={submit}>
      <input
        type="search"
        value={value}
        placeholder={t('searchPlaceholder')}
        aria-label={t('searchPlaceholder')}
        onChange={(event) => setValue(event.target.value)}
      />
      <button type="submit">{t('searchButton')}</button>
    </form>
  );
}
