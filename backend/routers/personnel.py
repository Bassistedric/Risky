from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select

from ..database import SessionLocal
from .. import models
from ..schemas.personnel import PersonArchiveRequest

from ..services.session import require_write_session
from ..services.audit import write_audit_log

router = APIRouter(
    tags=["Personnel"],
)


# ============================================================
# ORGANISATIONS
# ============================================================

@router.post("/seed-organizations")
def seed_organizations(
    session=Depends(require_write_session),
):

    db = SessionLocal()

    try:
        existing = db.scalar(
            select(models.Organization).where(
                models.Organization.code == "VMA"
            )
        )

        if existing:
            return {
                "status": "already_exists",
            }

        vma = models.Organization(
            code="VMA",
            name="VMA",
            entity_type="group",
        )

        db.add(vma)
        db.flush()

        vma_sud = models.Organization(
            code="VMA_SUD",
            name="VMA Sud",
            entity_type="entity",
            parent_id=vma.id,
        )

        db.add(vma_sud)
        db.flush()

        db.add_all(
            [
                models.Organization(
                    code="HVAC",
                    name="HVAC",
                    entity_type="business",
                    parent_id=vma_sud.id,
                ),
                models.Organization(
                    code="REF",
                    name="REF",
                    entity_type="business",
                    parent_id=vma_sud.id,
                ),
                models.Organization(
                    code="ELEC",
                    name="ELEC",
                    entity_type="business",
                    parent_id=vma_sud.id,
                ),
            ]
        )

        db.commit()

        return {
            "status": "created",
        }

    finally:
        db.close()


@router.get("/organizations")
def list_organizations():
    db = SessionLocal()

    try:
        organizations = db.scalars(
            select(models.Organization).order_by(
                models.Organization.id
            )
        ).all()

        return [
            {
                "id": organization.id,
                "code": organization.code,
                "name": organization.name,
                "type": organization.entity_type,
                "parent_id": organization.parent_id,
                "active": organization.active,
            }
            for organization in organizations
        ]

    finally:
        db.close()


# ============================================================
# CATEGORIES DE PERSONNEL
# ============================================================

@router.post("/seed-person-categories")
def seed_person_categories(
    session=Depends(require_write_session),
):

    db = SessionLocal()

    try:
        categories = [
            (
                "CAT1",
                "Ligne hiérarchique / management opérationnel",
            ),
            (
                "CAT2",
                "Employés",
            ),
            (
                "CAT3",
                "Chefs d'équipe",
            ),
            (
                "CAT4",
                "Ouvriers",
            ),
        ]

        created = 0

        for code, name in categories:
            existing = db.scalar(
                select(models.PersonCategory).where(
                    models.PersonCategory.code == code
                )
            )

            if not existing:
                db.add(
                    models.PersonCategory(
                        code=code,
                        name=name,
                    )
                )

                created += 1

        db.commit()

        return {
            "status": "ok",
            "created": created,
        }

    finally:
        db.close()


@router.get("/person-categories")
def list_person_categories():
    db = SessionLocal()

    try:
        categories = db.scalars(
            select(models.PersonCategory).order_by(
                models.PersonCategory.id
            )
        ).all()

        return [
            {
                "id": category.id,
                "code": category.code,
                "name": category.name,
                "active": category.active,
            }
            for category in categories
        ]

    finally:
        db.close()


# ============================================================
# FONCTIONS
# ============================================================

@router.post("/seed-functions")
def seed_functions(
    session=Depends(require_write_session),
):

    db = SessionLocal()

    try:
        functions = [
            (
                "SITE_SUP",
                "Site Supervisor",
            ),
            (
                "PM",
                "Project Manager",
            ),
            (
                "APM",
                "Assistant Project Manager",
            ),
            (
                "OPM",
                "OPM",
            ),
            (
                "CE",
                "Chef d'équipe",
            ),
            (
                "EMP",
                "Employé",
            ),
            (
                "OUV",
                "Ouvrier",
            ),
        ]

        created = 0

        for code, name in functions:
            existing = db.scalar(
                select(models.Function).where(
                    models.Function.code == code
                )
            )

            if not existing:
                db.add(
                    models.Function(
                        code=code,
                        name=name,
                    )
                )

                created += 1

        db.commit()

        return {
            "status": "ok",
            "created": created,
        }

    finally:
        db.close()


@router.get("/functions")
def list_functions():
    db = SessionLocal()

    try:
        functions = db.scalars(
            select(models.Function).order_by(
                models.Function.id
            )
        ).all()

        return [
            {
                "id": function.id,
                "code": function.code,
                "name": function.name,
                "active": function.active,
            }
            for function in functions
        ]

    finally:
        db.close()


# ============================================================
# PERSONNES
# ============================================================

@router.post("/seed-person")
def seed_person(
    session=Depends(require_write_session),
):

    db = SessionLocal()

    try:
        existing = db.scalar(
            select(models.Person).where(
                models.Person.employee_number == "0001"
            )
        )

        if existing:
            return {
                "status": "already_exists",
                "person_id": existing.id,
            }

        category = db.scalar(
            select(models.PersonCategory).where(
                models.PersonCategory.code == "CAT1"
            )
        )

        function = db.scalar(
            select(models.Function).where(
                models.Function.code == "PM"
            )
        )

        organization = db.scalar(
            select(models.Organization).where(
                models.Organization.code == "VMA_SUD"
            )
        )

        person = models.Person(
            employee_number="0001",
            last_name="DEMO",
            first_name="Jean",
            email="jean.demo@example.com",
            function_id=(
                function.id
                if function
                else None
            ),
            category_id=(
                category.id
                if category
                else None
            ),
            organization_id=(
                organization.id
                if organization
                else None
            ),
            status="ACTIVE",
        )

        db.add(person)
        db.commit()
        db.refresh(person)

        return {
            "status": "created",
            "person_id": person.id,
        }

    finally:
        db.close()


@router.get("/people")
def list_people(
    status: str = "ACTIVE",
):
    db = SessionLocal()

    try:
        query = select(
            models.Person
        ).order_by(
            models.Person.id
        )

        if status != "ALL":
            query = query.where(
                models.Person.status == status
            )

        people = db.scalars(
            query
        ).all()

        return [
            {
                "id": person.id,
                "employee_number": person.employee_number,
                "initials": person.initials,
                "last_name": person.last_name,
                "first_name": person.first_name,
                "email": person.email,
                "function": (
                    person.function.name
                    if person.function
                    else None
                ),
                "category": (
                    person.category.code
                    if person.category
                    else None
                ),
                "organization": (
                    person.organization.name
                    if person.organization
                    else None
                ),
                "manager": (
                    (
                        f"{person.manager.first_name} "
                        f"{person.manager.last_name}"
                    )
                    if person.manager
                    else None
                ),
                "status": person.status,
                "archive_reason": person.archive_reason,
                "archived_at": person.archived_at,
            }
            for person in people
        ]

    finally:
        db.close()


