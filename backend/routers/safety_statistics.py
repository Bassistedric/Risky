from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select

from .. import models
from ..database import SessionLocal
from ..schemas.safety_statistics import (
    SafetyPermanentDisabilityCreate,
    SafetyTargetUpsert,
    SafetyWorkHoursUpsert,
)
from ..services.safety_statistics import (
    build_statistics_summary,
    build_work_hours_dimension_key,
)
from ..services.accidentology_statistics import (
    build_accidentology_summary,
)
from ..services.safety_hours_import import (
    parse_rh_work_hours,
)
from ..services.audit import write_audit_log
from ..services.session import require_write_session


router = APIRouter(
    prefix="/safety-statistics",
    tags=["Safety Statistics"],
)

# ============================================================
# SYNTHÈSE STATISTIQUE
# ============================================================

@router.get("/summary")
def get_statistics_summary(
    organization_id: int,
    year: int,
    month_to: int | None = None,
    trade_code: str | None = None,
):
    db = SessionLocal()

    try:
        try:
            return build_statistics_summary(
                db,
                organization_id=organization_id,
                year=year,
                month_to=month_to,
                trade_code=trade_code,
            )

        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            )

    finally:
        db.close()

# ============================================================
# ANALYSE ACCIDENTOLOGIQUE
# ============================================================

