from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select

from ..database import SessionLocal
from .. import models

from ..services.session import require_write_session
from ..services.audit import write_audit_log

router = APIRouter(
    tags=["Habilitations"],
)

def create_next_authorization_cycle(db):
    """
    Crée le cycle collectif suivant sur base du cycle actif actuel.

    Exemple :
    2025-2029 -> 2030-2034
    """

    current_cycle = db.scalar(
        select(models.AuthorizationCycle)
        .where(models.AuthorizationCycle.active == True)
        .order_by(models.AuthorizationCycle.end_date.desc())
    )

    if not current_cycle:
        return {
            "status": "error",
            "message": "Aucun cycle actif trouvé",
        }

    next_start = current_cycle.end_date + timedelta(days=1)

    next_end = datetime(
        next_start.year + 5,
        1,
        1,
    ) - timedelta(days=1)

    next_code = (
        f"AUTH_{next_start.year}_{next_end.year}"
    )

    existing = db.scalar(
        select(models.AuthorizationCycle).where(
            models.AuthorizationCycle.code == next_code
        )
    )

    if existing:
        return {
            "status": "already_exists",
            "cycle_id": existing.id,
            "code": existing.code,
        }

    next_cycle = models.AuthorizationCycle(
        code=next_code,
        name=(
            f"Cycle d'habilitation "
            f"{next_start.year}-{next_end.year}"
        ),
        start_date=next_start,
        end_date=next_end,
        automatic_renewal=True,
        active=False,
    )

    db.add(next_cycle)
    db.flush()
    

    return {
        "status": "created",
        "cycle": {
            "id": next_cycle.id,
            "code": next_cycle.code,
            "name": next_cycle.name,
            "start_date": next_cycle.start_date,
            "end_date": next_cycle.end_date,
            "active": next_cycle.active,
        },
    }

