# ========================================================
# RISKY — MODÈLE GÉNÉRIQUE ACTION
# ========================================================

from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ====================================================
    # ORIGINE
    # ====================================================

    origin_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    event_id: Mapped[int | None] = mapped_column(
        ForeignKey("events.id"),
        nullable=True,
        index=True,
    )

    # ====================================================
    # ACTION
    # ====================================================

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    action_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    scope: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    process_code: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    # ====================================================
    # PILOTAGE
    # ====================================================

    responsible_person_id: Mapped[int | None] = mapped_column(
        ForeignKey("people.id"),
        nullable=True,
    )

    responsible_text: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="MEDIUM",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="TODO",
    )

    progress_percent: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # ====================================================
    # RAPPORT / SUIVI
    # ====================================================

    resources: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    follow_up_indicator: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ====================================================
    # TRAÇABILITÉ
    # ====================================================

    created_by_person_id: Mapped[int | None] = mapped_column(
        ForeignKey("people.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )