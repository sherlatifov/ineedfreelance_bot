from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest


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
        True  — сообщение успешно изменено.
        False — изменить сообщение не удалось.
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

    except TelegramBadRequest:
        return False


async def delete_message_safely(
    bot: Bot,
    chat_id: int,
    message_id: int,
) -> bool:
    """
    Безопасно удаляет сообщение.

    Если Telegram не позволяет удалить сообщение,
    просто возвращаем False вместо падения бота.
    """

    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )

        return True

    except TelegramBadRequest:
        return False