@router.get("/accidentology")
def get_accidentology_statistics(
    organization_id: int,
    year: int,
    month_to: int = 12,
    trade_code: str | None = None,
    language: str = "fr",
):
    db = SessionLocal()

    try:
        try:
            return build_accidentology_summary(
                db,
                organization_id=organization_id,
                year=year,
                month_to=month_to,
                trade_code=trade_code,
                language=language,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc
    finally:
        db.close()


# ============================================================
# RÉFÉRENTIEL MÉTIERS
# ============================================================

@router.get("/trades")
def list_trades():
    db = SessionLocal()

    try:
        trades = db.scalars(
            select(models.TradeReference)
            .where(
                models.TradeReference.active.is_(True)
            )
            .order_by(
                models.TradeReference.name
            )
        ).all()

        return [
            {
                "id": trade.id,
                "code": trade.code,
                "name": trade.name,
            }
            for trade in trades
        ]

    finally:
        db.close()


# ============================================================
# IMPORT RH — APERÇU
# ============================================================

@router.post("/work-hours/import/preview")
async def preview_work_hours_import(
    file: UploadFile = File(...),
    session=Depends(require_write_session),
):
    try:
        content = await file.read()

        return parse_rh_work_hours(
            content,
            file.filename or "import.xlsx",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ============================================================
# IMPORT RH — APPLICATION
# ============================================================

@router.post("/work-hours/import/apply")
async def apply_work_hours_import(
    file: UploadFile = File(...),
    session=Depends(require_write_session),
):
    try:
        content = await file.read()
        preview = parse_rh_work_hours(
            content,
            file.filename or "import.xlsx",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    db = SessionLocal()

    try:
        organizations = {}

        for entity in preview["entities"]:
            code = entity[
                "organization_code"
            ]

            organization = db.scalar(
                select(models.Organization)
                .where(
                    models.Organization.code
                    == code,
                    models.Organization.active.is_(
                        True
                    ),
                )
            )

            if not organization:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Organisation RISKY "
                        f"introuvable : {code}"
                    ),
                )

            organizations[
                code
            ] = organization

        changed = 0

        for source_row in preview["rows"]:
            organization = organizations[
                source_row[
                    "organization_code"
                ]
            ]

            for (
                category,
                hours_key,
            ) in (
                (
                    "WORKER",
                    "worker_hours",
                ),
                (
                    "EMPLOYEE",
                    "employee_hours",
                ),
            ):
                dimension_key = (
                    build_work_hours_dimension_key(
                        workforce_category=category,
                    )
                )

                existing = db.scalar(
                    select(
                        models.SafetyWorkHours
                    )
                    .where(
                        models.SafetyWorkHours.organization_id
                        == organization.id,
                        models.SafetyWorkHours.year
                        == source_row["year"],
                        models.SafetyWorkHours.month
                        == source_row["month"],
                        models.SafetyWorkHours.dimension_key
                        == dimension_key,
                    )
                )

                if not existing:
                    existing = (
                        models.SafetyWorkHours(
                            organization_id=(
                                organization.id
                            ),
                            year=source_row[
                                "year"
                            ],
                            month=source_row[
                                "month"
                            ],
                            workforce_category=(
                                category
                            ),
                            trade_id=None,
                            dimension_key=(
                                dimension_key
                            ),
                        )
                    )

                    db.add(existing)

                existing.workforce_category = (
                    category
                )
                existing.trade_id = None
                existing.worked_hours = (
                    source_row[
                        hours_key
                    ]
                )
                existing.source = (
                    "RH Excel - "
                    + preview["filename"]
                )

                changed += 1

        write_audit_log(
            db=db,
            session=session,
            action="IMPORT",
            entity_type=(
                "SAFETY_WORK_HOURS"
            ),
            entity_id=(
                f'{preview["year"]}:'
                f'{preview["month_to"]}'
            ),
            after_data={
                "filename":
                    preview["filename"],
                "year":
                    preview["year"],
                "month_to":
                    preview["month_to"],
                "record_count":
                    changed,
            },
            details=(
                "Import des heures prestées "
                "depuis le fichier mensuel RH"
            ),
        )

        db.commit()

        return {
            "status": "ok",
            "filename":
                preview["filename"],
            "year": preview["year"],
            "month_to":
                preview["month_to"],
            "records_written":
                changed,
            "entities":
                preview["entities"],
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# HEURES PRESTÉES — ENCODAGE / MODIFICATION
# ============================================================

@router.put("/work-hours")
def upsert_work_hours(
    data: SafetyWorkHoursUpsert,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        organization = db.get(
            models.Organization,
            data.organization_id,
        )

        if not organization:
            raise HTTPException(
                status_code=404,
                detail="Organisation introuvable",
            )

        if data.year < 2000 or data.year > 2100:
            raise HTTPException(
                status_code=400,
                detail="Année invalide",
            )

        if data.month < 1 or data.month > 12:
            raise HTTPException(
                status_code=400,
                detail="Mois invalide",
            )

        if data.worked_hours < 0:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Les heures prestées "
                    "ne peuvent pas être négatives"
                ),
            )

        category = (
            data.workforce_category
            .strip()
            .upper()
        )

        if category not in {
            "WORKER",
            "EMPLOYEE",
        }:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Population invalide : "
                    "WORKER ou EMPLOYEE attendu"
                ),
            )

        dimension_key = (
            build_work_hours_dimension_key(
                workforce_category=category,
            )
        )

        existing = db.scalar(
            select(models.SafetyWorkHours)
            .where(
                models.SafetyWorkHours.organization_id
                == data.organization_id,
                models.SafetyWorkHours.year
                == data.year,
                models.SafetyWorkHours.month
                == data.month,
                models.SafetyWorkHours.dimension_key
                == dimension_key,
            )
        )

        if existing:
            row = existing
            row.workforce_category = category
            row.trade_id = None
            row.worked_hours = data.worked_hours
            row.source = data.source

        else:
            row = models.SafetyWorkHours(
                organization_id=data.organization_id,
                year=data.year,
                month=data.month,
                workforce_category=category,
                trade_id=None,
                dimension_key=dimension_key,
                worked_hours=data.worked_hours,
                source=data.source,
            )

            db.add(row)

        db.commit()
        db.refresh(row)

        return {
            "status": "ok",
            "id": row.id,
            "organization_id": row.organization_id,
            "year": row.year,
            "month": row.month,
            "workforce_category": (
                row.workforce_category
            ),
            "trade_id": row.trade_id,
            "dimension_key": row.dimension_key,
            "worked_hours": row.worked_hours,
            "source": row.source,
        }

    finally:
        db.close()


# ============================================================
# HEURES PRESTÉES — CONSULTATION
# ============================================================

@router.get("/work-hours")
def list_work_hours(
    organization_id: int,
    year: int,
):
    db = SessionLocal()

    try:
        rows = db.scalars(
            select(models.SafetyWorkHours)
            .where(
                models.SafetyWorkHours.organization_id
                == organization_id,
                models.SafetyWorkHours.year
                == year,
            )
            .order_by(
                models.SafetyWorkHours.month,
                models.SafetyWorkHours.dimension_key,
            )
        ).all()

        return [
            {
                "id": row.id,
                "organization_id": (
                    row.organization_id
                ),
                "year": row.year,
                "month": row.month,
                "workforce_category": (
                    row.workforce_category
                ),
                "trade_id": row.trade_id,
                "trade_code": (
                    row.trade.code
                    if row.trade
                    else None
                ),
                "worked_hours": row.worked_hours,
                "source": row.source,
            }
            for row in rows
        ]

    finally:
        db.close()


