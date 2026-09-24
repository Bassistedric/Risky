from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import delete, select

from ...database import SessionLocal
from ... import models

from ...schemas.events import EventCreate, EventAnalysisTypeUpdate
from ...schemas import events as schemas

from ...services.session import require_write_session
from ...services.audit import write_audit_log
from ...services.serious_accidents import evaluate_serious_accident
router = APIRouter(
    prefix="/events",
    tags=["Accidents & Incidents"],
)


@router.post("")
def create_event(
    data: EventCreate,
    session=Depends(require_write_session),
):

    db = SessionLocal()

    try:
        allowed_types = {
            "ACCIDENT",
            "INCIDENT",
            "NEAR_MISS",
            "MATERIAL",
            "ENVIRONMENT",
        }

        if data.event_type not in allowed_types:
            return {
                "status": "error",
                "message": "Type d'Ã©vÃ©nement invalide",
                "allowed_types": sorted(allowed_types),
            }

        # ====================================================
        # CATÃ‰GORIE DE PERSONNE
        # ====================================================

        allowed_person_categories = {
            "WORKER",
            "EMPLOYEE",
            "TEMPORARY",
            "SUBCONTRACTOR",
            "OTHER",
        }

        if (
            data.person_category is not None
            and data.person_category
            not in allowed_person_categories
        ):
            return {
                "status": "error",
                "message": "CatÃ©gorie de personne invalide",
                "allowed_categories": sorted(
                    allowed_person_categories
                ),
            }

        # ====================================================
        # IMPACT ENVIRONNEMENTAL
        # ====================================================

        allowed_environmental_types = {
            "SPILL",
            "LEAK",
            "RELEASE",
            "SOIL",
            "WATER",
            "AIR",
            "OTHER",
        }

        if (
            data.environmental_damage_type is not None
            and data.environmental_damage_type
            not in allowed_environmental_types
        ):
            return {
                "status": "error",
                "message": (
                    "Type d'impact environnemental invalide"
                ),
                "allowed_types": sorted(
                    allowed_environmental_types
                ),
            }

        if data.lost_days < 0:
            return {
                "status": "error",
                "message": (
                    "Le nombre de jours perdus "
                    "ne peut pas Ãªtre nÃ©gatif"
                ),
            }

        if data.modified_duty_days < 0:
            return {
                "status": "error",
                "message": (
                    "Le nombre de jours de travail adaptÃ© "
                    "ne peut pas Ãªtre nÃ©gatif"
                ),
            }

        if (
            data.material_damage_cost is not None
            and data.material_damage_cost < 0
        ):
            return {
                "status": "error",
                "message": (
                    "Le coÃ»t des dommages matÃ©riels "
                    "ne peut pas Ãªtre nÃ©gatif"
                ),
            }

        if (
            data.environmental_quantity is not None
            and data.environmental_quantity < 0
        ):
            return {
                "status": "error",
                "message": (
                    "La quantitÃ© environnementale "
                    "ne peut pas Ãªtre nÃ©gative"
                ),
            }

        if data.person_id is not None:
            person = db.get(
                models.Person,
                data.person_id,
            )

            if not person:
                return {
                    "status": "error",
                    "message": "Personne introuvable",
                }

        if data.organization_id is not None:
            organization = db.get(
                models.Organization,
                data.organization_id,
            )

            if not organization:
                return {
                    "status": "error",
                    "message": "Organisation introuvable",
                }

        year = data.event_date.year
        prefix = f"EVT-{year}-"

        existing_numbers = db.scalars(
            select(models.Event.event_number)
            .where(
                models.Event.event_number.like(
                    f"{prefix}%"
                )
            )
            .order_by(
                models.Event.event_number.desc()
            )
        ).all()

        if existing_numbers:
            last_number = existing_numbers[0]
            sequence = (
                int(last_number.split("-")[-1]) + 1
            )
        else:
            sequence = 1

        event_number = f"{prefix}{sequence:04d}"

        lost_days = (
            data.lost_days
            if data.lost_time
            else 0
        )

        modified_duty_days = (
            data.modified_duty_days
            if data.modified_duty
            else 0
        )

        event = models.Event(
            event_number=event_number,
            event_date=data.event_date,
            event_type=data.event_type,

            # ================================================
            # PERSONNE / VICTIME
            # ================================================

            person_id=data.person_id,
            person_category=data.person_category,
            victim_last_name=data.victim_last_name,
            victim_first_name=data.victim_first_name,

            # ================================================
            # ORGANISATION / HIÃ‰RARCHIE
            # ================================================

            organization_id=data.organization_id,
            project_manager=data.project_manager,
            site_supervisor=data.site_supervisor,

            # ================================================
            # Ã‰VÃ‰NEMENT
            # ================================================

            location=data.location,
            description=data.description,

            # ================================================
            # CONSÃ‰QUENCES HUMAINES
            # ================================================

            lost_time=data.lost_time,
            lost_days=lost_days,

            modified_duty=data.modified_duty,
            modified_duty_days=modified_duty_days,

            fatal=data.fatal,
            permanent_injury=data.permanent_injury,

            # ================================================
            # CONSÃ‰QUENCES MATÃ‰RIELLES
            # ================================================

            material_damage=data.material_damage,
            material_damage_details=(
                data.material_damage_details
            ),
            material_damage_cost=(
                data.material_damage_cost
            ),

            # ================================================
            # CONSÃ‰QUENCES ENVIRONNEMENTALES
            # ================================================

            environmental_damage=(
                data.environmental_damage
            ),
            environmental_damage_type=(
                data.environmental_damage_type
            ),
            environmental_damage_details=(
                data.environmental_damage_details
            ),
            environmental_quantity=(
                data.environmental_quantity
            ),
            environmental_unit=(
                data.environmental_unit
            ),

            status="OPEN",
        )

        db.add(event)
        db.flush()

        write_audit_log(
            db=db,
            session=session,
            action="CREATE",
            entity_type="EVENT",
            entity_id=event.id,
            after_data={
                "event_number": event.event_number,
                "event_date": event.event_date,
                "event_type": event.event_type,
                "person_id": event.person_id,
                                "person_category": (
                    event.person_category
                ),
                "victim_last_name": (
                    event.victim_last_name
                ),
                "victim_first_name": (
                    event.victim_first_name
                ),
                "organization_id": event.organization_id,
                                "project_manager": (
                    event.project_manager
                ),
                "site_supervisor": (
                    event.site_supervisor
                ),
                "location": event.location,
                "description": event.description,
                "lost_time": event.lost_time,
                "lost_days": event.lost_days,
                "modified_duty": event.modified_duty,
                "modified_duty_days": (
                    event.modified_duty_days
                ),
                "fatal": event.fatal,
                "permanent_injury": (
                    event.permanent_injury
                ),
                                "material_damage": (
                    event.material_damage
                ),
                "material_damage_details": (
                    event.material_damage_details
                ),
                "material_damage_cost": (
                    event.material_damage_cost
                ),
                "environmental_damage": (
                    event.environmental_damage
                ),
                "environmental_damage_type": (
                    event.environmental_damage_type
                ),
                "environmental_damage_details": (
                    event.environmental_damage_details
                ),
                "environmental_quantity": (
                    event.environmental_quantity
                ),
                "environmental_unit": (
                    event.environmental_unit
                ),
                "status": event.status,
            },
            details="CrÃ©ation d'un Ã©vÃ©nement",
        )

        db.commit()
        db.refresh(event)

        return {
            "status": "created",
            "event": {
                "id": event.id,
                "event_number": event.event_number,
                "event_date": event.event_date,
                "event_type": event.event_type,

                # ============================================
                # PERSONNE / VICTIME
                # ============================================

                "person_id": event.person_id,
                "person_category": event.person_category,
                "victim_last_name": event.victim_last_name,
                "victim_first_name": event.victim_first_name,

                # ============================================
                # ORGANISATION / HIÃ‰RARCHIE
                # ============================================

                "organization_id": event.organization_id,
                "project_manager": event.project_manager,
                "site_supervisor": event.site_supervisor,

                # ============================================
                # Ã‰VÃ‰NEMENT
                # ============================================

                "location": event.location,
                "description": event.description,

                # ============================================
                # CONSÃ‰QUENCES HUMAINES
                # ============================================

                "lost_time": event.lost_time,
                "lost_days": event.lost_days,
                "modified_duty": event.modified_duty,
                "modified_duty_days": (
                    event.modified_duty_days
                ),
                "fatal": event.fatal,
                "permanent_injury": event.permanent_injury,

                # ============================================
                # CONSÃ‰QUENCES MATÃ‰RIELLES
                # ============================================

                "material_damage": event.material_damage,
                "material_damage_details": (
                    event.material_damage_details
                ),
                "material_damage_cost": (
                    event.material_damage_cost
                ),

                # ============================================
                # CONSÃ‰QUENCES ENVIRONNEMENTALES
                # ============================================

                "environmental_damage": (
                    event.environmental_damage
                ),
                "environmental_damage_type": (
                    event.environmental_damage_type
                ),
                "environmental_damage_details": (
                    event.environmental_damage_details
                ),
                "environmental_quantity": (
                    event.environmental_quantity
                ),
                "environmental_unit": (
                    event.environmental_unit
                ),

                "event_status": event.status,
            },
        }

    finally:
        db.close()


