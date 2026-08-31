class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    budget_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    budget_max: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False,
        index=True,
    )

    deadline: Mapped[date | None] = mapped_column(
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

    client: Mapped["User"] = relationship(
        "User",
    )

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="jobs",
    )

    skills: Mapped[list["Skill"]] = relationship(
        "Skill",
        secondary=job_skills,
        back_populates="jobs",
    )