# ============================================================
# OBJECTIFS CFE — ENCODAGE / MODIFICATION
# ============================================================

@router.put("/targets")
def upsert_target(
    data: SafetyTargetUpsert,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        organization = db.get(
            models.Organization,
            data.organization_id,
        )

        if not organization:
            raise HTTPException(
                status_code=404,
                detail="Organisation introuvable",
            )

        if data.tf_target is not None:
            if data.tf_target < 0:
                raise HTTPException(
                    status_code=400,
                    detail="Objectif TF invalide",
                )

        if data.tg_target is not None:
            if data.tg_target < 0:
                raise HTTPException(
                    status_code=400,
                    detail="Objectif TG invalide",
                )

        target = db.scalar(
            select(models.SafetyTarget)
            .where(
                models.SafetyTarget.organization_id
                == data.organization_id,
                models.SafetyTarget.year
                == data.year,
            )
        )

        if target:
            target.tf_target = data.tf_target
            target.tg_target = data.tg_target
            target.source = data.source

        else:
            target = models.SafetyTarget(
                organization_id=(
                    data.organization_id
                ),
                year=data.year,
                tf_target=data.tf_target,
                tg_target=data.tg_target,
                source=data.source,
            )

            db.add(target)

        db.commit()
        db.refresh(target)

        return {
            "status": "ok",
            "id": target.id,
            "organization_id": (
                target.organization_id
            ),
            "year": target.year,
            "tf_target": target.tf_target,
            "tg_target": target.tg_target,
            "source": target.source,
        }

    finally:
        db.close()


@router.get("/targets")
def get_target(
    organization_id: int,
    year: int,
):
    db = SessionLocal()

    try:
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
                "organization_id": organization_id,
                "year": year,
                "tf_target": None,
                "tg_target": None,
            }

        return {
            "organization_id": target.organization_id,
            "year": target.year,
            "tf_target": target.tf_target,
            "tg_target": target.tg_target,
            "source": target.source,
        }

    finally:
        db.close()


# ============================================================
# INVALIDITÉS PERMANENTES
# ============================================================

@router.post("/permanent-disabilities")
def create_permanent_disability(
    data: SafetyPermanentDisabilityCreate,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        organization = db.get(
            models.Organization,
            data.organization_id,
        )

        if not organization:
            raise HTTPException(
                status_code=404,
                detail="Organisation introuvable",
            )

        if (
            data.disability_percent <= 0
            or data.disability_percent > 100
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Le taux d'invalidité doit "
                    "être supérieur à 0 et "
                    "inférieur ou égal à 100 %"
                ),
            )

        row = models.SafetyPermanentDisability(
            organization_id=data.organization_id,
            year=data.year,
            disability_percent=(
                data.disability_percent
            ),
            conventional_days=0,
            source=data.source,
        )

        db.add(row)
        db.commit()
        db.refresh(row)

        return {
            "status": "ok",
            "id": row.id,
            "organization_id": row.organization_id,
            "year": row.year,
            "disability_percent": (
                row.disability_percent
            ),
            "conventional_days": (
                row.conventional_days
            ),
            "source": row.source,
        }

    finally:
        db.close()


@router.get("/permanent-disabilities")
def list_permanent_disabilities(
    organization_id: int,
    year: int,
):
    db = SessionLocal()

    try:
        rows = db.scalars(
            select(
                models.SafetyPermanentDisability
            )
            .where(
                models.SafetyPermanentDisability.organization_id
                == organization_id,
                models.SafetyPermanentDisability.year
                == year,
            )
            .order_by(
                models.SafetyPermanentDisability.id
            )
        ).all()

        return [
            {
                "id": row.id,
                "organization_id": (
                    row.organization_id
                ),
                "year": row.year,
                "disability_percent": (
                    row.disability_percent
                ),
                "conventional_days": (
                    row.conventional_days
                ),
                "source": row.source,
            }
            for row in rows
        ]

    finally:
        db.close()


@router.delete(
    "/permanent-disabilities/{disability_id}"
)
def delete_permanent_disability(
    disability_id: int,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        row = db.get(
            models.SafetyPermanentDisability,
            disability_id,
        )

        if not row:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Invalidité permanente "
                    "introuvable"
                ),
            )

        db.delete(row)
        db.commit()

        return {
            "status": "deleted",
            "id": disability_id,
        }

    finally:
        db.close()