@router.get("")
def get_events():
    db = SessionLocal()

    try:
        events = db.scalars(
            select(models.Event)
            .order_by(models.Event.event_date.desc())
        ).all()

        classifications = {
            item.event_id: item
            for item in db.scalars(
                select(models.EventClassification).where(
                    models.EventClassification.event_id.in_(
                        [event.id for event in events]
                    )
                )
            ).all()
        }

        return {
            "count": len(events),
            "events": [
                {
                    "id": event.id,
                    "event_number": event.event_number,
                    "event_date": event.event_date,
                    "event_type": event.event_type,
                    "person_id": event.person_id,

                    "person": (
                        f"{event.person.first_name} "
                        f"{event.person.last_name}"
                        if event.person
                        else (
                            " ".join(
                                part
                                for part in [
                                    event.victim_first_name,
                                    event.victim_last_name,
                                ]
                                if part
                            )
                            or None
                        )
                    ),

                    "person_category": event.person_category,
                    "victim_last_name": event.victim_last_name,
                    "victim_first_name": event.victim_first_name,
                    "organization_id": event.organization_id,
                    "organization": (
                        event.organization.name
                        if event.organization
                        else None
                    ),
                    "project_manager": event.project_manager,
                    "site_supervisor": event.site_supervisor,
                    "location": event.location,
                    "description": event.description,
                    "lost_time": event.lost_time,
                    "lost_days": event.lost_days,
                    "modified_duty": event.modified_duty,
                    "modified_duty_days": event.modified_duty_days,
                    "fatal": event.fatal,
                    "permanent_injury": event.permanent_injury,
                    "material_damage": event.material_damage,
                    "material_damage_details": (
                        event.material_damage_details
                    ),
                    "material_damage_cost": (
                        event.material_damage_cost
                    ),

                    "environmental_damage": (
                        event.environmental_damage
                    ),
                    "environmental_damage_type": (
                        event.environmental_damage_type
                    ),
                    "environmental_damage_details": (
                        event.environmental_damage_details
                    ),
                    "environmental_quantity": (
                        event.environmental_quantity
                    ),
                    "environmental_unit": (
                        event.environmental_unit
                    ),
                    "analysis_type": event.analysis_type,
                    "circumstantial_report_required": bool(
                        evaluate_serious_accident(
                            db,
                            event,
                            classifications.get(event.id),
                        ).get("circumstantial_report_required")
                    ),
                    "status": event.status,
                                "person_category": event.person_category,
                    "victim_last_name": event.victim_last_name,
                    "victim_first_name": event.victim_first_name,

                    "project_manager": event.project_manager,
                    "site_supervisor": event.site_supervisor,

                    "material_damage": event.material_damage,
                    "material_damage_details": (
                        event.material_damage_details
                    ),
                    "material_damage_cost": (
                        event.material_damage_cost
                    ),

                    "environmental_damage": (
                        event.environmental_damage
                    ),
                    "environmental_damage_type": (
                        event.environmental_damage_type
                    ),
                    "environmental_damage_details": (
                        event.environmental_damage_details
                    ),
                    "environmental_quantity": (
                        event.environmental_quantity
                    ),
                    "environmental_unit": (
                        event.environmental_unit
                    ),
                }
                for event in events
            ],
        }

    finally:
        db.close()


