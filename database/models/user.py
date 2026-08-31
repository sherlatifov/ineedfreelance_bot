from .base import Base
from datetime import datetime
from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )

    username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Текущий режим пользователя:
    # freelancer / client
    role: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # Язык интерфейса:
    # ru / en
    language: Mapped[str] = mapped_column(
        String(2),
        default="ru",
        nullable=False,
    )

    is_blocked: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    blocked_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column( 
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False, 
    )
    
    is_admin: Mapped[bool] = mapped_column(
    default=False,
    nullable=False,
    )

    freelancer_profile: Mapped[ 
        "FreelancerProfile | None" 
        ] = relationship(
        "FreelancerProfile", 
        back_populates="user", 
        uselist=False, 
        cascade="all, delete-orphan", 
        )