from fastapi import APIRouter, Depends, HTTPException

from .. import models
from ..database import SessionLocal
from ..services.session import require_write_session
from ..services.audit import write_audit_log
from ..schemas import events as schemas


router = APIRouter(
    prefix="/events",
    tags=["Events - HEEPO"],
)


def get_active_heepo_factor(
    db,
    factor_id: int | None,
    family: str,
):
    if factor_id is None:
        return None

    factor = db.get(models.HeepoFactor, factor_id)

    if factor is None:
        raise HTTPException(
            status_code=400,
            detail=f"Facteur HEEPO {factor_id} introuvable",
        )

    if not factor.active:
        raise HTTPException(
            status_code=400,
            detail=f"Facteur HEEPO {factor.code} inactif",
        )

    if factor.family != family:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Le facteur {factor.code} appartient à la famille "
                f"{factor.family} et non à {family}"
            ),
        )

    return factor

@router.post("/heepo-factors/import/preview")
def preview_heepo_factor_import(
    payload: schemas.HeepoFactorImportPreview,
):
    db = SessionLocal()

    try:
        allowed_families = {
            "HOMME",
            "EQUIPEMENT",
            "ENVIRONNEMENT",
            "ORGANISATION",
            "PRODUIT",
        }

        changes = []
        summary = {
            "new": 0,
            "modified": 0,
            "unchanged": 0,
            "reactivated": 0,
            "missing": 0,
        }

        incoming_keys = set()

        for item in payload.items:
            if item.family not in allowed_families:
                raise HTTPException(
                    status_code=400,
                    detail=f"Famille HEEPO invalide : {item.family}",
                )

            key = (item.family, item.code)

            if key in incoming_keys:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Doublon HEEPO dans l'import : "
                        f"{item.family} / {item.code}"
                    ),
                )

            incoming_keys.add(key)

            existing = (
                db.query(models.HeepoFactor)
                .filter(
                    models.HeepoFactor.family == item.family,
                    models.HeepoFactor.code == item.code,
                )
                .first()
            )

            if existing is None:
                status = "NEW"
                old_label = None

            elif not existing.active:
                status = "REACTIVATED"
                old_label = existing.label

            elif existing.label != item.label:
                status = "MODIFIED"
                old_label = existing.label

            else:
                status = "UNCHANGED"
                old_label = existing.label

            summary[status.lower()] += 1

            changes.append(
                {
                    "family": item.family,
                    "code": item.code,
                    "status": status,
                    "old_label": old_label,
                    "new_label": item.label,
                }
            )

        existing_factors = (
            db.query(models.HeepoFactor)
            .filter(models.HeepoFactor.active.is_(True))
            .all()
        )

        for existing in existing_factors:
            key = (existing.family, existing.code)

            if key not in incoming_keys:
                summary["missing"] += 1

                changes.append(
                    {
                        "family": existing.family,
                        "code": existing.code,
                        "status": "MISSING",
                        "old_label": existing.label,
                        "new_label": None,
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


@router.post("/heepo-factors/import/apply")
def apply_heepo_factor_import(
    payload: schemas.HeepoFactorImportPreview,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        allowed_families = {
            "HOMME",
            "EQUIPEMENT",
            "ENVIRONNEMENT",
            "ORGANISATION",
            "PRODUIT",
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
            if item.family not in allowed_families:
                raise HTTPException(
                    status_code=400,
                    detail=f"Famille HEEPO invalide : {item.family}",
                )

            key = (item.family, item.code)

            if key in incoming_keys:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Doublon HEEPO dans l'import : "
                        f"{item.family} / {item.code}"
                    ),
                )

            incoming_keys.add(key)

            existing = (
                db.query(models.HeepoFactor)
                .filter(
                    models.HeepoFactor.family == item.family,
                    models.HeepoFactor.code == item.code,
                )
                .first()
            )

            if existing is None:
                factor = models.HeepoFactor(
                    family=item.family,
                    code=item.code,
                    label=item.label,
                    active=True,
                )
                db.add(factor)
                summary["new"] += 1

            elif not existing.active:
                existing.label = item.label
                existing.active = True
                summary["reactivated"] += 1

            elif existing.label != item.label:
                existing.label = item.label
                summary["modified"] += 1

            else:
                summary["unchanged"] += 1

        existing_factors = (
            db.query(models.HeepoFactor)
            .filter(models.HeepoFactor.active.is_(True))
            .all()
        )

        for existing in existing_factors:
            key = (existing.family, existing.code)

            if key not in incoming_keys:
                existing.active = False
                summary["deactivated"] += 1

        write_audit_log(
            db=db,
            session=session,
            action="IMPORT",
            entity_type="HEEPO_FACTOR_REFERENCE",
            details=(
                f"Import catalogue HEEPO "
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
# CONSULTATION DU RÉFÉRENTIEL HEEPO
# ============================================================

@router.get("/heepo-factors")
def get_heepo_factors():
    db = SessionLocal()

    try:
        factors = (
            db.query(models.HeepoFactor)
            .filter(
                models.HeepoFactor.active.is_(True)
            )
            .order_by(
                models.HeepoFactor.family,
                models.HeepoFactor.id,
            )
            .all()
        )

        return {
            "items": [
                {
                    "id": factor.id,
                    "family": factor.family,
                    "code": factor.code,
                    "label": factor.label,
                }
                for factor in factors
            ]
        }

    finally:
        db.close()

@router.put(
    "/{event_id}/heepo",
    response_model=schemas.EventHeepoResponse,
)
def update_event_heepo(
    event_id: int,
    payload: schemas.EventHeepoUpdate,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        event = db.get(models.Event, event_id)

        if event is None:
            raise HTTPException(
                status_code=404,
                detail="Événement introuvable",
            )

        allowed_families = {
            "HOMME",
            "EQUIPEMENT",
            "ENVIRONNEMENT",
            "ORGANISATION",
            "PRODUIT",
        }

        # ---------------------------------------------------------
        # 1. Validation complète avant toute modification
        # ---------------------------------------------------------

        validated_items = []
        items_by_family = {}

        for item in payload.items:
            if item.family not in allowed_families:
                raise HTTPException(
                    status_code=400,
                    detail=f"Famille HEEPO invalide : {item.family}",
                )

            items_by_family.setdefault(item.family, []).append(item)

        for family, family_items in items_by_family.items():

            na_items = [
                item for item in family_items
                if item.is_na
            ]

            # N.A. est exclusif dans une famille
            if na_items:
                if len(family_items) != 1:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"N.A. est exclusif pour la famille {family}"
                        ),
                    )

                item = na_items[0]

                if item.factor_id is not None or item.other_text:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"N.A. ne peut pas contenir de facteur "
                            f"ou de texte libre pour {family}"
                        ),
                    )

                validated_items.append(
                    {
                        "family": family,
                        "factor": None,
                        "other_text": None,
                        "is_na": True,
                    }
                )

                continue

            # Facteurs normaux
            for item in family_items:
                if item.factor_id is None:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Un facteur HEEPO est requis pour "
                            f"la famille {family}"
                        ),
                    )

                factor = get_active_heepo_factor(
                    db,
                    item.factor_id,
                    family,
                )

                is_other = factor.code in {
                    "H0",
                    "E0",
                    "En0",
                    "O0",
                    "P0",
                }

                if is_other and not (
                    item.other_text
                    and item.other_text.strip()
                ):
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Un texte libre est obligatoire "
                            f"pour le facteur {factor.code} - Autres"
                        ),
                    )

                if not is_other and item.other_text:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Le texte libre est uniquement autorisé "
                            f"pour un facteur Autres"
                        ),
                    )

                validated_items.append(
                    {
                        "family": family,
                        "factor": factor,
                        "other_text": (
                            item.other_text.strip()
                            if item.other_text
                            else None
                        ),
                        "is_na": False,
                    }
                )

        # ---------------------------------------------------------
        # 2. Snapshot AVANT modification
        # ---------------------------------------------------------

        existing_items = (
            db.query(models.EventHeepoFactor)
            .filter(
                models.EventHeepoFactor.event_id == event_id
            )
            .all()
        )

        before_data = [
            {
                "family": item.family,
                "factor_code": item.factor_code_snapshot,
                "factor_label": item.factor_label_snapshot,
                "other_text": item.other_text,
                "is_na": item.is_na,
            }
            for item in existing_items
        ]

        # ---------------------------------------------------------
        # 3. Remplacement de l'analyse HEEPO
        # ---------------------------------------------------------

        for item in existing_items:
            db.delete(item)

        db.flush()

        created_items = []

        for validated in validated_items:
            factor = validated["factor"]

            new_item = models.EventHeepoFactor(
                event_id=event_id,
                heepo_factor_id=(
                    factor.id if factor else None
                ),
                family=validated["family"],
                factor_code_snapshot=(
                    factor.code if factor else None
                ),
                factor_label_snapshot=(
                    factor.label if factor else None
                ),
                other_text=validated["other_text"],
                is_na=validated["is_na"],
            )

            db.add(new_item)
            created_items.append(new_item)

        db.flush()

        # ---------------------------------------------------------
        # 4. Snapshot APRÈS modification
        # ---------------------------------------------------------

        after_data = [
            {
                "family": item.family,
                "factor_code": item.factor_code_snapshot,
                "factor_label": item.factor_label_snapshot,
                "other_text": item.other_text,
                "is_na": item.is_na,
            }
            for item in created_items
        ]

        # ---------------------------------------------------------
        # 5. Audit
        # ---------------------------------------------------------

        write_audit_log(
            db=db,
            session=session,
            action="CREATE" if not before_data else "UPDATE",
            entity_type="EVENT_HEEPO",
            entity_id=event_id,
            before_data=before_data if before_data else None,
            after_data=after_data,
            details=f"Analyse HEEPO de l'événement {event.event_number}",
        )

        db.commit()

        for item in created_items:
            db.refresh(item)

        return {
            "event_id": event_id,
            "items": created_items,
        }

    except:
        db.rollback()
        raise

    finally:
        db.close()

@router.get(
    "/{event_id}/heepo",
    response_model=schemas.EventHeepoResponse,
)
def get_event_heepo(
    event_id: int,
):
    db = SessionLocal()

    try:
        event = db.get(models.Event, event_id)

        if event is None:
            raise HTTPException(
                status_code=404,
                detail="Événement introuvable",
            )

        items = (
            db.query(models.EventHeepoFactor)
            .filter(
                models.EventHeepoFactor.event_id == event_id
            )
            .order_by(models.EventHeepoFactor.id)
            .all()
        )

        return {
            "event_id": event_id,
            "items": items,
        }

    finally:
        db.close()
