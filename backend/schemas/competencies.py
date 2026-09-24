from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

class PersonCompetencyCreate(BaseModel):
    competency_id: int
    obtained_at: Optional[datetime] = None
    provider: Optional[str] = None
    certificate_reference: Optional[str] = None
    document_path: Optional[str] = None
    comment: Optional[str] = None

class PersonCompetencyStatusUpdate(BaseModel):
    status: str
    comment: Optional[str] = None