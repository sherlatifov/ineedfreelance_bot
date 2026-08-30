from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, ForeignKey, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


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

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
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

# Freelance Profile

class FreelancerProfile(Base): 
    __tablename__ = "freelancer_profiles" 

    id: Mapped[int] = mapped_column(
        primary_key=True, 
        autoincrement=True, 
    ) 
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey( "users.id", ondelete="CASCADE", ), 
        unique=True, 
        nullable=False, 
        index=True, 
    ) 
    
    user: Mapped[User] = relationship( 
        "User", 
        back_populates="freelancer_profile", 
    ) 
    
    title: Mapped[str | None] = mapped_column( 
        String(255), 
        nullable=True, 
    )  
    
    bio: Mapped[str | None] = mapped_column( 
        Text, 
        nullable=True, 
    )
    
    skills: Mapped[str | None] = mapped_column( 
        Text, 
        nullable=True, 
    )
    
    hourly_rate: Mapped[int | None] = mapped_column( 
        Integer, 
        nullable=True, 
    )
    
    experience: Mapped[str | None] = mapped_column( 
        String(100), 
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