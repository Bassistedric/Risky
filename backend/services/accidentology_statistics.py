from __future__ import annotations

from collections import Counter
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..domain_models.actions.action import Action
from .safety_statistics import (
    get_organization_trade_code,
    resolve_event_scope,
)


def _counter_rows(counter: Counter) -> list[dict]:
    total = sum(counter.values())
    return [
        {
            "code": code,
            "label": label,
            "count": count,
            "percent": (count * 100 / total) if total else 0,
        }
        for (code, label), count in counter.most_common()
    ]




def _translated_label(obj, language: str | None, fallback: str | None) -> str:
    lang = (language or "fr").split("-")[0].lower()
    if lang in {"nl", "en", "pl"}:
        value = getattr(obj, f"label_{lang}", None)
        if value:
            return value
    return getattr(obj, "label", None) or fallback or ""


def _just_culture_label(db: Session, row, language: str | None) -> str:
    node = db.scalar(select(models.JustCultureNode).where(models.JustCultureNode.conclusion_code == row.conclusion_code, models.JustCultureNode.node_type == "CONCLUSION").limit(1))
    if node:
        lang = (language or "fr").split("-")[0].lower()
        if lang in {"nl", "en", "pl"}:
            value = getattr(node, f"conclusion_label_{lang}", None)
            if value:
                return value
        if node.conclusion_label:
            return node.conclusion_label
    return row.conclusion_label or row.conclusion_code


