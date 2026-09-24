from datetime import datetime

from sqlalchemy import select

from .. import models

from .audit import write_audit_log


def regenerate_general_authorization(
    db,
    person_id: int,
    session: dict | None = None,
):
    """
    Régénère l'habilitation générale courante d'une personne.

    L'ancienne habilitation ACTIVE est conservée en historique
    avec le statut SUPERSEDED.

    La nouvelle habilitation contient un snapshot des compétences
    générales actuellement VALIDATED.
    """

    # 1. Trouver le cycle collectif actif
    cycle = db.scalar(
        select(models.AuthorizationCycle).where(
            models.AuthorizationCycle.active == True
        )
    )

    if not cycle:
        return None

    # 2. Trouver l'habilitation ACTIVE actuelle
    current_authorization = db.scalar(
        select(models.Authorization).where(
            models.Authorization.person_id == person_id,
            models.Authorization.cycle_id == cycle.id,
            models.Authorization.status == "ACTIVE",
        )
    )

    previous_authorization_id = None

    # 3. Conserver l'ancienne version en historique
    if current_authorization:
        previous_authorization_id = current_authorization.id
        current_authorization.status = "SUPERSEDED"

    # 4. Créer une nouvelle habilitation
    new_authorization = models.Authorization(
        person_id=person_id,
        cycle_id=cycle.id,
        issued_at=datetime.now(),
        status="ACTIVE",
        comment="Version générée automatiquement",
    )

    db.add(new_authorization)
    db.flush()

    # 5. Chercher les compétences générales
    # actuellement VALIDATED
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
            models.PersonCompetency.person_id
            == person_id,
            models.PersonCompetency.validation_status
            == "VALIDATED",
            models.ValidityRule.code
            == "GENERAL_AUTHORIZATION",
        )
    ).all()

    # 6. Créer le snapshot de l'habilitation
    for person_competency in person_competencies:
        snapshot = models.AuthorizationCompetency(
            authorization_id=new_authorization.id,
            competency_id=(
                person_competency.competency_id
            ),
        )

        db.add(snapshot)

    # 7. Auditer la génération automatique
    if session:
        write_audit_log(
            db=db,
            session=session,
            action="CREATE",
            entity_type="AUTHORIZATION",
            entity_id=new_authorization.id,
            after_data={
                "person_id": person_id,
                "cycle_id": cycle.id,
                "cycle_code": cycle.code,
                "status": new_authorization.status,
                "issued_at": new_authorization.issued_at,
                "previous_authorization_id": (
                    previous_authorization_id
                ),
                "competency_ids": [
                    person_competency.competency_id
                    for person_competency
                    in person_competencies
                ],
                "generation_mode": "AUTOMATIC",
            },
            details="Génération automatique d'une habilitation",
        )

    return new_authorization