@router.post("/authorization-cycles/create-next")
def create_next_authorization_cycle_route(
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        result = create_next_authorization_cycle(db)

        if result.get("status") != "created":
            return result

        cycle = result["cycle"]

        write_audit_log(
            db=db,
            session=session,
            action="CREATE",
            entity_type="AUTHORIZATION_CYCLE",
            entity_id=cycle["id"],
            after_data={
                "code": cycle["code"],
                "name": cycle["name"],
                "start_date": cycle["start_date"],
                "end_date": cycle["end_date"],
                "active": cycle["active"],
            },
            details="Création du cycle collectif d'habilitation",
        )

        db.commit()

        return result

    finally:
        db.close()

@router.post("/authorization-cycles/{cycle_id}/activate")
def activate_authorization_cycle(
    cycle_id: int,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        new_cycle = db.get(
            models.AuthorizationCycle,
            cycle_id,
        )

        if not new_cycle:
             return {
                "status": "error",
                "message": "Cycle introuvable",
            }

        if new_cycle.active:
            return {
                "status": "already_active",
                "cycle_id": new_cycle.id,
                "code": new_cycle.code,
            }

        now = datetime.now()

        if new_cycle.start_date > now:
            return {
                "status": "error",
                "message": "Ce cycle ne peut pas encore être activé",
                "cycle_id": new_cycle.id,
                "code": new_cycle.code,
                "start_date": new_cycle.start_date,
            }

        # Désactiver le ou les cycles actuellement actifs
        active_cycles = db.scalars(
            select(models.AuthorizationCycle).where(
                models.AuthorizationCycle.active == True
            )
        ).all()

        for cycle in active_cycles:
            cycle.active = False

        # Activer le nouveau cycle
        new_cycle.active = True

        # Personnes actives uniquement
        people = db.scalars(
            select(models.Person).where(
                models.Person.status == "ACTIVE"
            )
        ).all()

        created_authorizations = []

        for person in people:
            # Compétences générales actuellement VALIDATED
            person_competencies = db.scalars(
                select(models.PersonCompetency)
                .join(
                    models.Competency,
                    models.PersonCompetency.competency_id
                    == models.Competency.id,
                )
                .join(
                    models.ValidityRule,
                    models.Competency.validity_rule_id
                    == models.ValidityRule.id,
                )
                .where(
                    models.PersonCompetency.person_id == person.id,
                    models.PersonCompetency.validation_status
                    == "VALIDATED",
                    models.ValidityRule.code
                    == "GENERAL_AUTHORIZATION",
                )
            ).all()

            # Pas d'habilitation vide
            if not person_competencies:
                continue

            authorization = models.Authorization(
                person_id=person.id,
                cycle_id=new_cycle.id,
                issued_at=datetime.now(),
                status="ACTIVE",
                comment=f"Renouvellement collectif {new_cycle.code}",
            )

            db.add(authorization)
            db.flush()

            for person_competency in person_competencies:
                db.add(
                    models.AuthorizationCompetency(
                        authorization_id=authorization.id,
                        competency_id=person_competency.competency_id,
                    )
                )
                
            write_audit_log(
                db=db,
                session=session,
                action="CREATE",
                entity_type="AUTHORIZATION",
                entity_id=authorization.id,
                after_data={
                    "person_id": person.id,
                    "cycle_id": new_cycle.id,
                    "cycle_code": new_cycle.code,
                    "issued_at": authorization.issued_at,
                    "status": authorization.status,
                    "competency_ids": [
                        person_competency.competency_id
                        for person_competency
                        in person_competencies
                    ],
                    "generation_mode": "COLLECTIVE_RENEWAL",
                },
                details=(
                    "Création d'une habilitation "
                    "par renouvellement collectif"
                ),
            )

            created_authorizations.append(
                {
                    "authorization_id": authorization.id,
                    "person_id": person.id,
                    "employee_number": person.employee_number,
                }
            )

        write_audit_log(
            db=db,
            session=session,
            action="ACTIVATE",
            entity_type="AUTHORIZATION_CYCLE",
            entity_id=new_cycle.id,
            before_data={
                "active": False,
                "previous_active_cycles": [
                    {
                        "id": cycle.id,
                        "code": cycle.code,
                    }
                    for cycle in active_cycles
                ],
            },
            after_data={
                "active": True,
                "code": new_cycle.code,
                "start_date": new_cycle.start_date,
                "end_date": new_cycle.end_date,
                "created_authorizations": len(
                    created_authorizations
                ),
            },
            details=(
                f"Activation du cycle collectif "
                f"{new_cycle.code}"
            ),
        )

        db.commit()   
        

        return {
            "status": "activated",
            "cycle": {
                "id": new_cycle.id,
                "code": new_cycle.code,
                "start_date": new_cycle.start_date,
                "end_date": new_cycle.end_date,
                "active": new_cycle.active,
            },
            "authorizations_created": len(
                created_authorizations
            ),
            "people": created_authorizations,
        }

    finally:
        db.close()

@router.get("/authorization-cycles")
def list_authorization_cycles():
    db = SessionLocal()

    try:
        cycles = db.scalars(
            select(models.AuthorizationCycle).order_by(
                models.AuthorizationCycle.start_date
            )
        ).all()

        return [
            {
                "id": cycle.id,
                "code": cycle.code,
                "name": cycle.name,
                "start_date": cycle.start_date,
                "end_date": cycle.end_date,
                "automatic_renewal": cycle.automatic_renewal,
                "active": cycle.active,
            }
            for cycle in cycles
        ]

    finally:
        db.close()

@router.post("/people/{person_id}/authorizations")
def create_authorization(
    person_id: int,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        person = db.get(models.Person, person_id)

        if not person:
            return {
                "status": "error",
                "message": "Personne introuvable",
            }

        cycle = db.scalar(
            select(models.AuthorizationCycle).where(
                models.AuthorizationCycle.active == True
            )
        )

        if not cycle:
            return {
                "status": "error",
                "message": "Aucun cycle d'habilitation actif",
            }

        existing = db.scalar(
            select(models.Authorization).where(
                models.Authorization.person_id == person_id,
                models.Authorization.cycle_id == cycle.id,
                models.Authorization.status == "ACTIVE",
            )
        )

        if existing:
            return {
                "status": "already_exists",
                "authorization_id": existing.id,
            }

        person_competencies = db.scalars(
            select(models.PersonCompetency).where(
                models.PersonCompetency.person_id == person_id,
                models.PersonCompetency.validation_status == "VALIDATED",
            )
        ).all()

        eligible_competencies = [
            pc
            for pc in person_competencies
            if pc.competency.validity_rule
            and pc.competency.validity_rule.code
            == "GENERAL_AUTHORIZATION"
        ]

        if not eligible_competencies:
            return {
                "status": "error",
                "message": "Aucune compétence habilitable",
            }

        authorization = models.Authorization(
            person_id=person_id,
            cycle_id=cycle.id,
            issued_at=datetime.now(),
            status="ACTIVE",
        )

        db.add(authorization)
        db.flush()

        for pc in eligible_competencies:
            db.add(
                models.AuthorizationCompetency(
                    authorization_id=authorization.id,
                    competency_id=pc.competency_id,
                )
            )
        write_audit_log(
            db=db,
            session=session,
            action="CREATE",
            entity_type="AUTHORIZATION",
            entity_id=authorization.id,
            after_data={
                "person_id": person.id,
                "cycle_id": cycle.id,
                "cycle_code": cycle.code,
                "issued_at": authorization.issued_at,
                "status": authorization.status,
                "competencies": [
                    pc.competency.code
                    for pc in eligible_competencies
                ],
            },
            details="Création d'une habilitation",
        )

        db.commit()
        db.refresh(authorization)
        
        return {
            "status": "created",
            "authorization_id": authorization.id,
            "person": f"{person.first_name} {person.last_name}",
            "cycle": cycle.code,
            "valid_until": cycle.end_date,
            "competencies": [
                pc.competency.code
                for pc in eligible_competencies
            ],
        }

    finally:
        db.close()

@router.get("/authorizations/{authorization_id}")
def get_authorization(authorization_id: int):
    db = SessionLocal()

    try:
        authorization = db.get(
            models.Authorization,
            authorization_id,
        )

        if not authorization:
            return {
                "status": "error",
                "message": "Habilitation introuvable",
            }

        return {
            "id": authorization.id,
            "person": {
                "id": authorization.person.id,
                "employee_number": authorization.person.employee_number,
                "last_name": authorization.person.last_name,
                "first_name": authorization.person.first_name,
            },
            "cycle": {
                "code": authorization.cycle.code,
                "start_date": authorization.cycle.start_date,
                "end_date": authorization.cycle.end_date,
            },
            "issued_at": authorization.issued_at,
            "status": authorization.status,
            "comment": authorization.comment,
            "competencies": [
                {
                    "id": item.competency.id,
                    "code": item.competency.code,
                    "name": item.competency.name,
                }
                for item in authorization.competencies
            ],
        }

    finally:
        db.close()

@router.get("/people/{person_id}/current-authorization")
def get_current_authorization(person_id: int):
    db = SessionLocal()

    try:
        person = db.get(models.Person, person_id)

        if not person:
            return {
                "status": "error",
                "message": "Personne introuvable",
            }

        authorization = db.scalar(
            select(models.Authorization)
            .where(
                models.Authorization.person_id == person_id,
                models.Authorization.status == "ACTIVE",
            )
            .order_by(models.Authorization.issued_at.desc())
        )

        if not authorization:
            return {
                "status": "none",
                "message": "Aucune habilitation active",
                "person_id": person_id,
            }

        return {
            "id": authorization.id,
            "person": {
                "id": person.id,
                "employee_number": person.employee_number,
                "last_name": person.last_name,
                "first_name": person.first_name,
            },
            "cycle": {
                "id": authorization.cycle.id,
                "code": authorization.cycle.code,
                "name": authorization.cycle.name,
                "start_date": authorization.cycle.start_date,
                "end_date": authorization.cycle.end_date,
            },
            "issued_at": authorization.issued_at,
            "status": authorization.status,
            "comment": authorization.comment,
            "competencies": [
                {
                    "id": item.competency.id,
                    "code": item.competency.code,
                    "name": item.competency.name,
                }
                for item in authorization.competencies
            ],
        }

    finally:
        db.close()

@router.get("/people/{person_id}/authorizations")
def get_person_authorizations(person_id: int):
    db = SessionLocal()

    try:
        person = db.get(models.Person, person_id)

        if not person:
            return {
                "status": "error",
                "message": "Personne introuvable",
            }

        authorizations = db.scalars(
            select(models.Authorization)
            .where(
                models.Authorization.person_id == person_id
            )
            .order_by(models.Authorization.issued_at.asc())
        ).all()

        return {
            "person": {
                "id": person.id,
                "employee_number": person.employee_number,
                "last_name": person.last_name,
                "first_name": person.first_name,
            },
            "authorizations": [
                {
                    "id": authorization.id,
                    "cycle": {
                        "id": authorization.cycle.id,
                        "code": authorization.cycle.code,
                        "name": authorization.cycle.name,
                        "start_date": authorization.cycle.start_date,
                        "end_date": authorization.cycle.end_date,
                    },
                    "issued_at": authorization.issued_at,
                    "status": authorization.status,
                    "comment": authorization.comment,
                    "competencies": [
                        {
                            "id": item.competency.id,
                            "code": item.competency.code,
                            "name": item.competency.name,
                        }
                        for item in authorization.competencies
                    ],
                }
                for authorization in authorizations
            ],
        }

    finally:
        db.close()