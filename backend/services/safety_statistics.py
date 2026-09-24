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
# RÉFÉRENTIEL MÉTIER
# ============================================================

def get_trade_by_code(
    db: Session,
    trade_code: str,
) -> Optional[models.TradeReference]:

    return db.scalar(
        select(models.TradeReference)
        .where(
            models.TradeReference.code
            == trade_code.upper(),
            models.TradeReference.active.is_(True),
        )
    )


# ============================================================
# FILTRE MÉTIER — ÉVÉNEMENTS
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

    trade = get_trade_by_code(
        db,
        trade_code,
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
# RÉSOLUTION PÉRIMÈTRE ÉVÉNEMENTS
# ============================================================

def resolve_event_scope(
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
# RÉSOLUTION PÉRIMÈTRE HEURES
# ============================================================

def resolve_hours_scope(
    db: Session,
    organization_id: int,
) -> list[int]:

    organization = db.get(
        models.Organization,
        organization_id,
    )

    if not organization:
        raise ValueError(
            "Organisation introuvable"
        )

    # Si le périmètre sélectionné est un métier,
    # les heures sont encodées au niveau de son parent.
    if (
        organization.entity_type == "TRADE"
        and organization.parent_id is not None
    ):
        return [
            organization.parent_id
        ]

    scope_ids = get_descendant_organization_ids(
        db,
        organization_id,
    )

    # On ne conserve pas les nœuds TRADE pour les heures :
    # elles sont enregistrées au niveau des entités.
    organizations = db.scalars(
        select(models.Organization)
        .where(
            models.Organization.id.in_(
                scope_ids
            )
        )
    ).all()

    return [
        organization.id
        for organization in organizations
        if organization.entity_type != "TRADE"
    ]


# ============================================================
# MÉTIER IMPLICITE D'UN NŒUD TRADE
# ============================================================

def get_organization_trade_code(
    db: Session,
    organization_id: int,
) -> Optional[str]:

    organization = db.get(
        models.Organization,
        organization_id,
    )

    if (
        not organization
        or organization.entity_type != "TRADE"
    ):
        return None

    trade = db.scalar(
        select(models.TradeReference)
        .join(
            models.OrganizationTrade,
            models.OrganizationTrade.trade_id
            == models.TradeReference.id,
        )
        .where(
            models.OrganizationTrade.organization_id
            == organization_id,
            models.TradeReference.active.is_(True),
        )
    )

    if not trade:
        return None

    return trade.code


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
    """
    Les heures RH officielles ne sont pas ventilées
    par métier. La dimension statistique est donc
    uniquement WORKER ou EMPLOYEE.

    trade_code reste dans la signature pour conserver
    la compatibilité avec d'anciens appels, mais il
    n'entre plus dans la clé.
    """

    category = workforce_category.upper()

    if category in {
        "WORKER",
        "EMPLOYEE",
    }:
        return category

    raise ValueError(
        "Population invalide : "
        "WORKER ou EMPLOYEE attendu"
    )


# ============================================================
# MOIS ÉCOULÉS
# ============================================================

def get_elapsed_months(
    year: int,
    month_to: Optional[int] = None,
) -> int:

    if month_to is not None:
        return month_to

    now = datetime.now()

    if year < now.year:
        return 12

    if year > now.year:
        return 0

    return now.month


# ============================================================
# HEURES — AGRÉGATION
# ============================================================

def get_month_worked_hours(
    db: Session,
    *,
    organization_id: int,
    year: int,
    month: int,
    trade_code: Optional[str] = None,
) -> float:

    organization = db.get(
        models.Organization,
        organization_id,
    )

    if not organization:
        raise ValueError(
            "Organisation introuvable"
        )

    # Les heures RH sont officielles au niveau
    # organisationnel et population (ouvriers/employés).
    # Le métier reste une dimension d'analyse des événements
    # mais ne modifie jamais le dénominateur TF/TG/TGG.
    scope_ids = resolve_hours_scope(
        db,
        organization_id,
    )

    query = (
        select(models.SafetyWorkHours)
        .where(
            models.SafetyWorkHours.organization_id.in_(
                scope_ids
            ),
            models.SafetyWorkHours.year == year,
            models.SafetyWorkHours.month == month,
        )
    )

    rows = db.scalars(query).all()

    return sum(
        row.worked_hours
        for row in rows
        if row.dimension_key in {
            "WORKER",
            "EMPLOYEE",
        }
    )


# ============================================================
# ÉVÉNEMENTS — AGRÉGATION MENSUELLE
# ============================================================

def get_month_event_metrics(
    db: Session,
    *,
    organization_id: int,
    year: int,
    month: int,
    trade_code: Optional[str] = None,
) -> dict:

    organization = db.get(
        models.Organization,
        organization_id,
    )

    if not organization:
        raise ValueError(
            "Organisation introuvable"
        )

    effective_trade_code = (
        trade_code
        or get_organization_trade_code(
            db,
            organization_id,
        )
    )

    scope_ids = resolve_event_scope(
        db=db,
        organization_id=organization_id,
        trade_code=effective_trade_code,
    )

    if not scope_ids:
        return {
            "accidents_with_lost_time": 0,
            "accidents_without_lost_time": 0,
            "lost_days": 0,
            "incidents": 0,
            "near_misses": 0,
        }

    events = db.scalars(
        select(models.Event)
        .where(
            models.Event.organization_id.in_(
                scope_ids
            ),
            models.Event.event_date
            >= datetime(
                year,
                month,
                1,
            ),
            models.Event.event_date
            < (
                datetime(
                    year + 1,
                    1,
                    1,
                )
                if month == 12
                else datetime(
                    year,
                    month + 1,
                    1,
                )
            ),
        )
    ).all()

    accidents = [
        event
        for event in events
        if event.event_type == "ACCIDENT"
    ]

    return {
        "accidents_with_lost_time": sum(
            1
            for event in accidents
            if event.lost_time
        ),
        "accidents_without_lost_time": sum(
            1
            for event in accidents
            if not event.lost_time
        ),
        "lost_days": sum(
            event.lost_days
            for event in accidents
        ),
        "incidents": sum(
            1
            for event in events
            if event.event_type == "INCIDENT"
        ),
        "near_misses": sum(
            1
            for event in events
            if event.event_type == "NEAR_MISS"
        ),
    }


# ============================================================
# JOURS CONVENTIONNELS
# ============================================================

def get_conventional_days(
    db: Session,
    *,
    organization_id: int,
    year: int,
) -> float:

    scope_ids = get_descendant_organization_ids(
        db,
        organization_id,
    )

    rows = db.scalars(
        select(
            models.SafetyPermanentDisability
        )
        .where(
            models.SafetyPermanentDisability.organization_id.in_(
                scope_ids
            ),
            models.SafetyPermanentDisability.year
            == year,
        )
    ).all()

    return sum(
        row.conventional_days
        for row in rows
    )


# ============================================================
# OBJECTIFS CFE
# ============================================================

def get_safety_target(
    db: Session,
    *,
    organization_id: int,
    year: int,
) -> dict:

    target = db.scalar(
        select(models.SafetyTarget)
        .where(
            models.SafetyTarget.organization_id
            == organization_id,
            models.SafetyTarget.year
            == year,
        )
    )

    if not target:
        return {
            "tf_target": None,
            "tg_target": None,
        }

    return {
        "tf_target": target.tf_target,
        "tg_target": target.tg_target,
    }


# ============================================================
# SYNTHÈSE STATISTIQUE
# ============================================================

def build_statistics_summary(
    db: Session,
    *,
    organization_id: int,
    year: int,
    month_to: Optional[int] = None,
    trade_code: Optional[str] = None,
) -> dict:

    organization = db.get(
        models.Organization,
        organization_id,
    )

    if not organization:
        raise ValueError(
            "Organisation introuvable"
        )

    if year < 2000 or year > 2100:
        raise ValueError(
            "Année invalide"
        )

    effective_month_to = (
        month_to
        if month_to is not None
        else get_elapsed_months(year)
    )

    if (
        effective_month_to < 1
        or effective_month_to > 12
    ):
        raise ValueError(
            "Mois invalide"
        )

    # TF/TG/TGG utilisent toujours l'ensemble des événements
    # du périmètre organisationnel avec les heures RH officielles.
    # Le métier sera appliqué séparément aux analyses
    # accidentologiques (HEEPO, Fedris, causes, etc.).
    effective_trade_code = None

    monthly: list[dict] = []

    total_hours = 0.0
    total_with_lost_time = 0
    total_without_lost_time = 0
    total_lost_days = 0
    total_incidents = 0
    total_near_misses = 0

    cumulative_hours = 0.0
    cumulative_lost_time = 0
    cumulative_lost_days = 0

    for month in range(
        1,
        effective_month_to + 1,
    ):
        worked_hours = get_month_worked_hours(
            db,
            organization_id=organization_id,
            year=year,
            month=month,
            trade_code=effective_trade_code,
        )

        event_metrics = get_month_event_metrics(
            db,
            organization_id=organization_id,
            year=year,
            month=month,
            trade_code=effective_trade_code,
        )

        total_hours += worked_hours
        total_with_lost_time += (
            event_metrics[
                "accidents_with_lost_time"
            ]
        )
        total_without_lost_time += (
            event_metrics[
                "accidents_without_lost_time"
            ]
        )
        total_lost_days += (
            event_metrics["lost_days"]
        )
        total_incidents += (
            event_metrics["incidents"]
        )
        total_near_misses += (
            event_metrics["near_misses"]
        )

        cumulative_hours += worked_hours
        cumulative_lost_time += (
            event_metrics[
                "accidents_with_lost_time"
            ]
        )
        cumulative_lost_days += (
            event_metrics["lost_days"]
        )

        monthly.append(
            {
                "month": month,
                "worked_hours": worked_hours,
                "accidents_with_lost_time": (
                    event_metrics[
                        "accidents_with_lost_time"
                    ]
                ),
                "accidents_without_lost_time": (
                    event_metrics[
                        "accidents_without_lost_time"
                    ]
                ),
                "lost_days": (
                    event_metrics["lost_days"]
                ),
                "incidents": (
                    event_metrics["incidents"]
                ),
                "near_misses": (
                    event_metrics["near_misses"]
                ),
                "tf": calculate_tf(
                    event_metrics[
                        "accidents_with_lost_time"
                    ],
                    worked_hours,
                ),
                "tg": calculate_tg(
                    event_metrics["lost_days"],
                    worked_hours,
                ),
                "tf_ytd": calculate_tf(
                    cumulative_lost_time,
                    cumulative_hours,
                ),
                "tg_ytd": calculate_tg(
                    cumulative_lost_days,
                    cumulative_hours,
                ),
            }
        )

    conventional_days = get_conventional_days(
        db,
        organization_id=organization_id,
        year=year,
    )

    target = get_safety_target(
        db,
        organization_id=organization_id,
        year=year,
    )

    projection = calculate_year_end_projection(
        lost_time_accidents=(
            total_with_lost_time
        ),
        lost_days=total_lost_days,
        worked_hours=total_hours,
        elapsed_months=effective_month_to,
    )

    return {
        "scope": {
            "organization_id": (
                organization.id
            ),
            "organization_code": (
                organization.code
            ),
            "organization_name": (
                organization.name
            ),
            "organization_type": (
                organization.entity_type
            ),
            "trade_code": (
                effective_trade_code
            ),
        },
        "period": {
            "year": year,
            "month_to": effective_month_to,
        },
        "totals": {
            "worked_hours": total_hours,
            "accidents_with_lost_time": (
                total_with_lost_time
            ),
            "accidents_without_lost_time": (
                total_without_lost_time
            ),
            "lost_days": total_lost_days,
            "conventional_days": (
                conventional_days
            ),
            "incidents": total_incidents,
            "near_misses": total_near_misses,
        },
        "indicators": {
            "tf": calculate_tf(
                total_with_lost_time,
                total_hours,
            ),
            "tg": calculate_tg(
                total_lost_days,
                total_hours,
            ),
            "tgg": calculate_tgg(
                conventional_days,
                total_hours,
            ),
        },
        "targets": target,
        "projection": projection,
        "monthly": monthly,
    }