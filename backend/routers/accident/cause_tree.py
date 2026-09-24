from fastapi import APIRouter, Depends, HTTPException

from ...database import SessionLocal
from ...schemas.cause_tree import (
    EventCauseFactCreate,
    EventCauseFactUpdate,
    EventCauseFactResponse,
    EventCauseFactGuidedCreate,
    EventCauseFactGuidedResponse,
    EventCauseRelationCreate,
    EventCauseRelationResponse,
    EventCauseTreeResponse,
    EventCauseLevelsResponse,
    EventCauseFactLevelResponse,
)
from ...services.audit import write_audit_log
from ...services.cause_tree import (
    calculate_event_cause_levels,
    close_event_cause_branch,
    reopen_event_cause_branch,
    create_event_cause_fact,
    create_event_cause_fact_guided,
    create_event_cause_relation,
    delete_event_cause_fact,
    delete_event_cause_relation,
    get_event_cause_tree,
    set_event_cause_final_fact,
    update_event_cause_fact,
)
from ...services.session import require_write_session


router = APIRouter(
    prefix="/events",
    tags=["Cause Tree"],
)


@router.post(
    "/{event_id}/cause-tree/facts",
    response_model=EventCauseFactResponse,
)
def create_cause_fact(
    event_id: int,
    payload: EventCauseFactCreate,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        fact = create_event_cause_fact(
            db=db,
            event_id=event_id,
            description=payload.description,
            fact_type=payload.fact_type,
            sort_order=payload.sort_order,
        )

        write_audit_log(
            db=db,
            session=session,
            action="CREATE",
            entity_type="EVENT_CAUSE_FACT",
            entity_id=fact.id,
            after_data={
                "event_id": fact.event_id,
                "fact_type": fact.fact_type,
                "description": fact.description,
                "sort_order": fact.sort_order,
            },
            details="CrÃ©ation d'un fait dans l'arbre des causes.",
        )

        db.commit()
        db.refresh(fact)

        return fact

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

@router.post(
    "/{event_id}/cause-tree/relations",
    response_model=EventCauseRelationResponse,
)
def create_cause_relation(
    event_id: int,
    payload: EventCauseRelationCreate,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        relation = create_event_cause_relation(
            db=db,
            event_id=event_id,
            cause_fact_id=payload.cause_fact_id,
            effect_fact_id=payload.effect_fact_id,
        )

        write_audit_log(
            db=db,
            session=session,
            action="CREATE",
            entity_type="EVENT_CAUSE_RELATION",
            entity_id=relation.id,
            after_data={
                "event_id": relation.event_id,
                "cause_fact_id": relation.cause_fact_id,
                "effect_fact_id": relation.effect_fact_id,
            },
            details="CrÃ©ation d'une relation dans l'arbre des causes.",
        )

        db.commit()
        db.refresh(relation)

        return relation

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

@router.get(
    "/{event_id}/cause-tree",
    response_model=EventCauseTreeResponse,
)
def get_cause_tree(
    event_id: int,
):
    db = SessionLocal()

    try:
        facts, relations = get_event_cause_tree(
            db=db,
            event_id=event_id,
        )

        return EventCauseTreeResponse(
            event_id=event_id,
            facts=facts,
            relations=relations,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    finally:
        db.close()

@router.delete(
    "/{event_id}/cause-tree/facts/{fact_id}",
)
def delete_cause_fact(
    event_id: int,
    fact_id: int,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        deleted_fact, deleted_relation_ids = (
            delete_event_cause_fact(
                db=db,
                event_id=event_id,
                fact_id=fact_id,
            )
        )

        write_audit_log(
            db=db,
            session=session,
            action="DELETE",
            entity_type="EVENT_CAUSE_FACT",
            entity_id=deleted_fact["id"],
            before_data=deleted_fact,
            after_data=None,
            details=(
                "Suppression d'un fait de l'arbre des causes. "
                f"Relations supprimÃ©es : {deleted_relation_ids}."
            ),
        )

        db.commit()

        return {
            "success": True,
            "deleted_fact_id": deleted_fact["id"],
            "deleted_relation_ids": deleted_relation_ids,
        }

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

@router.delete(
    "/{event_id}/cause-tree/relations/{relation_id}",
)
def delete_cause_relation(
    event_id: int,
    relation_id: int,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        deleted_relation = delete_event_cause_relation(
            db=db,
            event_id=event_id,
            relation_id=relation_id,
        )

        write_audit_log(
            db=db,
            session=session,
            action="DELETE",
            entity_type="EVENT_CAUSE_RELATION",
            entity_id=deleted_relation["id"],
            before_data=deleted_relation,
            after_data=None,
            details="Suppression d'une relation dans l'arbre des causes.",
        )

        db.commit()

        return {
            "success": True,
            "deleted_relation_id": deleted_relation["id"],
        }

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

@router.put(
    "/{event_id}/cause-tree/facts/{fact_id}",
    response_model=EventCauseFactResponse,
)
def update_cause_fact(
    event_id: int,
    fact_id: int,
    payload: EventCauseFactUpdate,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        fact, before_data = update_event_cause_fact(
            db=db,
            event_id=event_id,
            fact_id=fact_id,
            description=payload.description,
            sort_order=payload.sort_order,
        )

        after_data = {
            "id": fact.id,
            "event_id": fact.event_id,
            "fact_type": fact.fact_type,
            "description": fact.description,
            "sort_order": fact.sort_order,
        }

        write_audit_log(
            db=db,
            session=session,
            action="UPDATE",
            entity_type="EVENT_CAUSE_FACT",
            entity_id=fact.id,
            before_data=before_data,
            after_data=after_data,
            details="Modification d'un fait dans l'arbre des causes.",
        )

        db.commit()
        db.refresh(fact)

        return fact

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

@router.post(
    "/{event_id}/cause-tree/facts/{fact_id}/close-branch",
    response_model=EventCauseFactResponse,
)
def close_cause_branch(
    event_id: int,
    fact_id: int,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        fact, before_data = close_event_cause_branch(
            db=db,
            event_id=event_id,
            fact_id=fact_id,
        )

        after_data = {
            "id": fact.id,
            "event_id": fact.event_id,
            "fact_type": fact.fact_type,
            "description": fact.description,
            "sort_order": fact.sort_order,
            "is_terminal": fact.is_terminal,
        }

        write_audit_log(
            db=db,
            session=session,
            action="CLOSE_BRANCH",
            entity_type="EVENT_CAUSE_FACT",
            entity_id=fact.id,
            before_data=before_data,
            after_data=after_data,
            details="Branche terminÃ©e dans l'arbre des causes.",
        )

        db.commit()
        db.refresh(fact)

        return fact

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

@router.post(
    "/{event_id}/cause-tree/facts/{fact_id}/reopen-branch",
    response_model=EventCauseFactResponse,
)
def reopen_cause_branch(
    event_id: int,
    fact_id: int,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        fact, before_data = reopen_event_cause_branch(
            db=db,
            event_id=event_id,
            fact_id=fact_id,
        )

        after_data = {
            "id": fact.id,
            "event_id": fact.event_id,
            "fact_type": fact.fact_type,
            "description": fact.description,
            "sort_order": fact.sort_order,
            "is_terminal": fact.is_terminal,
        }

        write_audit_log(
            db=db,
            session=session,
            action="REOPEN_BRANCH",
            entity_type="EVENT_CAUSE_FACT",
            entity_id=fact.id,
            before_data=before_data,
            after_data=after_data,
            details="Branche rouverte dans l'arbre des causes.",
        )

        db.commit()
        db.refresh(fact)

        return fact

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

@router.post(
    "/{event_id}/cause-tree/facts/{fact_id}/set-final",
    response_model=EventCauseFactResponse,
)
def set_cause_final_fact(
    event_id: int,
    fact_id: int,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        fact, before_data = set_event_cause_final_fact(
            db=db,
            event_id=event_id,
            fact_id=fact_id,
        )

        after_data = {
            "id": fact.id,
            "event_id": fact.event_id,
            "fact_type": fact.fact_type,
            "description": fact.description,
            "sort_order": fact.sort_order,
            "is_terminal": fact.is_terminal,
        }

        write_audit_log(
            db=db,
            session=session,
            action="SET_FINAL",
            entity_type="EVENT_CAUSE_FACT",
            entity_id=fact.id,
            before_data=before_data,
            after_data=after_data,
            details="DÃ©signation du fait final de l'arbre des causes.",
        )

        db.commit()
        db.refresh(fact)

        return fact

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

@router.post(
    "/{event_id}/cause-tree/guided-facts",
    response_model=EventCauseFactGuidedResponse,
)
def create_guided_cause_fact(
    event_id: int,
    payload: EventCauseFactGuidedCreate,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        fact, relations = create_event_cause_fact_guided(
            db=db,
            event_id=event_id,
            description=payload.description,
            sort_order=payload.sort_order,
            effect_fact_ids=payload.effect_fact_ids,
        )

        after_data = {
            "fact": {
                "id": fact.id,
                "event_id": fact.event_id,
                "fact_type": fact.fact_type,
                "description": fact.description,
                "sort_order": fact.sort_order,
                "is_terminal": fact.is_terminal,
            },
            "relations": [
                {
                    "id": relation.id,
                    "event_id": relation.event_id,
                    "cause_fact_id": relation.cause_fact_id,
                    "effect_fact_id": relation.effect_fact_id,
                }
                for relation in relations
            ],
        }

        write_audit_log(
            db=db,
            session=session,
            action="GUIDED_CREATE",
            entity_type="EVENT_CAUSE_FACT",
            entity_id=fact.id,
            after_data=after_data,
            details=(
                "CrÃ©ation guidÃ©e d'un Ã©lÃ©ment "
                "dans l'arbre des causes."
            ),
        )

        db.commit()
        db.refresh(fact)

        return EventCauseFactGuidedResponse(
            fact=fact,
            relations=relations,
        )

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

@router.get(
    "/{event_id}/cause-tree/levels",
    response_model=EventCauseLevelsResponse,
)
def get_cause_tree_levels(
    event_id: int,
):
    db = SessionLocal()

    try:
        levels = calculate_event_cause_levels(
            db=db,
            event_id=event_id,
        )

        return EventCauseLevelsResponse(
            event_id=event_id,
            levels=[
                EventCauseFactLevelResponse(
                    fact_id=fact_id,
                    level=level,
                )
                for fact_id, level in sorted(
                    levels.items(),
                    key=lambda item: (
                        item[1],
                        item[0],
                    ),
                )
            ],
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        db.close()

