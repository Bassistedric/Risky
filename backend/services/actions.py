# ========================================================
# RISKY — SERVICE MÉTIER ACTIONS
# ========================================================

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import models
from backend.domain_models.actions.action import Action
from backend.schemas.actions import ActionCreate, ActionUpdate


# ========================================================
# RÉFÉRENTIELS MÉTIER
# ========================================================

ALLOWED_ACTION_TYPES = {
    "CORRECTIVE",
    "PREVENTIVE",
}

ALLOWED_SCOPES = {
    "LOCAL",
    "GLOBAL",
}

ALLOWED_PRIORITIES = {
    "LOW",
    "MEDIUM",
    "HIGH",
}

ALLOWED_STATUSES = {
    "TODO",
    "IN_PROGRESS",
    "DONE",
    "TO_VALIDATE",
    "CLOSED",
}

ALLOWED_PROCESS_CODES = {
    "PR01",
    "PR02",
    "PR03",
    "PR04",
    "PR05",
    "PR06",
    "PR07",
    "PR08",
}


# ========================================================
# CONTRÔLES GÉNÉRAUX
# ========================================================

def _ensure_event_exists(
    db: Session,
    event_id: int,
) -> None:
    event = db.get(models.Event, event_id)

    if not event:
        raise ValueError("Événement introuvable.")


def _ensure_person_exists(
    db: Session,
    person_id: int | None,
) -> None:
    if person_id is None:
        return

    person = db.get(models.Person, person_id)

    if not person:
        raise ValueError("Responsable introuvable.")


# ========================================================
# NORMALISATION / VALIDATION MÉTIER
# ========================================================

def _validate_action_values(
    *,
    action_type: str,
    scope: str,
    process_code: str | None,
    priority: str,
    status: str,
    progress_percent: int | None,
) -> dict:
    action_type = action_type.strip().upper()
    scope = scope.strip().upper()
    priority = priority.strip().upper()
    status = status.strip().upper()

    if process_code:
        process_code = process_code.strip().upper()

    if action_type not in ALLOWED_ACTION_TYPES:
        raise ValueError(
            "Type d'action invalide."
        )

    if scope not in ALLOWED_SCOPES:
        raise ValueError(
            "Portée d'action invalide."
        )

    if priority not in ALLOWED_PRIORITIES:
        raise ValueError(
            "Priorité invalide."
        )

    if status not in ALLOWED_STATUSES:
        raise ValueError(
            "Statut d'action invalide."
        )

    # ----------------------------------------------------
    # ACTION LOCALE / CHANTIER
    # ----------------------------------------------------

    if scope == "LOCAL":
        process_code = None

        if progress_percent is None:
            progress_percent = 0

    # ----------------------------------------------------
    # ACTION GLOBALE / SUIVI 9001
    # ----------------------------------------------------

    if scope == "GLOBAL":
        if process_code not in ALLOWED_PROCESS_CODES:
            raise ValueError(
                "Une action globale doit être liée "
                "à un processus PR01 à PR08."
            )

        # Le pilotage de l'avancement est réalisé
        # dans le tableau de suivi 9001.
        progress_percent = None

    return {
        "action_type": action_type,
        "scope": scope,
        "process_code": process_code,
        "priority": priority,
        "status": status,
        "progress_percent": progress_percent,
    }


# ========================================================
# CRÉATION DEPUIS UN ÉVÉNEMENT
# ========================================================

def create_event_action(
    db: Session,
    event_id: int,
    data: ActionCreate,
    created_by_person_id: int | None,
) -> Action:
    _ensure_event_exists(db, event_id)

    _ensure_person_exists(
        db,
        data.responsible_person_id,
    )

    description = data.description.strip()

    if not description:
        raise ValueError(
            "La description de l'action est obligatoire."
        )

    values = _validate_action_values(
        action_type=data.action_type,
        scope=data.scope,
        process_code=data.process_code,
        priority=data.priority,
        status="TODO",
        progress_percent=data.progress_percent,
    )

    action = Action(
        origin_type="ACCIDENT",
        event_id=event_id,
        description=description,
        responsible_person_id=data.responsible_person_id,
        responsible_text=(
            data.responsible_text.strip()
            if data.responsible_text
            else None
        ),
        due_date=data.due_date,
        resources=data.resources,
        follow_up_indicator=data.follow_up_indicator,
        created_by_person_id=created_by_person_id,
        **values,
    )

    db.add(action)
    db.flush()

    return action