@router.get("/{event_id}")
def get_event(event_id: int):
    db = SessionLocal()

    try:
        event = db.get(
            models.Event,
            event_id,
        )

        if not event:
            return {
                "status": "error",
                "message": "Ã‰vÃ©nement introuvable",
            }

        return {
            "id": event.id,
            "event_number": event.event_number,
            "event_date": event.event_date,
            "event_type": event.event_type,
            "analysis_type": event.analysis_type,

            # ================================================
            # PERSONNE / VICTIME
            # ================================================

            "person": (
                {
                    "id": event.person.id,
                    "employee_number": (
                        event.person.employee_number
                    ),
                    "last_name": event.person.last_name,
                    "first_name": event.person.first_name,
                }
                if event.person
                else None
            ),

            "person_id": event.person_id,
            "person_category": event.person_category,
            "victim_last_name": event.victim_last_name,
            "victim_first_name": event.victim_first_name,

            # ================================================
            # ORGANISATION / HIÃ‰RARCHIE
            # ================================================

            "organization": (
                {
                    "id": event.organization.id,
                    "name": event.organization.name,
                }
                if event.organization
                else None
            ),

            "project_manager": event.project_manager,
            "site_supervisor": event.site_supervisor,

            # ================================================
            # Ã‰VÃ‰NEMENT
            # ================================================

            "location": event.location,
            "description": event.description,

            # ================================================
            # CONSÃ‰QUENCES HUMAINES
            # ================================================

            "lost_time": event.lost_time,
            "lost_days": event.lost_days,
            "modified_duty": event.modified_duty,
            "modified_duty_days": event.modified_duty_days,
            "fatal": event.fatal,
            "permanent_injury": event.permanent_injury,

            # ================================================
            # CONSÃ‰QUENCES MATÃ‰RIELLES
            # ================================================

            "material_damage": event.material_damage,
            "material_damage_details": (
                event.material_damage_details
            ),
            "material_damage_cost": (
                event.material_damage_cost
            ),

            # ================================================
            # CONSÃ‰QUENCES ENVIRONNEMENTALES
            # ================================================

            "environmental_damage": (
                event.environmental_damage
            ),
            "environmental_damage_type": (
                event.environmental_damage_type
            ),
            "environmental_damage_details": (
                event.environmental_damage_details
            ),
            "environmental_quantity": (
                event.environmental_quantity
            ),
            "environmental_unit": (
                event.environmental_unit
            ),

            # ================================================
            # DOSSIER
            # ================================================

            "status": event.status,
            "created_at": event.created_at,
        }

    finally:
        db.close()

