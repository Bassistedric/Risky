# ========================================================
# RISKY — SERVICE RAPPORT D'ANALYSE ÉVÉNEMENT
# ========================================================

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import models
from backend.domain_models.actions.action import Action
from backend.services.cause_tree import (
    calculate_event_cause_levels,
    get_event_cause_tree,
)
from backend.services.event_photos import get_event_photos
from backend.services.just_culture import (
    get_event_just_culture_analysis,
)


# ========================================================
# OUTILS
# ========================================================

def _person_name(person) -> str | None:
    if person is None:
        return None

    return " ".join(
        part
        for part in [
            person.first_name,
            person.last_name,
        ]
        if part
    )


# ========================================================
# CONSTRUCTION DES DONNÉES DU RAPPORT
# ========================================================

def build_accident_report_preview(
    db: Session,
    event_id: int,
) -> dict:

    event = db.get(
        models.Event,
        event_id,
    )

    if event is None:
        raise ValueError(
            "Événement introuvable."
        )

    # ====================================================
    # ÉVÉNEMENT
    # ====================================================

    victim_name = (
        _person_name(event.person)
        if event.person
        else " ".join(
            part
            for part in [
                event.victim_first_name,
                event.victim_last_name,
            ]
            if part
        ) or None
    )

    event_data = {
        "id": event.id,
        "event_number": event.event_number,
        "event_date": event.event_date,
        "event_type": event.event_type,
        "analysis_type": event.analysis_type,
        "status": event.status,

        "description": event.description,
        "location": event.location,

        "person_id": event.person_id,
        "person_name": victim_name,
        "person_category": event.person_category,

        "organization_id": event.organization_id,
        "organization_name": (
            event.organization.name
            if event.organization
            else None
        ),

        "project_manager": event.project_manager,
        "site_supervisor": event.site_supervisor,

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
    }

      # ====================================================
    # RELATION DES FAITS
    # ====================================================

    facts = event.facts

    facts_data = None

    if facts is not None:
        facts_data = {
            column.name: getattr(
                facts,
                column.name,
            )
            for column
            in models.EventFacts.__table__.columns
        }

    # ====================================================
    # CLASSIFICATION
    # ====================================================

    classification = event.classification

    classification_data = None

    if classification is not None:

        def get_reference_labels(
            category: str,
            code: str | None,
            snapshot: str | None,
        ) -> dict:
            if not code:
                return {
                    "fr": snapshot,
                    "nl": None,
                    "en": None,
                    "pl": None,
                }

            reference = (
                db.query(
                    models.EventCodeReference
                )
                .filter(
                    models.EventCodeReference.category
                    == category,
                    models.EventCodeReference.code
                    == code,
                )
                .first()
            )

            if reference is None:
                return {
                    "fr": snapshot,
                    "nl": None,
                    "en": None,
                    "pl": None,
                }

            return {
                "fr": (
                    reference.label
                    or snapshot
                ),
                "nl": reference.label_nl,
                "en": reference.label_en,
                "pl": reference.label_pl,
            }

        deviation_labels = (
            get_reference_labels(
                "DEVIATION",
                classification.deviation_code,
                classification.deviation_label_snapshot,
            )
        )

        material_agent_labels = (
            get_reference_labels(
                "MATERIAL_AGENT",
                classification.material_agent_code,
                classification.material_agent_label_snapshot,
            )
        )

        injury_nature_labels = (
            get_reference_labels(
                "INJURY_NATURE",
                classification.injury_nature_code,
                classification.injury_nature_label_snapshot,
            )
        )

        injury_location_labels = (
            get_reference_labels(
                "INJURY_LOCATION",
                classification.injury_location_code,
                classification.injury_location_label_snapshot,
            )
        )

        classification_data = {
            column.name: getattr(
                classification,
                column.name,
            )
            for column
            in models.EventClassification.__table__.columns
        }

        classification_data.update({
            "deviation_label_fr":
                deviation_labels["fr"],
            "deviation_label_nl":
                deviation_labels["nl"],
            "deviation_label_en":
                deviation_labels["en"],
            "deviation_label_pl":
                deviation_labels["pl"],

            "material_agent_label_fr":
                material_agent_labels["fr"],
            "material_agent_label_nl":
                material_agent_labels["nl"],
            "material_agent_label_en":
                material_agent_labels["en"],
            "material_agent_label_pl":
                material_agent_labels["pl"],

            "injury_nature_label_fr":
                injury_nature_labels["fr"],
            "injury_nature_label_nl":
                injury_nature_labels["nl"],
            "injury_nature_label_en":
                injury_nature_labels["en"],
            "injury_nature_label_pl":
                injury_nature_labels["pl"],

            "injury_location_label_fr":
                injury_location_labels["fr"],
            "injury_location_label_nl":
                injury_location_labels["nl"],
            "injury_location_label_en":
                injury_location_labels["en"],
            "injury_location_label_pl":
                injury_location_labels["pl"],
        })

    # ====================================================
    # HEEPO
    # ====================================================

        # ====================================================
    # HEEPO
    # ====================================================

    heepo_items = (
        db.query(models.EventHeepoFactor)
        .filter(
            models.EventHeepoFactor.event_id
            == event_id
        )
        .order_by(
            models.EventHeepoFactor.id
        )
        .all()
    )

    heepo_data = [
        {
            "id": item.id,
            "family": item.family,
            "factor_code": (
                item.factor_code_snapshot
            ),

            # Libellé historique conservé
            "factor_label": (
                item.factor_label_snapshot
            ),

            # Référentiel multilingue actuel
            "factor_label_fr": (
                item.factor.label
                if item.factor
                else item.factor_label_snapshot
            ),
            "factor_label_nl": (
                item.factor.label_nl
                if item.factor
                else None
            ),
            "factor_label_en": (
                item.factor.label_en
                if item.factor
                else None
            ),
            "factor_label_pl": (
                item.factor.label_pl
                if item.factor
                else None
            ),

            "other_text": item.other_text,
            "is_na": item.is_na,
        }
        for item in heepo_items
    ]

    # ====================================================
    # PHOTOS
    # ====================================================

    photos = get_event_photos(
        db=db,
        event_id=event_id,
    )

    photos_data = [
        {
            "id": photo.id,
            "original_filename": (
                photo.original_filename
            ),
            "content_type": photo.content_type,
            "file_size": photo.file_size,
            "caption": photo.caption,
            "sort_order": photo.sort_order,
        }
        for photo in photos
    ]

    # ====================================================
    # ARBRE DES CAUSES
    # ====================================================

    cause_facts, cause_relations = (
        get_event_cause_tree(
            db=db,
            event_id=event_id,
        )
    )

    cause_tree_data = None

    if cause_facts or cause_relations:
        cause_levels = calculate_event_cause_levels(
            db=db,
            event_id=event_id,
        )

        cause_tree_data = {
            "facts": [
                {
                    "id": fact.id,
                    "fact_type": fact.fact_type,
                    "description": (
                        fact.description
                    ),
                    "sort_order": (
                        fact.sort_order
                    ),
                    "is_terminal": (
                        fact.is_terminal
                    ),
                    "level": cause_levels.get(
                        fact.id
                    ),
                }
                for fact in cause_facts
            ],
            "relations": [
                {
                    "id": relation.id,
                    "cause_fact_id": (
                        relation.cause_fact_id
                    ),
                    "effect_fact_id": (
                        relation.effect_fact_id
                    ),
                }
                for relation
                in cause_relations
            ],
        }
    # ====================================================
    # JUST CULTURE
    # ====================================================

        just_culture_data = None

    if event.analysis_type == "ADVANCED":
        try:
            (
                analysis,
                tree_version,
                current_node,
                history,
            ) = get_event_just_culture_analysis(
                db=db,
                event_id=event_id,
            )

            # ------------------------------------------------
            # Conclusion / recommandation multilingues
            # ------------------------------------------------

            conclusion_node = None

            if analysis.conclusion_code:
                conclusion_node = (
                    db.query(models.JustCultureNode)
                    .filter(
                        models.JustCultureNode.tree_version_id
                        == tree_version.id,
                        models.JustCultureNode.conclusion_code
                        == analysis.conclusion_code,
                    )
                    .first()
                )

            # ------------------------------------------------
            # Historique multilingue
            # ------------------------------------------------

            history_data = []

            for step in history:
                source_node = (
                    db.query(models.JustCultureNode)
                    .filter(
                        models.JustCultureNode.tree_version_id
                        == tree_version.id,
                        models.JustCultureNode.code
                        == step.node_code,
                    )
                    .first()
                )

                target_node = (
                    db.query(models.JustCultureNode)
                    .filter(
                        models.JustCultureNode.tree_version_id
                        == tree_version.id,
                        models.JustCultureNode.code
                        == step.target_node_code,
                    )
                    .first()
                )

                transition = None

                if (
                    source_node is not None
                    and target_node is not None
                ):
                    transition = (
                        db.query(
                            models.JustCultureTransition
                        )
                        .filter(
                            models.JustCultureTransition.source_node_id
                            == source_node.id,
                            models.JustCultureTransition.target_node_id
                            == target_node.id,
                        )
                        .first()
                    )

                history_data.append({
                    "step_order": step.step_order,
                    "node_code": step.node_code,

                    # Snapshots historiques FR
                    "question_text": (
                        step.question_text
                    ),
                    "answer_label": (
                        step.answer_label
                    ),

                    # Référentiel actuel multilingue
                    "question_text_fr": (
                        source_node.text
                        if source_node
                        else step.question_text
                    ),
                    "question_text_nl": (
                        source_node.text_nl
                        if source_node
                        else None
                    ),
                    "question_text_en": (
                        source_node.text_en
                        if source_node
                        else None
                    ),
                    "question_text_pl": (
                        source_node.text_pl
                        if source_node
                        else None
                    ),

                    "answer_label_fr": (
                        transition.answer_label
                        if transition
                        else step.answer_label
                    ),
                    "answer_label_nl": (
                        transition.answer_label_nl
                        if transition
                        else None
                    ),
                    "answer_label_en": (
                        transition.answer_label_en
                        if transition
                        else None
                    ),
                    "answer_label_pl": (
                        transition.answer_label_pl
                        if transition
                        else None
                    ),

                    "target_node_code": (
                        step.target_node_code
                    ),
                })

            just_culture_data = {
                "analysis_id": analysis.id,
                "status": analysis.status,

                "tree_code": tree_version.code,
                "tree_version": tree_version.version,

                "current_node_code": (
                    current_node.code
                    if current_node
                    else None
                ),

                "conclusion_code": (
                    analysis.conclusion_code
                ),

                # Snapshot historique
                "conclusion_label": (
                    analysis.conclusion_label
                ),

                # Référentiel multilingue
                "conclusion_label_fr": (
                    conclusion_node.conclusion_label
                    if conclusion_node
                    else analysis.conclusion_label
                ),
                "conclusion_label_nl": (
                    conclusion_node.conclusion_label_nl
                    if conclusion_node
                    else None
                ),
                "conclusion_label_en": (
                    conclusion_node.conclusion_label_en
                    if conclusion_node
                    else None
                ),
                "conclusion_label_pl": (
                    conclusion_node.conclusion_label_pl
                    if conclusion_node
                    else None
                ),

                "recommendation_code": (
                    analysis.recommendation_code
                ),

                # Snapshot historique
                "recommendation_label": (
                    analysis.recommendation_label
                ),

                # Référentiel multilingue
                "recommendation_label_fr": (
                    conclusion_node.recommendation_label
                    if conclusion_node
                    else analysis.recommendation_label
                ),
                "recommendation_label_nl": (
                    conclusion_node.recommendation_label_nl
                    if conclusion_node
                    else None
                ),
                "recommendation_label_en": (
                    conclusion_node.recommendation_label_en
                    if conclusion_node
                    else None
                ),
                "recommendation_label_pl": (
                    conclusion_node.recommendation_label_pl
                    if conclusion_node
                    else None
                ),

                "validated": analysis.validated,
                "validated_at": (
                    analysis.validated_at
                ),
                "validated_by_person_id": (
                    analysis.validated_by_person_id
                ),

                "history": history_data,
            }

        except ValueError:
            # Analyse Advanced sans Just Culture
            # encore démarrée.
            just_culture_data = None

    # ====================================================
    # ACTIONS
    # ====================================================

    actions = list(
        db.scalars(
            select(Action)
            .where(
                Action.event_id == event_id,
                Action.origin_type
                == "ACCIDENT",
            )
            .order_by(
                Action.due_date.asc(),
                Action.created_at.asc(),
                Action.id.asc(),
            )
        ).all()
    )

    actions_data = [
        {
            "id": action.id,
            "description": action.description,
            "action_type": action.action_type,
            "scope": action.scope,
            "process_code": (
                action.process_code
            ),

            "responsible_person_id": (
                action.responsible_person_id
            ),
            "responsible_text": (
                action.responsible_text
            ),

            "due_date": action.due_date,
            "priority": action.priority,
            "progress_percent": (
                action.progress_percent
            ),

            "resources": action.resources,
            "follow_up_indicator": (
                action.follow_up_indicator
            ),
        }
        for action in actions
    ]

    # ====================================================
    # SECTIONS À PUBLIER
    # ====================================================

    sections = {
        "facts": facts_data is not None,

        "classification": (
            classification_data
            is not None
        ),

        "photos": bool(
            photos_data
        ),

        "heepo": any(
            not item["is_na"]
            for item in heepo_data
        ),

        "cause_tree": (
            cause_tree_data
            is not None
        ),

        "just_culture": (
            just_culture_data
            is not None
        ),

        "actions": bool(
            actions_data
        ),
    }

    # ====================================================
    # RÉPONSE
    # ====================================================

    return {
        "event_id": event.id,
        "event_number": event.event_number,

        "event": event_data,
        "facts": facts_data,
        "classification": (
            classification_data
        ),

        "heepo": heepo_data,
        "photos": photos_data,

        "cause_tree": cause_tree_data,
        "just_culture": (
            just_culture_data
        ),

        "actions": actions_data,

        "sections": sections,
    }