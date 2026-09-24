from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import select

from ... import models
from ...schemas import events as schemas
from ...database import SessionLocal
from ...services.session import require_write_session
from ...services.audit import write_audit_log
from ...services.serious_accidents import evaluate_serious_accident


router = APIRouter(
    prefix="/events",
    tags=["Events - Accident grave"],
)

@router.post("/serious-accident-criteria/import/preview")
def preview_serious_accident_criteria_import(
    payload: schemas.SeriousAccidentCriterionImportPreview,
):
    db = SessionLocal()

    try:
        allowed_groups = {
            "DEVIATION_SERIOUS",
            "MATERIAL_AGENT_SERIOUS",
            "INJURY_TEMPORARY_SERIOUS",
        }

        allowed_match_types = {
            "EXACT",
            "RANGE",
        }

        summary = {
            "new": 0,
            "modified": 0,
            "unchanged": 0,
            "reactivated": 0,
            "missing": 0,
        }

        changes = []
        incoming_keys = set()

        for item in payload.items:

            if item.criterion_group not in allowed_groups:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Groupe de critÃ¨re accident grave invalide : "
                        f"{item.criterion_group}"
                    ),
                )

            if item.match_type not in allowed_match_types:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Type de correspondance invalide : "
                        f"{item.match_type}"
                    ),
                )

            if item.match_type == "EXACT" and item.code_to is not None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Le critÃ¨re EXACT {item.code_from} "
                        "ne peut pas avoir de code_to"
                    ),
                )

            if item.match_type == "RANGE" and not item.code_to:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Le critÃ¨re RANGE {item.code_from} "
                        "doit avoir un code_to"
                    ),
                )

            key = (
                item.criterion_group,
                item.match_type,
                item.code_from,
                item.code_to,
            )

            if key in incoming_keys:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Doublon dans l'import des critÃ¨res accident grave : "
                        f"{item.criterion_group} / "
                        f"{item.code_from} / {item.code_to}"
                    ),
                )

            incoming_keys.add(key)

            existing = (
                db.query(models.SeriousAccidentCriterion)
                .filter(
                    models.SeriousAccidentCriterion.criterion_group
                    == item.criterion_group,
                    models.SeriousAccidentCriterion.match_type
                    == item.match_type,
                    models.SeriousAccidentCriterion.code_from
                    == item.code_from,
                    models.SeriousAccidentCriterion.code_to
                    == item.code_to,
                )
                .first()
            )

            if existing is None:
                status = "NEW"
                old_data = None

            elif not existing.active:
                status = "REACTIVATED"
                old_data = {
                    "label": existing.label,
                    "requires_multiple_lost_days":
                        existing.requires_multiple_lost_days,
                }

            elif (
                existing.label != item.label
                or existing.requires_multiple_lost_days
                != item.requires_multiple_lost_days
            ):
                status = "MODIFIED"
                old_data = {
                    "label": existing.label,
                    "requires_multiple_lost_days":
                        existing.requires_multiple_lost_days,
                }

            else:
                status = "UNCHANGED"
                old_data = {
                    "label": existing.label,
                    "requires_multiple_lost_days":
                        existing.requires_multiple_lost_days,
                }

            summary[status.lower()] += 1

            changes.append(
                {
                    "criterion_group": item.criterion_group,
                    "match_type": item.match_type,
                    "code_from": item.code_from,
                    "code_to": item.code_to,
                    "status": status,
                    "old_data": old_data,
                    "new_data": {
                        "label": item.label,
                        "requires_multiple_lost_days":
                            item.requires_multiple_lost_days,
                    },
                }
            )

        existing_criteria = (
            db.query(models.SeriousAccidentCriterion)
            .filter(
                models.SeriousAccidentCriterion.active.is_(True)
            )
            .all()
        )

        for existing in existing_criteria:
            key = (
                existing.criterion_group,
                existing.match_type,
                existing.code_from,
                existing.code_to,
            )

            if key not in incoming_keys:
                summary["missing"] += 1

                changes.append(
                    {
                        "criterion_group": existing.criterion_group,
                        "match_type": existing.match_type,
                        "code_from": existing.code_from,
                        "code_to": existing.code_to,
                        "status": "MISSING",
                        "old_data": {
                            "label": existing.label,
                            "requires_multiple_lost_days":
                                existing.requires_multiple_lost_days,
                        },
                        "new_data": None,
                    }
                )

        return {
            "status": "preview",
            "source": payload.source,
            "source_version": payload.source_version,
            "summary": summary,
            "changes": changes,
        }

    finally:
        db.close()