# ============================================================
# MODIFICATION D'UN Ã‰VÃ‰NEMENT
# ============================================================

@router.patch("/{event_id}")
def update_event(
    event_id: int,
    payload: schemas.EventUpdate,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        event = db.get(
            models.Event,
            event_id,
        )

        if event is None:
            raise HTTPException(
                status_code=404,
                detail="Ã‰vÃ©nement introuvable",
            )

        update_data = payload.model_dump(
            exclude_unset=True,
        )

        # ====================================================
        # VALIDATIONS
        # ====================================================

        if "event_type" in update_data:
            allowed_types = {
                "ACCIDENT",
                "INCIDENT",
                "NEAR_MISS",
                "MATERIAL",
                "ENVIRONMENT",
            }

            if update_data["event_type"] not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail="Type d'Ã©vÃ©nement invalide",
                )

        if "person_category" in update_data:
            allowed_person_categories = {
                "WORKER",
                "EMPLOYEE",
                "TEMPORARY",
                "SUBCONTRACTOR",
                "OTHER",
            }

            category = update_data["person_category"]

            if (
                category is not None
                and category not in allowed_person_categories
            ):
                raise HTTPException(
                    status_code=400,
                    detail="CatÃ©gorie de personne invalide",
                )

        if "analysis_type" in update_data:
            if update_data["analysis_type"] not in {
                "NORMAL",
                "ADVANCED",
            }:
                raise HTTPException(
                    status_code=400,
                    detail="Type d'analyse invalide",
                )

        if (
            update_data.get("lost_days") is not None
            and update_data["lost_days"] < 0
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Le nombre de jours perdus "
                    "ne peut pas Ãªtre nÃ©gatif"
                ),
            )

        if (
            update_data.get("modified_duty_days") is not None
            and update_data["modified_duty_days"] < 0
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Le nombre de jours de travail adaptÃ© "
                    "ne peut pas Ãªtre nÃ©gatif"
                ),
            )

        if (
            update_data.get("material_damage_cost") is not None
            and update_data["material_damage_cost"] < 0
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Le coÃ»t des dommages matÃ©riels "
                    "ne peut pas Ãªtre nÃ©gatif"
                ),
            )

        if (
            update_data.get("environmental_quantity") is not None
            and update_data["environmental_quantity"] < 0
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "La quantitÃ© environnementale "
                    "ne peut pas Ãªtre nÃ©gative"
                ),
            )

        # ====================================================
        # PERSONNE
        # ====================================================

        if (
            "person_id" in update_data
            and update_data["person_id"] is not None
        ):
            person = db.get(
                models.Person,
                update_data["person_id"],
            )

            if person is None:
                raise HTTPException(
                    status_code=400,
                    detail="Personne introuvable",
                )

        # ====================================================
        # ORGANISATION
        # ====================================================

        if (
            "organization_id" in update_data
            and update_data["organization_id"] is not None
        ):
            organization = db.get(
                models.Organization,
                update_data["organization_id"],
            )

            if organization is None:
                raise HTTPException(
                    status_code=400,
                    detail="Organisation introuvable",
                )

        # ====================================================
        # AUDIT â€” Ã‰TAT AVANT MODIFICATION
        # ====================================================

        before_data = {
            field: getattr(event, field)
            for field in update_data
        }

        # ====================================================
        # RÃˆGLES DE COHÃ‰RENCE
        # ====================================================

        if update_data.get("lost_time") is False:
            update_data["lost_days"] = 0

        if update_data.get("modified_duty") is False:
            update_data["modified_duty_days"] = 0

        if update_data.get("material_damage") is False:
            update_data["material_damage_details"] = None
            update_data["material_damage_cost"] = None

        if update_data.get("environmental_damage") is False:
            update_data["environmental_damage_type"] = None
            update_data["environmental_damage_details"] = None
            update_data["environmental_quantity"] = None
            update_data["environmental_unit"] = None

 # ====================================================
        # VALIDATION DU STATUT
        # ====================================================

        if "status" in update_data:
            new_status = update_data["status"]

            allowed_statuses = {
                "OPEN",
                "IN_PROGRESS",
                "ACCEPTED",
                "REJECTED",
                "CLOSED",
            }

            if new_status not in allowed_statuses:
                raise HTTPException(
                    status_code=400,
                    detail="Statut d'événement invalide",
                )

            if event.event_type == "ACCIDENT":
                allowed_event_statuses = {
                    "OPEN",
                    "IN_PROGRESS",
                    "ACCEPTED",
                    "REJECTED",
                }
            else:
                allowed_event_statuses = {
                    "OPEN",
                    "CLOSED",
                }

            if new_status not in allowed_event_statuses:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Ce statut n'est pas autorisé "
                        "pour ce type d'événement"
                    ),
                )


        # ====================================================
        # MISE Ã€ JOUR
        # ====================================================

        for field, value in update_data.items():
            setattr(
                event,
                field,
                value,
            )

        db.flush()

        after_data = {
            field: getattr(event, field)
            for field in update_data
        }

        write_audit_log(
            db=db,
            session=session,
            action="UPDATE",
            entity_type="EVENT",
            entity_id=event.id,
            before_data=before_data,
            after_data=after_data,
            details=(
                f"Modification de l'Ã©vÃ©nement "
                f"{event.event_number}"
            ),
        )

        db.commit()
        db.refresh(event)

        return {
            "status": "updated",
            "event_id": event.id,
            "event_number": event.event_number,
        }

    except:
        db.rollback()
        raise

    finally:
        db.close()



