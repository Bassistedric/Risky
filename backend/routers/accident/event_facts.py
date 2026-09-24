from fastapi import APIRouter, Depends, HTTPException

from ... import models
from ...database import SessionLocal
from ...schemas.events import EventFactsUpdate, EventFactsResponse
from ...services.session import require_write_session
from ...services.audit import write_audit_log


router = APIRouter(
    prefix="/events",
    tags=["Events - Relation des faits"],
)

@router.put(
    "/{event_id}/facts",
    response_model=EventFactsResponse,
)
def update_event_facts(
    event_id: int,
    data: EventFactsUpdate,
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

        facts = event.facts

        if facts is None:
            facts = models.EventFacts(
                event_id=event.id,
            )
            db.add(facts)
            action = "CREATE"
            before_data = None

        else:
            action = "UPDATE"
            before_data = {
                column.name: getattr(facts, column.name)
                for column in models.EventFacts.__table__.columns
            }

        update_data = data.model_dump()

        for field, value in update_data.items():
            setattr(facts, field, value)

        db.flush()

        after_data = {
            column.name: getattr(facts, column.name)
            for column in models.EventFacts.__table__.columns
        }

        write_audit_log(
            db=db,
            session=session,
            action=action,
            entity_type="EVENT_FACTS",
            entity_id=facts.id,
            before_data=before_data,
            after_data=after_data,
            details=f"Relation des faits de l'Ã©vÃ©nement {event.event_number}",
        )

        db.commit()
        db.refresh(facts)

        return facts

    except:
        db.rollback()
        raise

    finally:
        db.close()


@router.get(
    "/{event_id}/facts",
    response_model=EventFactsResponse,
)
def get_event_facts(event_id: int):
    db = SessionLocal()

    try:
        event = db.get(models.Event, event_id)

        if event is None:
            raise HTTPException(
                status_code=404,
                detail="Ã‰vÃ©nement introuvable",
            )

        if event.facts is None:
            raise HTTPException(
                status_code=404,
                detail="Relation des faits non renseignÃ©e",
            )

        return event.facts

    finally:
        db.close()

