# ========================================================
# RISKY — ROUTES ACTIONS D'UN ÉVÉNEMENT
# ========================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.schemas.actions import (
    ActionCreate,
    ActionResponse,
    ActionUpdate,
    EventActionListResponse,
)
from backend.services.actions import (
    create_event_action,
    get_action,
    get_event_actions,
    update_action,
)
from backend.services.session import require_write_session


router = APIRouter()


# ========================================================
# LISTE DES ACTIONS DE L'ÉVÉNEMENT
# ========================================================

@router.get(
    "/events/{event_id}/actions",
    response_model=EventActionListResponse,
)
def list_event_actions(
    event_id: int,
):
    db: Session = SessionLocal()

    try:
        actions = get_event_actions(
            db,
            event_id,
        )

        return EventActionListResponse(
            event_id=event_id,
            actions=actions,
            count=len(actions),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    finally:
        db.close()


# ========================================================
# CRÉER UNE ACTION DEPUIS L'ÉVÉNEMENT
# ========================================================

@router.post(
    "/events/{event_id}/actions",
    response_model=ActionResponse,
)
def create_action(
    event_id: int,
    data: ActionCreate,
    session=Depends(require_write_session),
):
    db: Session = SessionLocal()

    try:
        action = create_event_action(
            db=db,
            event_id=event_id,
            data=data,
            created_by_person_id=session["person_id"],
        )

        db.commit()
        db.refresh(action)

        return action

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


# ========================================================
# MODIFIER UNE ACTION
# ========================================================

@router.put(
    "/events/{event_id}/actions/{action_id}",
    response_model=ActionResponse,
)
def modify_action(
    event_id: int,
    action_id: int,
    data: ActionUpdate,
    session=Depends(require_write_session),
):
    db: Session = SessionLocal()

    try:
        action = get_action(
            db,
            action_id,
        )

        # ------------------------------------------------
        # SÉCURITÉ DU LIEN ÉVÉNEMENT / ACTION
        # ------------------------------------------------

        if (
            action.origin_type != "ACCIDENT"
            or action.event_id != event_id
        ):
            raise ValueError(
                "Cette action n'appartient pas "
                "à cet événement."
            )

        action = update_action(
            db=db,
            action_id=action_id,
            data=data,
        )

        db.commit()
        db.refresh(action)

        return action

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