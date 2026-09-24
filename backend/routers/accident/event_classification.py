from fastapi import APIRouter, Depends, HTTPException

from ... import models
from ...database import SessionLocal
from ...schemas import events as schemas
from ...services.audit import write_audit_log
from ...services.serious_accidents import evaluate_serious_accident
from ...services.session import require_write_session


router = APIRouter(
    prefix="/events",
    tags=["Events - Classification"],
)


def get_active_event_code_reference(
    db,
    category: str,
    code: str | None,
):
    if code is None:
        return None

    reference = (
        db.query(models.EventCodeReference)
        .filter(
            models.EventCodeReference.category == category,
            models.EventCodeReference.code == code,
            models.EventCodeReference.active.is_(True),
        )
        .first()
    )

    if reference is None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Code '{code}' invalide ou inactif "
                f"pour la catÃ©gorie '{category}'"
            ),
        )

    return reference


@router.put(
    "/{event_id}/classification",
    response_model=schemas.EventClassificationUpdateResponse,
)
def update_event_classification(
    event_id: int,
    payload: schemas.EventClassificationUpdate,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        event = db.get(models.Event, event_id)

        if event is None:
            raise HTTPException(
                status_code=404,
                detail="Ã‰vÃ©nement introuvable",
            )

        deviation = get_active_event_code_reference(
            db,
            "DEVIATION",
            payload.deviation_code,
        )

        material_agent = get_active_event_code_reference(
            db,
            "MATERIAL_AGENT",
            payload.material_agent_code,
        )

        injury_nature = get_active_event_code_reference(
            db,
            "INJURY_NATURE",
            payload.injury_nature_code,
        )

        injury_location = get_active_event_code_reference(
            db,
            "INJURY_LOCATION",
            payload.injury_location_code,
        )

        classification = (
            db.query(models.EventClassification)
            .filter(
                models.EventClassification.event_id
                == event_id
            )
            .first()
        )

        is_new = classification is None
        before_data = None

        if classification is None:
            classification = models.EventClassification(
                event_id=event_id,
            )
            db.add(classification)
        else:
            before_data = {
                "deviation_code": classification.deviation_code,
                "deviation_label_snapshot":
                    classification.deviation_label_snapshot,
                "material_agent_code":
                    classification.material_agent_code,
                "material_agent_label_snapshot":
                    classification.material_agent_label_snapshot,
                "injury_nature_code":
                    classification.injury_nature_code,
                "injury_nature_label_snapshot":
                    classification.injury_nature_label_snapshot,
                "injury_location_code":
                    classification.injury_location_code,
                "injury_location_label_snapshot":
                    classification.injury_location_label_snapshot,
            }

        classification.deviation_code = (
            deviation.code if deviation else None
        )
        classification.deviation_label_snapshot = (
            deviation.label if deviation else None
        )

        classification.material_agent_code = (
            material_agent.code if material_agent else None
        )
        classification.material_agent_label_snapshot = (
            material_agent.label if material_agent else None
        )

        classification.injury_nature_code = (
            injury_nature.code if injury_nature else None
        )
        classification.injury_nature_label_snapshot = (
            injury_nature.label if injury_nature else None
        )

        classification.injury_location_code = (
            injury_location.code if injury_location else None
        )
        classification.injury_location_label_snapshot = (
            injury_location.label if injury_location else None
        )

        db.flush()

        after_data = {
            "deviation_code": classification.deviation_code,
            "deviation_label_snapshot":
                classification.deviation_label_snapshot,
            "material_agent_code":
                classification.material_agent_code,
            "material_agent_label_snapshot":
                classification.material_agent_label_snapshot,
            "injury_nature_code":
                classification.injury_nature_code,
            "injury_nature_label_snapshot":
                classification.injury_nature_label_snapshot,
            "injury_location_code":
                classification.injury_location_code,
            "injury_location_label_snapshot":
                classification.injury_location_label_snapshot,
        }

        write_audit_log(
            db=db,
            session=session,
            action="CREATE" if is_new else "UPDATE",
            entity_type="EVENT_CLASSIFICATION",
            entity_id=classification.id,
            before_data=before_data,
            after_data=after_data,
            details=(
                "Classification de l'Ã©vÃ©nement "
                f"{event.event_number}"
            ),
        )

        db.commit()
        db.refresh(classification)

        serious_accident_result = evaluate_serious_accident(
            db,
            event,
            classification,
        )

        return {
            "classification": classification,
            **serious_accident_result,
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


@router.get(
    "/{event_id}/classification",
    response_model=schemas.EventClassificationResponse,
)
def get_event_classification(event_id: int):
    db = SessionLocal()

    try:
        event = db.get(models.Event, event_id)

        if event is None:
            raise HTTPException(
                status_code=404,
                detail="Ã‰vÃ©nement introuvable",
            )

        classification = (
            db.query(models.EventClassification)
            .filter(
                models.EventClassification.event_id
                == event_id
            )
            .first()
        )

        if classification is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Aucune classification pour cet Ã©vÃ©nement"
                ),
            )

        return classification

    finally:
        db.close()