@router.put("/{event_id}/analysis-type")
def update_event_analysis_type(
    event_id: int,
    data: EventAnalysisTypeUpdate,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        event = db.get(models.Event, event_id)

        if event is None:
            raise HTTPException(
                status_code=404,
                detail="Ã‰vÃ©nement introuvable",
            )

        allowed_types = {"NORMAL", "ADVANCED"}

        if data.analysis_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Type d'analyse invalide. Valeurs autorisÃ©es : NORMAL, ADVANCED",
            )

        before_data = {
            "analysis_type": event.analysis_type,
        }

        event.analysis_type = data.analysis_type

        after_data = {
            "analysis_type": event.analysis_type,
        }

        write_audit_log(
            db=db,
            session=session,
            action="UPDATE",
            entity_type="EVENT_ANALYSIS_TYPE",
            entity_id=event.id,
            before_data=before_data,
            after_data=after_data,
            details=f"Modification du type d'analyse de l'Ã©vÃ©nement {event.event_number}",
        )

        db.commit()
        db.refresh(event)

        return {
            "event_id": event.id,
            "event_number": event.event_number,
            "analysis_type": event.analysis_type,
        }

    except:
        db.rollback()
        raise

    finally:
        db.close()

# ============================================================
# SUPPRESSION DÉFINITIVE D'UN ÉVÉNEMENT
# ============================================================

