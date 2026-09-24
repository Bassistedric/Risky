# ========================================================
# RISKY — SCHÉMAS ACTIONS
# ========================================================

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# ========================================================
# CRÉATION
# ========================================================

class ActionCreate(BaseModel):
    description: str = Field(min_length=1)

    action_type: str
    scope: str

    process_code: str | None = None

    responsible_person_id: int | None = None
    responsible_text: str | None = None

    due_date: date | None = None
    priority: str = "MEDIUM"

    progress_percent: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    resources: str | None = None
    follow_up_indicator: str | None = None


# ========================================================
# MODIFICATION
# ========================================================

class ActionUpdate(BaseModel):
    description: str | None = None

    action_type: str | None = None
    scope: str | None = None

    process_code: str | None = None

    responsible_person_id: int | None = None
    responsible_text: str | None = None

    due_date: date | None = None
    priority: str | None = None
    status: str | None = None

    progress_percent: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    resources: str | None = None
    follow_up_indicator: str | None = None


# ========================================================
# RÉPONSE
# ========================================================

class ActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    origin_type: str
    event_id: int | None

    description: str
    action_type: str
    scope: str
    process_code: str | None

    responsible_person_id: int | None
    responsible_text: str | None

    due_date: date | None
    priority: str
    status: str
    progress_percent: int | None

    resources: str | None
    follow_up_indicator: str | None

    created_by_person_id: int | None
    created_at: datetime
    updated_at: datetime


# ========================================================
# LISTE DES ACTIONS D'UN ÉVÉNEMENT
# ========================================================

class EventActionListResponse(BaseModel):
    event_id: int
    actions: list[ActionResponse]
    count: int

# ========================================================
# RÉPONSE TRANSVERSE
# ========================================================

class TransverseActionResponse(ActionResponse):
    origin_reference: str | None = None

# ========================================================
# LISTE TRANSVERSE DES ACTIONS
# ========================================================

class ActionListResponse(BaseModel):
    count: int
    actions: list[TransverseActionResponse]