@router.post("/serious-accident-criteria/import/apply")
def apply_serious_accident_criteria_import(
    payload: schemas.SeriousAccidentCriterionImportPreview,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        allowed_groups = {
            "DEVIATION_SERIOUS",
            "MATERIAL_AGENT_SERIOUS",
            "INJURY_TEMPORARY_SERIOUS",
        }

        allowed_match_types = {
            "EXACT",
            "RANGE",
        }

        summary = {
            "new": 0,
            "modified": 0,
            "unchanged": 0,
            "reactivated": 0,
            "deactivated": 0,
        }

        incoming_keys = set()

        for item in payload.items:

            if item.criterion_group not in allowed_groups:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Groupe de critÃ¨re accident grave invalide : "
                        f"{item.criterion_group}"
                    ),
                )

            if item.match_type not in allowed_match_types:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Type de correspondance invalide : "
                        f"{item.match_type}"
                    ),
                )

            if item.match_type == "EXACT" and item.code_to is not None:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Le critÃ¨re EXACT {item.code_from} "
                        "ne peut pas avoir de code_to"
                    ),
                )

            if item.match_type == "RANGE" and not item.code_to:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Le critÃ¨re RANGE {item.code_from} "
                        "doit avoir un code_to"
                    ),
                )

            key = (
                item.criterion_group,
                item.match_type,
                item.code_from,
                item.code_to,
            )

            if key in incoming_keys:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Doublon dans l'import des critÃ¨res accident grave : "
                        f"{item.criterion_group} / "
                        f"{item.code_from} / {item.code_to}"
                    ),
                )

            incoming_keys.add(key)

            existing = (
                db.query(models.SeriousAccidentCriterion)
                .filter(
                    models.SeriousAccidentCriterion.criterion_group
                    == item.criterion_group,
                    models.SeriousAccidentCriterion.match_type
                    == item.match_type,
                    models.SeriousAccidentCriterion.code_from
                    == item.code_from,
                    models.SeriousAccidentCriterion.code_to
                    == item.code_to,
                )
                .first()
            )

            if existing is None:
                criterion = models.SeriousAccidentCriterion(
                    criterion_group=item.criterion_group,
                    match_type=item.match_type,
                    code_from=item.code_from,
                    code_to=item.code_to,
                    label=item.label,
                    requires_multiple_lost_days=(
                        item.requires_multiple_lost_days
                    ),
                    active=True,
                )

                db.add(criterion)
                summary["new"] += 1

            elif not existing.active:
                existing.label = item.label
                existing.requires_multiple_lost_days = (
                    item.requires_multiple_lost_days
                )
                existing.active = True
                summary["reactivated"] += 1

            elif (
                existing.label != item.label
                or existing.requires_multiple_lost_days
                != item.requires_multiple_lost_days
            ):
                existing.label = item.label
                existing.requires_multiple_lost_days = (
                    item.requires_multiple_lost_days
                )
                summary["modified"] += 1

            else:
                summary["unchanged"] += 1

        existing_criteria = (
            db.query(models.SeriousAccidentCriterion)
            .filter(
                models.SeriousAccidentCriterion.active.is_(True)
            )
            .all()
        )

        for existing in existing_criteria:
            key = (
                existing.criterion_group,
                existing.match_type,
                existing.code_from,
                existing.code_to,
            )

            if key not in incoming_keys:
                existing.active = False
                summary["deactivated"] += 1

        write_audit_log(
            db=db,
            session=session,
            action="IMPORT",
            entity_type="SERIOUS_ACCIDENT_CRITERION",
            details=(
                f"Import critÃ¨res accident grave "
                f"{payload.source or ''} "
                f"{payload.source_version or ''} - "
                f"{summary}"
            ),
        )

        db.commit()

        return {
            "status": "applied",
            "source": payload.source,
            "source_version": payload.source_version,
            "summary": summary,
        }

    except:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# Ã‰VALUATION ACCIDENT GRAVE
# ============================================================

@router.get("/{event_id}/serious-accident-assessment")
def get_serious_accident_assessment(
    event_id: int,
):
    db = SessionLocal()

    try:
        event = db.get(
            models.Event,
            event_id,
        )

        if not event:
            raise HTTPException(
                status_code=404,
                detail="Ã‰vÃ©nement introuvable",
            )

        classification = db.scalar(
            select(models.EventClassification)
            .where(
                models.EventClassification.event_id
                == event_id
            )
        )

        return evaluate_serious_accident(
            db,
            event,
            classification,
        )

    finally:
        db.close()