@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        event = db.get(
            models.Event,
            event_id,
        )

        if event is None:
            raise HTTPException(
                status_code=404,
                detail="Événement introuvable",
            )

        event_number = event.event_number

        # ====================================================
        # AUDIT — AVANT SUPPRESSION
        # ====================================================

        write_audit_log(
            db=db,
            session=session,
            action="DELETE",
            entity_type="EVENT",
            entity_id=event.id,
            before_data={
                "event_number": event.event_number,
                "event_date": event.event_date,
                "event_type": event.event_type,
                "organization_id": event.organization_id,
                "person_id": event.person_id,
                "description": event.description,
                "status": event.status,
            },
            details=(
                f"Suppression définitive de l'événement "
                f"{event.event_number}"
            ),
        )

        # ====================================================
        # JUST CULTURE
        #
        # Les réponses dépendent de l'analyse.
        # Elles doivent donc être supprimées en premier.
        # ====================================================

        just_culture_analysis_ids = db.scalars(
            select(models.EventJustCultureAnalysis.id)
            .where(
                models.EventJustCultureAnalysis.event_id
                == event_id
            )
        ).all()

        if just_culture_analysis_ids:
            db.execute(
                delete(models.EventJustCultureAnswer)
                .where(
                    models.EventJustCultureAnswer.analysis_id.in_(
                        just_culture_analysis_ids
                    )
                )
            )

            db.execute(
                delete(models.EventJustCultureAnalysis)
                .where(
                    models.EventJustCultureAnalysis.event_id
                    == event_id
                )
            )

        # ====================================================
        # ARBRE DES CAUSES
        #
        # Les relations référencent les faits.
        # Relations d'abord, faits ensuite.
        # ====================================================

        db.execute(
            delete(models.EventCauseRelation)
            .where(
                models.EventCauseRelation.event_id
                == event_id
            )
        )

        db.execute(
            delete(models.EventCauseFact)
            .where(
                models.EventCauseFact.event_id
                == event_id
            )
        )

        # ====================================================
        # ÉVÉNEMENT
        #
        # SQLAlchemy supprimera également via cascade :
        # - EventFacts
        # - EventClassification
        # - EventHeepoFactor
        # ====================================================

        db.delete(event)

        db.commit()

        return {
            "status": "deleted",
            "event_id": event_id,
            "event_number": event_number,
        }

    except:
        db.rollback()
        raise

    finally:
        db.close()