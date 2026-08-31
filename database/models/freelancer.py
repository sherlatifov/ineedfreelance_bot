from .base import Base
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

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
    
    user: Mapped["User"] = relationship( 
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