# ========================================================
# LECTURE
# ========================================================

# ========================================================
# LECTURE TRANSVERSE
# ========================================================

# ========================================================
# LECTURE TRANSVERSE
# ========================================================

def get_actions(
    db: Session,
    *,
    origin_type: str | None = None,
    status: str | None = None,
    responsible_person_id: int | None = None,
) -> list[tuple[Action, str | None]]:
    statement = (
        select(
            Action,
            models.Event.event_number,
        )
        .outerjoin(
            models.Event,
            Action.event_id == models.Event.id,
        )
    )

    # ----------------------------------------------------
    # ORIGINE
    # ----------------------------------------------------

    if origin_type:
        origin_type = origin_type.strip().upper()

        statement = statement.where(
            Action.origin_type == origin_type
        )

    # ----------------------------------------------------
    # STATUT
    # ----------------------------------------------------

    if status:
        status = status.strip().upper()

        if status not in ALLOWED_STATUSES:
            raise ValueError(
                "Statut d'action invalide."
            )

        statement = statement.where(
            Action.status == status
        )

    # ----------------------------------------------------
    # RESPONSABLE
    # ----------------------------------------------------

    if responsible_person_id is not None:
        statement = statement.where(
            Action.responsible_person_id ==
            responsible_person_id
        )

    # ----------------------------------------------------
    # TRI
    # ----------------------------------------------------

    statement = statement.order_by(
        Action.due_date.asc(),
        Action.created_at.asc(),
        Action.id.asc(),
    )

    rows = db.execute(statement).all()

    return [
        (
            action,
            event_number,
        )
        for action, event_number in rows
    ]

def get_event_actions(
    db: Session,
    event_id: int,
) -> list[Action]:
    _ensure_event_exists(db, event_id)

    statement = (
        select(Action)
        .where(Action.event_id == event_id)
        .order_by(
            Action.created_at.asc(),
            Action.id.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_action(
    db: Session,
    action_id: int,
) -> Action:
    action = db.get(Action, action_id)

    if not action:
        raise ValueError("Action introuvable.")

    return action


# ========================================================
# MODIFICATION
# ========================================================

def update_action(
    db: Session,
    action_id: int,
    data: ActionUpdate,
) -> Action:
    action = get_action(db, action_id)

    changes = data.model_dump(
        exclude_unset=True,
    )

    if "responsible_person_id" in changes:
        _ensure_person_exists(
            db,
            changes["responsible_person_id"],
        )

    description = changes.get(
        "description",
        action.description,
    )

    if description is None or not description.strip():
        raise ValueError(
            "La description de l'action est obligatoire."
        )

    action_type = changes.get(
        "action_type",
        action.action_type,
    )

    scope = changes.get(
        "scope",
        action.scope,
    )

    process_code = changes.get(
        "process_code",
        action.process_code,
    )

    priority = changes.get(
        "priority",
        action.priority,
    )

    status = changes.get(
        "status",
        action.status,
    )

    progress_percent = changes.get(
        "progress_percent",
        action.progress_percent,
    )

    values = _validate_action_values(
        action_type=action_type,
        scope=scope,
        process_code=process_code,
        priority=priority,
        status=status,
        progress_percent=progress_percent,
    )

    # ----------------------------------------------------
    # CHAMPS SIMPLES
    # ----------------------------------------------------

    simple_fields = {
        "responsible_person_id",
        "responsible_text",
        "due_date",
        "resources",
        "follow_up_indicator",
    }

    for field in simple_fields:
        if field in changes:
            value = changes[field]

            if (
                isinstance(value, str)
                and value.strip() == ""
            ):
                value = None

            setattr(action, field, value)

    action.description = description.strip()

    # ----------------------------------------------------
    # VALEURS MÉTIER NORMALISÉES
    # ----------------------------------------------------

    for field, value in values.items():
        setattr(action, field, value)

    db.flush()

    return action