def build_accidentology_summary(
    db: Session,
    *,
    organization_id: int,
    year: int,
    month_to: int,
    trade_code: str | None = None,
    language: str = "fr",
) -> dict:
    if month_to < 1 or month_to > 12:
        raise ValueError("Mois invalide")

    organization = db.get(models.Organization, organization_id)
    if not organization:
        raise ValueError("Organisation introuvable")

    effective_trade = trade_code or get_organization_trade_code(
        db, organization_id
    )
    scope_ids = resolve_event_scope(
        db,
        organization_id=organization_id,
        trade_code=effective_trade,
    )

    if not scope_ids:
        events = []
    else:
        end = (
            datetime(year + 1, 1, 1)
            if month_to == 12
            else datetime(year, month_to + 1, 1)
        )
        events = list(
            db.scalars(
                select(models.Event).where(
                    models.Event.organization_id.in_(scope_ids),
                    models.Event.event_date >= datetime(year, 1, 1),
                    models.Event.event_date < end,
                )
            ).all()
        )

    event_ids = [event.id for event in events]
    event_count = len(events)
    normal_event_ids = {
        event.id for event in events
        if (event.analysis_type or "").upper() in {"NORMAL", "NORMALE"}
    }
    advanced_event_ids = {
        event.id for event in events
        if (event.analysis_type or "").upper() in {"ADVANCED", "APPROFONDIE", "APPROFONDI"}
    }

    heepo_rows = (
        list(
            db.scalars(
                select(models.EventHeepoFactor).where(
                    models.EventHeepoFactor.event_id.in_(event_ids),
                    models.EventHeepoFactor.is_na.is_(False),
                )
            ).all()
        )
        if event_ids else []
    )
    heepo_rows = [
        row for row in heepo_rows
        if row.factor_code_snapshot or row.other_text
    ]
    heepo_family = Counter(
        (row.family, row.family) for row in heepo_rows
    )
    heepo_refs = {factor.code: factor for factor in db.scalars(select(models.HeepoFactor)).all()}
    heepo_factors = Counter(
        (
            row.factor_code_snapshot or "OTHER",
            (_translated_label(heepo_refs[row.factor_code_snapshot], language, row.factor_label_snapshot) if row.factor_code_snapshot in heepo_refs else row.other_text or row.factor_label_snapshot or "Autre"),
        )
        for row in heepo_rows
    )
    heepo_event_ids = {row.event_id for row in heepo_rows}

    classifications = (
        list(
            db.scalars(
                select(models.EventClassification).where(
                    models.EventClassification.event_id.in_(event_ids)
                )
            ).all()
        )
        if event_ids else []
    )
    classification_event_ids = {
        row.event_id
        for row in classifications
        if any(
            (
                row.deviation_code,
                row.material_agent_code,
                row.injury_nature_code,
                row.injury_location_code,
            )
        )
    }

    def classification_rows(code_field: str, label_field: str) -> list[dict]:
        counter = Counter()
        for row in classifications:
            code = getattr(row, code_field)
            label = getattr(row, label_field)
            if code:
                category_map = {"deviation_code": "DEVIATION", "material_agent_code": "MATERIAL_AGENT", "injury_nature_code": "INJURY_NATURE", "injury_location_code": "INJURY_LOCATION"}
                reference = db.scalar(select(models.EventCodeReference).where(models.EventCodeReference.category == category_map[code_field], models.EventCodeReference.code == code).limit(1))
                localized = _translated_label(reference, language, label) if reference else label or code
                counter[(code, localized)] += 1
        return _counter_rows(counter)

    just_culture = (
        list(
            db.scalars(
                select(models.EventJustCultureAnalysis).where(
                    models.EventJustCultureAnalysis.event_id.in_(normal_event_ids),
                    models.EventJustCultureAnalysis.status == "COMPLETED",
                    models.EventJustCultureAnalysis.conclusion_code.is_not(None),
                )
            ).all()
        )
        if event_ids else []
    )
    conclusions = Counter(
        (
            row.conclusion_code,
            _just_culture_label(db, row, language),
        )
        for row in just_culture
    )

    actions = (
        list(
            db.scalars(
                select(Action).where(
                    Action.origin_type == "ACCIDENT",
                    Action.event_id.in_(event_ids),
                )
            ).all()
        )
        if event_ids else []
    )
    status_counts = Counter(action.status for action in actions)
    done_statuses = {"DONE", "CLOSED"}
    done_count = sum(
        count for status, count in status_counts.items()
        if status in done_statuses
    )
    overdue_count = sum(
        1 for action in actions
        if action.status not in done_statuses
        and action.due_date is not None
        and action.due_date < datetime.now().date()
    )

    # Les actions LOCAL ont un avancement chiffré dans RISKY.
    # Les actions GLOBAL sont pilotées dans le suivi 9001 :
    # elles ne doivent donc pas être assimilées à 0 %.
    local_actions = [
        action for action in actions
        if action.scope == "LOCAL"
    ]
    global_actions = [
        action for action in actions
        if action.scope == "GLOBAL"
    ]
    local_progress_values = [
        action.progress_percent
        for action in local_actions
        if action.progress_percent is not None
    ]
    local_progress = (
        sum(local_progress_values) / len(local_progress_values)
        if local_progress_values else None
    )

    return {
        "scope": {
            "organization_id": organization_id,
            "organization_name": organization.name,
            "trade_code": effective_trade,
        },
        "period": {"year": year, "month_to": month_to},
        "events": {
            "count": event_count,
            "accidents": sum(e.event_type == "ACCIDENT" for e in events),
            "incidents": sum(e.event_type == "INCIDENT" for e in events),
            "near_misses": sum(e.event_type == "NEAR_MISS" for e in events),
        },
        "coverage": {
            "events": event_count,
            "normal_events": len(normal_event_ids),
            "advanced_events": len(advanced_event_ids),
            "heepo": len(heepo_event_ids),
            "classification": len(classification_event_ids),
            "just_culture": len(just_culture),
            "actions": len(actions),
        },
        "heepo": {
            "families": _counter_rows(heepo_family),
            "factors": _counter_rows(heepo_factors),
        },
        "classification": {
            "deviation": classification_rows(
                "deviation_code", "deviation_label_snapshot"
            ),
            "material_agent": classification_rows(
                "material_agent_code", "material_agent_label_snapshot"
            ),
            "injury_nature": classification_rows(
                "injury_nature_code", "injury_nature_label_snapshot"
            ),
            "injury_location": classification_rows(
                "injury_location_code", "injury_location_label_snapshot"
            ),
        },
        "just_culture": {
            "conclusions": _counter_rows(conclusions),
        },
        "actions": {
            "total": len(actions),
            "done": done_count,
            "completion_percent": local_progress,
            "local_count": len(local_actions),
            "global_9001_count": len(global_actions),
            "overdue": overdue_count,
            "statuses": [
                {"status": status, "count": count}
                for status, count in status_counts.items()
            ],
        },
    }
