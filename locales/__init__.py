from locales import ru, en


SUPPORTED_LANGUAGES = {
    "ru": ru.TEXTS,
    "en": en.TEXTS,
}


def get_language(language_code: str | None) -> str:
    """
    Определяет поддерживаемый язык Telegram.

    ru     -> ru
    ru-RU  -> ru
    en     -> en
    en-US  -> en

    Неизвестный язык -> ru
    """

    if not language_code:
        return "ru"

    language = language_code.lower().split("-")[0]

    if language in SUPPORTED_LANGUAGES:
        return language

    return "ru"


def t(language: str, key: str) -> str:
    """
    Возвращает перевод.
    """

    texts = SUPPORTED_LANGUAGES.get(
        language,
        SUPPORTED_LANGUAGES["ru"],
    )

    return texts.get(
        key,
        SUPPORTED_LANGUAGES["ru"].get(key, key),
    )
