# ========================================================
# RISKY — ROUTES TRANSVERSES ACTIONS
# ========================================================

from fastapi import APIRouter, Depends, Query

from backend.database import SessionLocal
from backend.schemas.actions import (
    ActionListResponse,
    ActionResponse,
    TransverseActionResponse,
)

from backend.services.actions import get_actions
from backend.services.session import require_write_session


# ========================================================
# ROUTER
# ========================================================

router = APIRouter(
    prefix="/actions",
    tags=["actions"],
)


# ========================================================
# LISTE TRANSVERSE DES ACTIONS
# ========================================================

@router.get(
    "",
    response_model=ActionListResponse,
)
def list_actions(
    origin_type: str | None = Query(
        default=None,
    ),
    status: str | None = Query(
        default=None,
    ),
    responsible_person_id: int | None = Query(
        default=None,
    ),
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:

        rows = get_actions(
    db,
    origin_type=origin_type,
    status=status,
    responsible_person_id=responsible_person_id,
        )

        actions = []

        for action, origin_reference in rows:
            action_data = ActionResponse.model_validate(
                action,
            ).model_dump()

            actions.append(
                TransverseActionResponse(
                    **action_data,
                    origin_reference=origin_reference,
                )
            )

        return ActionListResponse(
            count=len(actions),
            actions=actions,
        )


    finally:
        db.close()