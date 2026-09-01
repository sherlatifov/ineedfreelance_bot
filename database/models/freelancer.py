from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


# TYPE_CHECKING нужен только для подсказок IDE и проверки типов.
#
# Во время обычного запуска Python этот импорт не выполняется.
# Это помогает избежать циклического импорта User <-> FreelancerProfile.
if TYPE_CHECKING:
    from .user import User


class FreelancerProfile(Base):
    """
    Профессиональный профиль фрилансера.

    Таблица:
        freelancer_profiles

    Один пользователь может иметь только один
    профиль фрилансера.
    """

    __tablename__ = "freelancer_profiles"

    # ---------------------------------------------------------
    # ID профиля
    # ---------------------------------------------------------

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # ---------------------------------------------------------
    # Связь с пользователем
    # ---------------------------------------------------------

    # user_id хранит ID пользователя из таблицы users.
    #
    # unique=True означает:
    # один User -> максимум один FreelancerProfile.
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    # SQLAlchemy relationship.
    #
    # Благодаря этому мы сможем обращаться:
    #
    # profile.user
    #
    # и получать связанного пользователя.
    user: Mapped["User"] = relationship(
        "User",
        back_populates="freelancer_profile",
    )

    # ---------------------------------------------------------
    # TITLE
    # ---------------------------------------------------------

    # Профессиональный заголовок фрилансера.
    #
    # Например:
    #
    # Python Backend Developer
    # Telegram Bot Developer
    # React Frontend Developer
    #
    # Пока ограничиваем длину 255 символами.
    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ---------------------------------------------------------
    # О СЕБЕ
    # ---------------------------------------------------------

    # Подробное описание фрилансера.
    #
    # Для него используем Text, потому что здесь
    # потенциально может быть большой текст.
    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ---------------------------------------------------------
    # НАВЫКИ
    # ---------------------------------------------------------

    # Пока оставляем навыки в существующем формате.
    #
    # Позже мы можем сделать отдельные таблицы:
    #
    # skills
    # freelancer_skills
    #
    # Но сейчас этого не трогаем.
    skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ---------------------------------------------------------
    # ПОЧАСОВАЯ СТАВКА
    # ---------------------------------------------------------

    # Сумма почасовой ставки.
    #
    # Например:
    #
    # 25
    #
    # Валюту добавим следующим отдельным этапом.
    hourly_rate: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # ---------------------------------------------------------
    # ОПЫТ
    # ---------------------------------------------------------

    # Например:
    #
    # Junior
    # Middle
    # Senior
    #
    # Пока оставляем String.
    experience: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )