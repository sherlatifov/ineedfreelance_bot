from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
import logging


logger = logging.getLogger(__name__)


async def edit_message_safely(
    bot: Bot,
    chat_id: int,
    message_id: int,
    text: str,
    reply_markup=None,
) -> bool:
    """
    Безопасно редактирует сообщение бота.

    Возвращает:

        True
        если сообщение успешно изменено.

        False
        если Telegram не позволил изменить сообщение.

    Важно:
    ошибку не скрываем полностью.
    Записываем её в лог, чтобы при проблеме
    мы точно знали, что произошло.
    """

    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )

        return True

    except TelegramBadRequest as error:

        logger.error(
            "Не удалось изменить сообщение Telegram. "
            "chat_id=%s message_id=%s error=%s",
            chat_id,
            message_id,
            error,
        )

        return False


async def delete_message_safely(
    bot: Bot,
    chat_id: int,
    message_id: int,
) -> bool:
    """
    Безопасно удаляет сообщение пользователя.

    Если Telegram не позволяет удалить сообщение,
    ошибка записывается в лог.

    Возвращаем:

        True  — удаление успешно.
        False — удалить не удалось.
    """

    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )

        return True

    except TelegramBadRequest as error:

        logger.warning(
            "Не удалось удалить сообщение. "
            "chat_id=%s message_id=%s error=%s",
            chat_id,
            message_id,
            error,
        )

        return False