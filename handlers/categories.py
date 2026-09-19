from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.repositories.category import get_category


router = Router()


@router.callback_query(F.data.startswith("category:"))
async def category_selected(callback: CallbackQuery):

    category_id = int(
        callback.data.split(":")[1]
    )

    category = await get_category(category_id)

    if not category:
        await callback.answer(
            "Категория не найдена",
            show_alert=True
        )
        return

    await callback.answer()

    await callback.message.edit_text(
        f"Выбрана категория:\n\n"
        f"📂 {category.name_ru}"
    )