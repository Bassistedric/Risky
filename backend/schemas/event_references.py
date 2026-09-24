from typing import Optional

from pydantic import BaseModel


class EventCodeImportItem(BaseModel):
    code: str
    label: str


class EventCodeImportPreview(BaseModel):
    category: str
    source: Optional[str] = None
    source_version: Optional[str] = None
    items: list[EventCodeImportItem]