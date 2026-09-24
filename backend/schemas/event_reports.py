# ========================================================
# RISKY — SCHÉMAS RAPPORTS ÉVÉNEMENT
# ========================================================

from typing import Any

from pydantic import BaseModel


class EventReportPreviewResponse(BaseModel):
    event_id: int
    event_number: str

    event: dict[str, Any]
    facts: dict[str, Any] | None
    classification: dict[str, Any] | None
    circumstantial_report: dict[str, Any] | None = None

    heepo: list[dict[str, Any]]
    photos: list[dict[str, Any]]

    cause_tree: dict[str, Any] | None
    just_culture: dict[str, Any] | None

    actions: list[dict[str, Any]]

    sections: dict[str, bool]