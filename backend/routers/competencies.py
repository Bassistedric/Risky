from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from ..database import SessionLocal
from .. import models
from ..schemas.competencies import (
    PersonCompetencyCreate,
    PersonCompetencyStatusUpdate,
)
from ..services.authorizations import (
    regenerate_general_authorization,
)
from ..services.session import require_write_session
from ..services.audit import write_audit_log

router = APIRouter(
    tags=["Compétences"],
)

@router.post("/seed-competency-categories")
def seed_competency_categories(
    session=Depends(require_write_session),
):

    db = SessionLocal()

    try:
        categories = [
            ("VCA", "VCA"),
            ("ELECTRICITE", "Électricité"),
            ("ENGINS", "Engins de levage / manutention"),
            ("HAUTEUR", "Travail en hauteur"),
            ("ECHAFAUDAGES", "Échafaudages"),
            ("LEVAGE", "Levage / élingage"),
            ("ESPACES_CONFINES", "Espaces confinés"),
            ("AMIANTE", "Amiante"),
            ("SECOURS_INCENDIE", "Incendie / premiers secours"),
            ("CONTROLES", "Contrôles / inspections"),
            ("AUTRES_RISQUES", "Autres tâches à risques"),
        ]

        created = 0

        for code, name in categories:
            existing = db.scalar(
                select(models.CompetencyCategory).where(
                    models.CompetencyCategory.code == code
                )
            )

            if not existing:
                db.add(
                    models.CompetencyCategory(
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


@router.get("/competency-categories")
def list_competency_categories():
    db = SessionLocal()

    try:
        categories = db.scalars(
            select(models.CompetencyCategory).order_by(
                models.CompetencyCategory.id
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

@router.post("/seed-competencies")
def seed_competencies(
    session=Depends(require_write_session),
):

    db = SessionLocal()

    try:
        competencies = [
            # VCA
            ("VCA_BASE", "VCA Base", "VCA"),
            ("VCA_CADRE", "VCA Cadre opérationnel", "VCA"),

            # Électricité
            ("BA4", "BA4", "ELECTRICITE"),
            ("BA5", "BA5", "ELECTRICITE"),
            ("MANOEUVRE_HT", "Manœuvre haute tension", "ELECTRICITE"),

            # Engins de levage / manutention
            ("CHARIOT", "Conduite d'élévateur à fourches", "ENGINS"),
            ("MANITOU", "Conduite d'engin télescopique / Manitou", "ENGINS"),
            ("NACELLE", "Conduite de nacelle élévatrice", "ENGINS"),
            ("PONT", "Conduite d'un pont poiré ou télécommandé", "ENGINS"),

            # Travail en hauteur
            ("HARNAIS", "Port du harnais antichute", "HAUTEUR"),
            ("TRAVAIL_HAUTEUR", "Travail en hauteur sur échafaudage", "HAUTEUR"),
            ("ANCRAGE_MOBILE", "Mise en place d'un point d'ancrage mobile", "HAUTEUR"),

            # Échafaudages
            (
                "ECHAFAUDAGE",
                "Montage, contrôle et démontage d'échafaudage",
                "ECHAFAUDAGES",
            ),

            # Levage / élingage
            ("GUIDAGE_LEVAGE", "Guidage du levage d'une charge", "LEVAGE"),
            ("ELINGAGE", "Élingage de charges", "LEVAGE"),

            # Espaces confinés
            ("ESPACE_CONFINE", "Travail en espace confiné", "ESPACES_CONFINES"),
            ("ARI", "Port d'un appareil respiratoire isolant (ARI)", "ESPACES_CONFINES"),

            # Amiante
            (
                "AMIANTE_TS",
                "Enlèvement d'amiante en traitement simple",
                "AMIANTE",
            ),

            # Incendie / premiers secours
            (
                "EPI_INCENDIE",
                "Équipier de première intervention",
                "SECOURS_INCENDIE",
            ),
            ("SECOURISTE", "Secouriste", "SECOURS_INCENDIE"),

            # Contrôles / inspections
            (
                "CONTROLE_MATERIEL",
                "Contrôle annuel du matériel",
                "CONTROLES",
            ),
        ]

        created = 0

        for code, name, category_code in competencies:
            existing = db.scalar(
                select(models.Competency).where(
                    models.Competency.code == code
                )
            )

            if existing:
                continue

            category = db.scalar(
                select(models.CompetencyCategory).where(
                    models.CompetencyCategory.code == category_code
                )
            )

            if category:
                db.add(
                    models.Competency(
                        code=code,
                        name=name,
                        category_id=category.id,
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


@router.get("/competencies")
def list_competencies():
    db = SessionLocal()

    try:
        competencies = db.scalars(
            select(models.Competency).order_by(
                models.Competency.id
            )
        ).all()

        return [
    {
        "id": competency.id,
        "code": competency.code,
        "name": competency.name,
        "category": (
            competency.category.name
            if competency.category
            else None
        ),
        "validity_rule": (
            competency.validity_rule.code
            if competency.validity_rule
            else None
        ),
        "active": competency.active,
    }
    for competency in competencies
]
    finally:
        db.close()

@router.post("/seed-validity-rules")
def seed_validity_rules(
    session=Depends(require_write_session),
):

    db = SessionLocal()

    try:
        rules = [
            {
                "code": "VCA_10Y",
                "name": "VCA - validité 10 ans date à date",
                "validity_months": 120,
                "validity_mode": "DATE_TO_DATE",
                "automatic_renewal": False,
            },
            {
                "code": "ANNUAL",
                "name": "Renouvellement annuel date à date",
                "validity_months": 12,
                "validity_mode": "DATE_TO_DATE",
                "automatic_renewal": False,
            },
            {
                "code": "GENERAL_AUTHORIZATION",
                "name": "Cycle d'habilitation générale",
                "validity_months": 60,
                "validity_mode": "COMMON_CYCLE",
                "automatic_renewal": True,
            },
        ]

        created = 0

        for rule_data in rules:
            existing = db.scalar(
                select(models.ValidityRule).where(
                    models.ValidityRule.code == rule_data["code"]
                )
            )

            if not existing:
                db.add(models.ValidityRule(**rule_data))
                created += 1

        db.commit()

        return {
            "status": "ok",
            "created": created,
        }

    finally:
        db.close()

@router.get("/validity-rules")
def list_validity_rules():
    db = SessionLocal()

    try:
        rules = db.scalars(
            select(models.ValidityRule).order_by(
                models.ValidityRule.id
            )
        ).all()

        return [
            {
                "id": rule.id,
                "code": rule.code,
                "name": rule.name,
                "validity_months": rule.validity_months,
                "validity_mode": rule.validity_mode,
                "automatic_renewal": rule.automatic_renewal,
                "active": rule.active,
            }
            for rule in rules
        ]

    finally:
        db.close()

@router.post("/assign-validity-rules")
def assign_validity_rules(
    session=Depends(require_write_session),
):
    
    db = SessionLocal()

    try:
        rules = {
            rule.code: rule
            for rule in db.scalars(
                select(models.ValidityRule)
            ).all()
        }

        mapping = {
            # VCA → 10 ans date à date
            "VCA_BASE": "VCA_10Y",
            "VCA_CADRE": "VCA_10Y",

            # Renouvellement annuel
            "SECOURISTE": "ANNUAL",
            "AMIANTE_TS": "ANNUAL",
            "EPI_INCENDIE": "ANNUAL",
        }

        updated = 0

        competencies = db.scalars(
            select(models.Competency)
        ).all()

        for competency in competencies:
            rule_code = mapping.get(
                competency.code,
                "GENERAL_AUTHORIZATION",
            )

            rule = rules.get(rule_code)

            if rule and competency.validity_rule_id != rule.id:
                competency.validity_rule_id = rule.id
                updated += 1

        db.commit()

        return {
            "status": "ok",
            "updated": updated,
        }

    finally:
        db.close()

@router.post("/seed-person-competency")
def seed_person_competency(
    session=Depends(require_write_session),
):

    db = SessionLocal()

    try:
        person = db.scalar(
            select(models.Person).where(
                models.Person.employee_number == "0001"
            )
        )

        if not person:
            return {
                "status": "error",
                "message": "Personne 0001 introuvable",
            }

        competency = db.scalar(
            select(models.Competency).where(
                models.Competency.code == "NACELLE"
            )
        )

        if not competency:
            return {
                "status": "error",
                "message": "Compétence NACELLE introuvable",
            }

        existing = db.scalar(
            select(models.PersonCompetency).where(
                models.PersonCompetency.person_id == person.id,
                models.PersonCompetency.competency_id == competency.id,
            )
        )

        if existing:
            return {
                "status": "already_exists",
                "person_competency_id": existing.id,
            }

        person_competency = models.PersonCompetency(
            person_id=person.id,
            competency_id=competency.id,
            provider="Organisme de démonstration",
            certificate_reference="DEMO-NACELLE-001",
            validation_status="VALIDATED",
            comment="Compétence de démonstration RISKY",
        )

        db.add(person_competency)
        db.commit()
        db.refresh(person_competency)

        return {
            "status": "created",
            "person_competency_id": person_competency.id,
        }

    finally:
        db.close()


@router.post("/people/{person_id}/competencies")
def add_person_competency(
    person_id: int,
    data: PersonCompetencyCreate,
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

        competency = db.get(
            models.Competency,
            data.competency_id,
        )

        if not competency:
            return {
                "status": "error",
                "message": "Compétence introuvable",
            }

        existing = db.scalar(
            select(models.PersonCompetency).where(
                models.PersonCompetency.person_id == person_id,
                models.PersonCompetency.competency_id == data.competency_id,
                models.PersonCompetency.validation_status != "REVOKED",
            )
        )

        if existing:
            return {
                "status": "already_exists",
                "person_competency_id": existing.id,
            }

        person_competency = models.PersonCompetency(
            person_id=person_id,
            competency_id=data.competency_id,
            obtained_at=data.obtained_at,
            provider=data.provider,
            certificate_reference=data.certificate_reference,
            document_path=data.document_path,
            validation_status="VALIDATED",
            comment=data.comment,
        )

        db.add(person_competency)
        db.flush()

        history = models.PersonCompetencyStatusHistory(
            person_competency_id=person_competency.id,
            previous_status=None,
            new_status="VALIDATED",
            reason="Compétence attribuée",
        )

        db.add(history)

        if (
            competency.validity_rule
            and competency.validity_rule.code == "GENERAL_AUTHORIZATION"
        ):
            regenerate_general_authorization(
                db,
                person_id,
                session=session,
            )

        db.commit()
        db.refresh(person_competency)

        return {
            "status": "created",
            "person_competency_id": person_competency.id,
            "person": f"{person.first_name} {person.last_name}",
            "competency": competency.name,
        }

    finally:
        db.close()

@router.post("/person-competencies/{person_competency_id}/status")
def update_person_competency_status(
    person_competency_id: int,
    data: PersonCompetencyStatusUpdate,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        allowed_statuses = {
            "VALIDATED",
            "SUSPENDED",
            "REVOKED",
        }

        if data.status not in allowed_statuses:
            return {
                "status": "error",
                "message": "Statut invalide",
                "allowed_statuses": sorted(allowed_statuses),
            }

        person_competency = db.get(
            models.PersonCompetency,
            person_competency_id,
        )

        if not person_competency:
            return {
                "status": "error",
                "message": "Compétence individuelle introuvable",
            }

        previous_status = person_competency.validation_status

        if previous_status == data.status:
            return {
                "status": "unchanged",
                "person_competency_id": person_competency.id,
                "validation_status": person_competency.validation_status,
            }

        before_data = {
            "validation_status": person_competency.validation_status,
            "comment": person_competency.comment,
        }

        person_competency.validation_status = data.status

        if data.comment is not None:
            person_competency.comment = data.comment

        history = models.PersonCompetencyStatusHistory(
            person_competency_id=person_competency.id,
            previous_status=previous_status,
            new_status=data.status,
            reason=data.comment,
        )

        db.add(history)

        validity_rule_code = person_competency.competency.validity_rule.code

        if validity_rule_code == "GENERAL_AUTHORIZATION":
            regenerate_general_authorization(
                db,
                person_competency.person_id,
                session=session,
            )

        write_audit_log(
            db=db,
            session=session,
            action="STATUS_CHANGE",
            entity_type="PERSON_COMPETENCY",
            entity_id=person_competency.id,
            before_data=before_data,
            after_data={
                "validation_status": person_competency.validation_status,
                "comment": person_competency.comment,
            },
            details=(
                f"Changement de statut de compétence : "
                f"{previous_status} -> {data.status}"
            ),
        )

        db.commit()
        db.refresh(person_competency)

        return {
            "status": "updated",
            "person_competency_id": person_competency.id,
            "validation_status": person_competency.validation_status,
            "comment": person_competency.comment,
        }

    finally:
        db.close()

@router.get("/people/{person_id}/competency-status")
def get_person_competency_status(person_id: int):
    db = SessionLocal()

    try:
        person = db.get(models.Person, person_id)

        if not person:
            return {
                "status": "error",
                "message": "Personne introuvable",
            }

        person_competencies = db.scalars(
            select(models.PersonCompetency).where(
                models.PersonCompetency.person_id == person_id
            )
        ).all()

        current = []

        for pc in person_competencies:
            competency = pc.competency

            if (
                competency.validity_rule
                and competency.validity_rule.code
                == "GENERAL_AUTHORIZATION"
            ):
                current.append(
                    {
                        "person_competency_id": pc.id,
                        "competency_id": competency.id,
                        "code": competency.code,
                        "name": competency.name,
                        "validation_status": pc.validation_status,
                        "usable": (
                            pc.validation_status == "VALIDATED"
                        ),
                    }
                )

        return {
            "person": {
                "id": person.id,
                "employee_number": person.employee_number,
                "last_name": person.last_name,
                "first_name": person.first_name,
            },
            "competencies": current,
        }

    finally:
        db.close()


@router.get("/person-competencies/{person_competency_id}/history")
def get_person_competency_history(person_competency_id: int):
    db = SessionLocal()

    try:
        person_competency = db.get(
            models.PersonCompetency,
            person_competency_id,
        )

        if not person_competency:
            return {
                "status": "error",
                "message": "Compétence individuelle introuvable",
            }

        history = db.scalars(
            select(models.PersonCompetencyStatusHistory)
            .where(
                models.PersonCompetencyStatusHistory.person_competency_id
                == person_competency_id
            )
            .order_by(
                models.PersonCompetencyStatusHistory.changed_at
            )
        ).all()

        return {
            "person_competency_id": person_competency.id,
            "person": (
                f"{person_competency.person.first_name} "
                f"{person_competency.person.last_name}"
            ),
            "competency": person_competency.competency.name,
            "current_status": person_competency.validation_status,
            "history": [
                {
                    "id": item.id,
                    "previous_status": item.previous_status,
                    "new_status": item.new_status,
                    "changed_at": item.changed_at,
                    "reason": item.reason,
                }
                for item in history
            ],
        }

    finally:
        db.close()