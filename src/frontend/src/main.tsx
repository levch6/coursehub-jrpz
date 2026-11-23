import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { App } from './App';
import { ApiProvider } from './api/ApiContext';
import { HttpCourseApi } from './api/courseApi';
import { FetchHttpClient } from './api/http';
import { I18nProvider } from './i18n/I18nContext';
import './styles.css';

const api = new HttpCourseApi(new FetchHttpClient());

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <I18nProvider>
      <ApiProvider api={api}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </ApiProvider>
    </I18nProvider>
  </StrictMode>,
);
