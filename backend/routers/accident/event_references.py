from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select

from ...database import SessionLocal
from ... import models
from ...schemas.event_references import EventCodeImportPreview

from ...services.session import require_write_session


router = APIRouter(
    prefix="/event-code-references",
    tags=["RÃ©fÃ©rentiels accidents"],
)


ALLOWED_CATEGORIES = {
    "DEVIATION",
    "MATERIAL_AGENT",
    "INJURY_NATURE",
    "INJURY_LOCATION",
}

# ============================================================
# CONSULTATION DES RÃ‰FÃ‰RENTIELS
# ============================================================

@router.get("")
def get_event_code_references(
    category: str,
):
    normalized_category = category.strip().upper()

    if normalized_category not in ALLOWED_CATEGORIES:
        return {
            "status": "error",
            "message": "CatÃ©gorie de rÃ©fÃ©rentiel inconnue",
            "allowed_categories": sorted(
                ALLOWED_CATEGORIES
            ),
        }

    db = SessionLocal()

    try:
        references = db.scalars(
            select(models.EventCodeReference)
            .where(
                models.EventCodeReference.category
                == normalized_category,
                models.EventCodeReference.active
                == True,
            )
            .order_by(
                models.EventCodeReference.id
            )
        ).all()

        return {
            "status": "ok",
            "category": normalized_category,
                        "items": [
                {
                    "id": reference.id,
                    "code": reference.code,
                    "label": reference.label,
                    "label_nl": reference.label_nl,
                    "label_en": reference.label_en,
                    "label_pl": reference.label_pl,
                }
                for reference in references
            ],
        }

    finally:
        db.close()

@router.post("/import/preview")
def preview_event_code_import(
    payload: EventCodeImportPreview,
):
    category = payload.category.strip().upper()

    if category not in ALLOWED_CATEGORIES:
        return {
            "status": "error",
            "message": "CatÃ©gorie de rÃ©fÃ©rentiel inconnue",
            "allowed_categories": sorted(
                ALLOWED_CATEGORIES
            ),
        }

    db = SessionLocal()

    try:
        existing_references = db.scalars(
            select(models.EventCodeReference)
            .where(
                models.EventCodeReference.category
                == category
            )
        ).all()

        existing_by_code = {
            reference.code.strip(): reference
            for reference in existing_references
        }

        imported_by_code = {}

        for item in payload.items:
            code = item.code.strip()
            label = item.label.strip()

            if not code:
                return {
                    "status": "error",
                    "message": "Un code importÃ© est vide",
                }

            if not label:
                return {
                    "status": "error",
                    "message": (
                        f"Le libellÃ© du code {code} "
                        "est vide"
                    ),
                }

            if code in imported_by_code:
                return {
                    "status": "error",
                    "message": (
                        f"Le code {code} apparaÃ®t "
                        "plusieurs fois dans l'import"
                    ),
                }

            imported_by_code[code] = label

        changes = []

        summary = {
            "new": 0,
            "modified": 0,
            "unchanged": 0,
            "reactivated": 0,
            "missing": 0,
        }

        for code, new_label in imported_by_code.items():
            existing = existing_by_code.get(code)

            if existing is None:
                summary["new"] += 1

                changes.append(
                    {
                        "code": code,
                        "status": "NEW",
                        "old_label": None,
                        "new_label": new_label,
                    }
                )

                continue

            if not existing.active:
                change_status = "REACTIVATED"
                summary["reactivated"] += 1

            elif existing.label.strip() != new_label:
                change_status = "MODIFIED"
                summary["modified"] += 1

            else:
                change_status = "UNCHANGED"
                summary["unchanged"] += 1

            changes.append(
                {
                    "code": code,
                    "status": change_status,
                    "old_label": existing.label,
                    "new_label": new_label,
                }
            )

        for code, existing in existing_by_code.items():
            if (
                existing.active
                and code not in imported_by_code
            ):
                summary["missing"] += 1

                changes.append(
                    {
                        "code": code,
                        "status": "MISSING",
                        "old_label": existing.label,
                        "new_label": None,
                    }
                )

        return {
            "status": "preview",
            "category": category,
            "source": payload.source,
            "source_version": payload.source_version,
            "summary": summary,
            "changes": changes,
        }

    finally:
        db.close()


@router.post("/import/apply")
def apply_event_code_import(
    payload: EventCodeImportPreview,
    session=Depends(require_write_session),
):
    
    category = payload.category.strip().upper()

    if category not in ALLOWED_CATEGORIES:
        return {
            "status": "error",
            "message": "CatÃ©gorie de rÃ©fÃ©rentiel inconnue",
            "allowed_categories": sorted(
                ALLOWED_CATEGORIES
            ),
        }

    db = SessionLocal()

    try:
        existing_references = db.scalars(
            select(models.EventCodeReference)
            .where(
                models.EventCodeReference.category
                == category
            )
        ).all()

        existing_by_code = {
            reference.code.strip(): reference
            for reference in existing_references
        }

        imported_by_code = {}

        for item in payload.items:
            code = item.code.strip()
            label = item.label.strip()

            if not code:
                return {
                    "status": "error",
                    "message": "Un code importÃ© est vide",
                }

            if not label:
                return {
                    "status": "error",
                    "message": (
                        f"Le libellÃ© du code {code} "
                        "est vide"
                    ),
                }

            if code in imported_by_code:
                return {
                    "status": "error",
                    "message": (
                        f"Le code {code} apparaÃ®t "
                        "plusieurs fois dans l'import"
                    ),
                }

            imported_by_code[code] = label

        now = datetime.now()

        summary = {
            "new": 0,
            "modified": 0,
            "unchanged": 0,
            "reactivated": 0,
            "deactivated": 0,
        }

        for code, new_label in imported_by_code.items():
            existing = existing_by_code.get(code)

            if existing is None:
                db.add(
                    models.EventCodeReference(
                        category=category,
                        code=code,
                        label=new_label,
                        active=True,
                        source=payload.source,
                        source_version=payload.source_version,
                        imported_at=now,
                        updated_at=now,
                    )
                )

                summary["new"] += 1
                continue

            changed = False

            if existing.label.strip() != new_label:
                existing.label = new_label
                summary["modified"] += 1
                changed = True

            if not existing.active:
                existing.active = True
                summary["reactivated"] += 1
                changed = True

            if changed:
                existing.updated_at = now
                existing.source = payload.source
                existing.source_version = (
                    payload.source_version
                )
            else:
                summary["unchanged"] += 1

        for code, existing in existing_by_code.items():
            if (
                existing.active
                and code not in imported_by_code
            ):
                existing.active = False
                existing.updated_at = now
                existing.source = payload.source
                existing.source_version = (
                    payload.source_version
                )

                summary["deactivated"] += 1

        db.commit()

        return {
            "status": "applied",
            "category": category,
            "source": payload.source,
            "source_version": payload.source_version,
            "summary": summary,
        }

    finally:
        db.close()

