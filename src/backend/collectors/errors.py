"""Помилки пакета збирачів."""


class CollectorError(Exception):
    """Базова помилка збирача."""


class FetchError(CollectorError):
    """Не вдалося отримати дані з джерела (мережа, код відповіді, формат)."""


class ParseError(CollectorError):
    """Отримані дані не відповідають очікуваній структурі."""


class UnknownPlatformError(CollectorError, KeyError):
    """У реєстрі немає збирача для вказаної платформи."""