@router.post("/people/{person_id}/archive")
def archive_person(
    person_id: int,
    data: PersonArchiveRequest,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        person = db.get(
            models.Person,
            person_id,
        )

        if not person:
            return {
                "status": "not_found",
                "person_id": person_id,
            }

        if person.status == "ARCHIVED":
            return {
                "status": "already_archived",
                "person_id": person.id,
            }

        before_data = {
            "status": person.status,
            "archive_reason": person.archive_reason,
            "archived_at": person.archived_at,
        }

        person.status = "ARCHIVED"
        person.archive_reason = data.reason
        person.archived_at = datetime.now()

        write_audit_log(
            db=db,
            session=session,
            action="ARCHIVE",
            entity_type="PERSON",
            entity_id=person.id,
            before_data=before_data,
            after_data={
                "status": person.status,
                "archive_reason": person.archive_reason,
                "archived_at": person.archived_at,
            },
            details="Archivage d'une personne",
        )

        db.commit()
        db.refresh(person)

        return {
            "status": "archived",
            "person_id": person.id,
            "archive_reason": person.archive_reason,
            "archived_at": person.archived_at,
        }

    finally:
        db.close()


@router.post("/people/{person_id}/reactivate")
def reactivate_person(
    person_id: int,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        person = db.get(
            models.Person,
            person_id,
        )

        if not person:
            return {
                "status": "not_found",
                "person_id": person_id,
            }

        if person.status == "ACTIVE":
            return {
                "status": "already_active",
                "person_id": person.id,
            }

        before_data = {
            "status": person.status,
            "archive_reason": person.archive_reason,
            "archived_at": person.archived_at,
        }

        person.status = "ACTIVE"
        person.archive_reason = None
        person.archived_at = None

        write_audit_log(
            db=db,
            session=session,
            action="REACTIVATE",
            entity_type="PERSON",
            entity_id=person.id,
            before_data=before_data,
            after_data={
                "status": person.status,
                "archive_reason": person.archive_reason,
                "archived_at": person.archived_at,
            },
            details="Réactivation d'une personne",
        )

        db.commit()
        db.refresh(person)

        return {
            "status": "reactivated",
            "person_id": person.id,
        }

    finally:
        db.close()

@router.get("/people/{person_id}/360")
def get_person_360(person_id: int):
    db = SessionLocal()

    try:
        person = db.get(models.Person, person_id)

        if not person:
            return {
                "status": "error",
                "message": "Personne introuvable",
            }

        # ----------------------------------------------------
        # COMPETENCES
        # ----------------------------------------------------

        person_competencies = db.scalars(
            select(models.PersonCompetency)
            .where(
                models.PersonCompetency.person_id == person_id
            )
            .order_by(models.PersonCompetency.id.asc())
        ).all()

        competencies = []

        for pc in person_competencies:
            competency = pc.competency

            competencies.append(
                {
                    "person_competency_id": pc.id,
                    "competency_id": competency.id,
                    "code": competency.code,
                    "name": competency.name,
                    "validation_status": pc.validation_status,
                    "obtained_at": pc.obtained_at,
                    "provider": pc.provider,
                    "certificate_reference": pc.certificate_reference,
                    "comment": pc.comment,
                }
            )

        # ----------------------------------------------------
        # HABILITATION ACTIVE
        # ----------------------------------------------------

        current_authorization = db.scalar(
            select(models.Authorization)
            .where(
                models.Authorization.person_id == person_id,
                models.Authorization.status == "ACTIVE",
            )
            .order_by(models.Authorization.issued_at.desc())
        )

        authorization_data = None

        if current_authorization:
            authorization_data = {
                "id": current_authorization.id,
                "cycle": {
                    "id": current_authorization.cycle.id,
                    "code": current_authorization.cycle.code,
                    "name": current_authorization.cycle.name,
                    "start_date": current_authorization.cycle.start_date,
                    "end_date": current_authorization.cycle.end_date,
                },
                "issued_at": current_authorization.issued_at,
                "status": current_authorization.status,
                "competencies": [
                    {
                        "id": item.competency.id,
                        "code": item.competency.code,
                        "name": item.competency.name,
                    }
                    for item in current_authorization.competencies
                ],
            }

        # ----------------------------------------------------
        # HISTORIQUE HABILITATIONS
        # ----------------------------------------------------

        authorizations = db.scalars(
            select(models.Authorization)
            .where(
                models.Authorization.person_id == person_id
            )
            .order_by(models.Authorization.issued_at.desc())
        ).all()

        authorization_history = [
            {
                "id": authorization.id,
                "cycle_code": authorization.cycle.code,
                "issued_at": authorization.issued_at,
                "status": authorization.status,
                "competency_count": len(
                    authorization.competencies
                ),
            }
            for authorization in authorizations
        ]

        # ----------------------------------------------------
        # ACCIDENTS / INCIDENTS - 3 DERNIERES ANNEES
        # ----------------------------------------------------

        three_years_ago = datetime.now().replace(
            year=datetime.now().year - 3
        )

        events_3_years = db.scalars(
            select(models.Event)
            .where(
                models.Event.person_id == person_id,
                models.Event.event_date >= three_years_ago,
            )
            .order_by(models.Event.event_date.desc())
        ).all()

        accident_events = [
            event
            for event in events_3_years
            if event.event_type == "ACCIDENT"
        ]

        total_lost_days = sum(
            event.lost_days
            for event in accident_events
        )

        accidents_data = [
            {
                "id": event.id,
                "event_number": event.event_number,
                "event_date": event.event_date,
                "event_type": event.event_type,
                "location": event.location,
                "description": event.description,
                "lost_time": event.lost_time,
                "lost_days": event.lost_days,
                "status": event.status,
            }
            for event in accident_events
        ]

        # ----------------------------------------------------
        # SYNTHESE
        # ----------------------------------------------------

        validated_count = sum(
            1
            for pc in person_competencies
            if pc.validation_status == "VALIDATED"
        )

        suspended_count = sum(
            1
            for pc in person_competencies
            if pc.validation_status == "SUSPENDED"
        )

        revoked_count = sum(
            1
            for pc in person_competencies
            if pc.validation_status == "REVOKED"
        )

        return {
            "person": {
                "id": person.id,
                "employee_number": person.employee_number,
                "last_name": person.last_name,
                "first_name": person.first_name,
                "email": person.email,
                "status": person.status,
            },

            "summary": {
                "competencies_total": len(person_competencies),
                "competencies_validated": validated_count,
                "competencies_suspended": suspended_count,
                "competencies_revoked": revoked_count,
                "authorization_active": (
                    current_authorization is not None
                ),
                "authorization_versions": len(authorizations),
                "accidents_3_years": len(accident_events),
                "lost_days_3_years": total_lost_days,
            },

            "competencies": competencies,

            "current_authorization": authorization_data,

            "authorization_history": authorization_history,

            "accidents_3_years": {
                "count": len(accident_events),
                "lost_days": total_lost_days,
                "events": accidents_data,
            },

            "future_modules": {
                "ilt": None,
                "toolbox": None,
                "actions": None,
            },
        }

    finally:
        db.close()