from typing import Optional

from pydantic import BaseModel


# ============================================================
# HEURES PRESTÉES
# ============================================================

class SafetyWorkHoursUpsert(BaseModel):
    organization_id: int
    year: int
    month: int
    workforce_category: str
    trade_id: Optional[int] = None
    worked_hours: float
    source: Optional[str] = None


# ============================================================
# OBJECTIFS CFE
# ============================================================

class SafetyTargetUpsert(BaseModel):
    organization_id: int
    year: int
    tf_target: Optional[float] = None
    tg_target: Optional[float] = None
    source: Optional[str] = None


# ============================================================
# INVALIDITÉ PERMANENTE
# ============================================================

class SafetyPermanentDisabilityCreate(BaseModel):
    organization_id: int
    year: int
    disability_percent: float
    source: Optional[str] = None