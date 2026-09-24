# ========================================================
# RISKY — SERVICE SAFETY FLASH CFE
# ========================================================

from backend.services.reports.accident_report import build_accident_report_preview
from backend.services.event_photos import get_event_photos


def _join_non_empty(values: list[str | None]) -> str:
    return "\n".join(value.strip() for value in values if value and value.strip())


def build_safety_flash_preview(db, event_id: int) -> dict:
    """Prépare un brouillon Safety Flash depuis le dossier, sans modifier le dossier."""
    report = build_accident_report_preview(db=db, event_id=event_id)
    event = report["event"]
    facts = report.get("facts") or {}
    actions = report.get("actions") or []

    facts_text = (
        facts.get("event_description")
        or facts.get("activity_before_event")
        or event.get("description")
        or ""
    )

    explanation_parts = [
        facts.get("direct_cause"),
        facts.get("third_party_details") if facts.get("caused_by_third_party") else None,
    ]

    recommendation_parts = [
        action.get("description")
        for action in actions
        if action.get("description")
    ]

    return {
        "event_id": event_id,
        "event_number": report["event_number"],
        "event_type": event.get("event_type"),
        "subject": event.get("description") or "",
        "facts": facts_text,
        "explanations": _join_non_empty(explanation_parts),
        "recommendations": _join_non_empty(recommendation_parts),
        "photos": flash_photos,
    }
