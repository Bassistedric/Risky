from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models


# ============================================================
# PÉRIMÈTRE ORGANISATIONNEL
# ============================================================

def get_descendant_organization_ids(
    db: Session,
    organization_id: int,
) -> list[int]:

    organizations = db.scalars(
        select(models.Organization)
        .where(
            models.Organization.active.is_(True)
        )
    ).all()

    children_by_parent: dict[
        Optional[int],
        list[int],
    ] = {}

    for organization in organizations:
        children_by_parent.setdefault(
            organization.parent_id,
            [],
        ).append(
            organization.id
        )

    result: list[int] = []
    pending = [organization_id]

    while pending:
        current_id = pending.pop()

        if current_id in result:
            continue

        result.append(current_id)

        pending.extend(
            children_by_parent.get(
                current_id,
                [],
            )
        )

    return result


# ============================================================
# FILTRE MÉTIER TRANSVERSAL
# ============================================================

def get_trade_organization_ids(
    db: Session,
    scope_organization_id: int,
    trade_code: str,
) -> list[int]:

    scope_ids = get_descendant_organization_ids(
        db,
        scope_organization_id,
    )

    trade = db.scalar(
        select(models.TradeReference)
        .where(
            models.TradeReference.code
            == trade_code.upper(),
            models.TradeReference.active.is_(True),
        )
    )

    if not trade:
        return []

    organization_ids = db.scalars(
        select(
            models.OrganizationTrade.organization_id
        )
        .where(
            models.OrganizationTrade.trade_id
            == trade.id,
            models.OrganizationTrade.organization_id.in_(
                scope_ids
            ),
        )
    ).all()

    return list(
        dict.fromkeys(
            organization_ids
        )
    )


# ============================================================
# RÉSOLUTION DU PÉRIMÈTRE
# ============================================================

def resolve_statistics_scope(
    db: Session,
    organization_id: int,
    trade_code: Optional[str] = None,
) -> list[int]:

    organization = db.get(
        models.Organization,
        organization_id,
    )

    if not organization:
        raise ValueError(
            "Organisation introuvable"
        )

    if trade_code:
        return get_trade_organization_ids(
            db=db,
            scope_organization_id=organization_id,
            trade_code=trade_code,
        )

    return get_descendant_organization_ids(
        db=db,
        organization_id=organization_id,
    )


# ============================================================
# CALCULS INDICATEURS
# ============================================================

def calculate_tf(
    lost_time_accidents: int,
    worked_hours: float,
) -> Optional[float]:

    if worked_hours <= 0:
        return None

    return (
        lost_time_accidents
        * 1_000_000
        / worked_hours
    )


def calculate_tg(
    lost_days: int,
    worked_hours: float,
) -> Optional[float]:

    if worked_hours <= 0:
        return None

    return (
        lost_days
        * 1_000
        / worked_hours
    )


def calculate_tgg(
    conventional_days: float,
    worked_hours: float,
) -> Optional[float]:

    if worked_hours <= 0:
        return None

    return (
        conventional_days
        * 1_000
        / worked_hours
    )


# ============================================================
# PROJECTION FIN D'ANNÉE
# ============================================================

def calculate_year_end_projection(
    *,
    lost_time_accidents: int,
    lost_days: int,
    worked_hours: float,
    elapsed_months: int,
) -> dict:

    if (
        worked_hours <= 0
        or elapsed_months <= 0
    ):
        return {
            "projected_hours": None,
            "projected_tf": None,
            "projected_tg": None,
        }

    projected_hours = (
        worked_hours
        / elapsed_months
        * 12
    )

    return {
        "projected_hours": projected_hours,
        "projected_tf": calculate_tf(
            lost_time_accidents,
            projected_hours,
        ),
        "projected_tg": calculate_tg(
            lost_days,
            projected_hours,
        ),
    }


# ============================================================
# DIMENSION HEURES
# ============================================================

def build_work_hours_dimension_key(
    workforce_category: str,
    trade_code: Optional[str] = None,
) -> str:

    category = workforce_category.upper()

    if category == "EMPLOYEE":
        return "EMPLOYEE"

    if category == "WORKER":
        if not trade_code:
            raise ValueError(
                "Un métier est obligatoire "
                "pour les heures ouvriers"
            )

        return (
            f"WORKER:{trade_code.upper()}"
        )

    raise ValueError(
        "Population invalide : "
        "WORKER ou EMPLOYEE attendu"
    )


# ============================================================
# MOIS ÉCOULÉS
# ============================================================

def get_elapsed_months(
    year: int,
) -> int:

    now = datetime.now()

    if year < now.year:
        return 12

    if year > now.year:
        return 0

    return now.month