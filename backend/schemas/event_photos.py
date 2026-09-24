# ============================================================
# RISKY — SCHÉMAS PHOTOS ÉVÉNEMENT
# ============================================================

from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ============================================================
# PHOTO — RÉPONSE
# ============================================================

class EventPhotoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int

    filename: str
    original_filename: str
    content_type: str
    file_size: int

    caption: str | None = None
    sort_order: int

    uploaded_by_person_id: int | None = None
    created_at: datetime


# ============================================================
# PHOTO — MODIFICATION
# ============================================================

class EventPhotoUpdate(BaseModel):
    caption: str | None = None
    sort_order: int | None = None


# ============================================================
# LISTE DES PHOTOS
# ============================================================

class EventPhotoListResponse(BaseModel):
    event_id: int
    photos: list[EventPhotoResponse]
    count: int
    max_photos: int = 4