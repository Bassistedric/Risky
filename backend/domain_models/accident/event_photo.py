# ============================================================
# RISKY — MODÈLE PHOTOS ÉVÉNEMENT
# ============================================================

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ...database import Base


class EventPhoto(Base):
    __tablename__ = "event_photos"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
        index=True,
    )

    # --------------------------------------------------------
    # FICHIER
    # --------------------------------------------------------

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Chemin relatif au stockage RISKY.
    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # --------------------------------------------------------
    # DOSSIER / RAPPORT
    # --------------------------------------------------------

    caption: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # --------------------------------------------------------
    # TRAÇABILITÉ
    # --------------------------------------------------------

    uploaded_by_person_id: Mapped[int | None] = mapped_column(
        ForeignKey("people.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
    )