from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from ... import models
from sqlalchemy import select

from ...database import SessionLocal
from ...schemas.just_culture import (
    JustCultureImportApplyResult,
    JustCultureImportPreview,
    JustCultureTreeImportFile,
    EventJustCultureStartResponse,
    EventJustCultureAnswerRequest,
    EventJustCultureAnswerResponse,
    EventJustCultureDetailResponse,
    EventJustCultureHistoryStep,
    EventJustCultureAvailableAnswer,
)
from ...services.audit import write_audit_log
from ...services.just_culture import (
    apply_just_culture_tree,
    validate_just_culture_tree,
    start_event_just_culture_analysis,
    answer_event_just_culture_question,
    get_event_just_culture_analysis,
    get_just_culture_available_answers,
    back_event_just_culture_question,
)
from ...services.session import require_write_session


router = APIRouter(
    prefix="/just-culture",
    tags=["Just Culture"],
)


# ========================================================
# JUST CULTURE — CONSTRUCTION DES RÉPONSES DISPONIBLES
# ========================================================

def build_available_answers(
    db,
    node,
) -> list[EventJustCultureAvailableAnswer]:

    if node is None or node.node_type != "QUESTION":
        return []

    transitions = get_just_culture_available_answers(
        db=db,
        node=node,
    )

    return [
        EventJustCultureAvailableAnswer(
            code=transition.answer_code,
            label=transition.answer_label,
            label_nl=transition.answer_label_nl,
            label_en=transition.answer_label_en,
            label_pl=transition.answer_label_pl,
            target_node_code=target_node.code,
            sort_order=transition.sort_order,
        )
        for transition in transitions
        if (
            transition.answer_code
            and (
                target_node := db.get(
                    type(node),
                    transition.target_node_id,
                )
            )
            is not None
        )
    ]


# ========================================================
# JUST CULTURE — IMPORT / PRÉVISUALISATION
# ========================================================

@router.post(
    "/import/preview",
    response_model=JustCultureImportPreview,
)
def preview_just_culture_import(
    data: JustCultureTreeImportFile,
) -> JustCultureImportPreview:
    return validate_just_culture_tree(data)


# ========================================================
# JUST CULTURE — IMPORT / APPLICATION
# ========================================================

@router.post(
    "/import/apply",
    response_model=JustCultureImportApplyResult,
)
def apply_just_culture_import(
    data: JustCultureTreeImportFile,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        result = apply_just_culture_tree(
            db=db,
            data=data,
        )

        if result.action != "UNCHANGED":
            write_audit_log(
                db=db,
                session=session,
                action=result.action,
                entity_type="JUST_CULTURE_TREE",
                entity_id=result.tree_version_id,
                after_data={
                    "tree_code": result.tree_code,
                    "tree_version": result.tree_version,
                    "nodes_created": result.nodes_created,
                    "transitions_created": (
                        result.transitions_created
                    ),
                },
                details=(
                    "Import de l'arbre décisionnel "
                    "Just Culture."
                ),
            )

        db.commit()

        return result

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ========================================================
# JUST CULTURE — DÉMARRER UNE ANALYSE
# ========================================================

@router.post(
    "/events/{event_id}/start",
    response_model=EventJustCultureStartResponse,
)
def start_event_just_culture(
    event_id: int,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        analysis, tree_version, root_node = (
            start_event_just_culture_analysis(
                db=db,
                event_id=event_id,
            )
        )

        available_answers = build_available_answers(
            db=db,
            node=root_node,
        )

        write_audit_log(
            db=db,
            session=session,
            action="START",
            entity_type="EVENT_JUST_CULTURE_ANALYSIS",
            entity_id=analysis.id,
            after_data={
                "event_id": event_id,
                "tree_version_id": tree_version.id,
                "tree_code": tree_version.code,
                "tree_version": tree_version.version,
                "current_node_code": root_node.code,
                "status": analysis.status,
            },
            details="Démarrage de l'analyse Just Culture.",
        )

        db.commit()

        return EventJustCultureStartResponse(
            analysis_id=analysis.id,
            event_id=event_id,
            status=analysis.status,
            tree_version_id=tree_version.id,
            tree_code=tree_version.code,
            tree_version=tree_version.version,

            current_node_code=root_node.code,
            current_node_text=root_node.text,
            current_node_text_nl=root_node.text_nl,
            current_node_text_en=root_node.text_en,
            current_node_text_pl=root_node.text_pl,
            current_node_type=root_node.node_type,

            available_answers=available_answers,
        )

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ========================================================
# JUST CULTURE — RÉPONDRE À UNE QUESTION
# ========================================================

@router.post(
    "/events/{event_id}/answer",
    response_model=EventJustCultureAnswerResponse,
)
def answer_event_just_culture(
    event_id: int,
    payload: EventJustCultureAnswerRequest,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        (
            analysis,
            answer_record,
            current_node,
            target_node,
        ) = answer_event_just_culture_question(
            db=db,
            event_id=event_id,
            answer_code=payload.answer_code,
        )

        available_answers = build_available_answers(
            db=db,
            node=(
                target_node
                if target_node.node_type == "QUESTION"
                else None
            ),
        )

        write_audit_log(
            db=db,
            session=session,
            action="ANSWER",
            entity_type="EVENT_JUST_CULTURE_ANALYSIS",
            entity_id=analysis.id,
            after_data={
                "event_id": event_id,
                "step_order": answer_record.step_order,
                "node_code": current_node.code,
                "answer_code": payload.answer_code,
                "answer": answer_record.answer_label,
                "target_node_code": target_node.code,
                "status": analysis.status,
                "conclusion_code": analysis.conclusion_code,
                "recommendation_code": (
                    analysis.recommendation_code
                ),
            },
            details=(
                "Réponse enregistrée dans "
                "l'analyse Just Culture."
            ),
        )

        db.commit()

        is_question = (
            target_node.node_type == "QUESTION"
        )

        return EventJustCultureAnswerResponse(
            analysis_id=analysis.id,
            event_id=event_id,
            status=analysis.status,
            step_order=answer_record.step_order,

            answered_node_code=current_node.code,

            question_text=current_node.text,
            question_text_nl=current_node.text_nl,
            question_text_en=current_node.text_en,
            question_text_pl=current_node.text_pl,

            answer_code=payload.answer_code.strip().upper(),
            answer_label=answer_record.answer_label,
            answer_label_nl=(
                next(
                    (
                        transition.answer_label_nl
                        for transition
                        in get_just_culture_available_answers(
                            db=db,
                            node=current_node,
                        )
                        if transition.answer_code
                        == payload.answer_code.strip().upper()
                    ),
                    None,
                )
            ),
            answer_label_en=(
                next(
                    (
                        transition.answer_label_en
                        for transition
                        in get_just_culture_available_answers(
                            db=db,
                            node=current_node,
                        )
                        if transition.answer_code
                        == payload.answer_code.strip().upper()
                    ),
                    None,
                )
            ),
            answer_label_pl=(
                next(
                    (
                        transition.answer_label_pl
                        for transition
                        in get_just_culture_available_answers(
                            db=db,
                            node=current_node,
                        )
                        if transition.answer_code
                        == payload.answer_code.strip().upper()
                    ),
                    None,
                )
            ),

            current_node_code=(
                target_node.code
                if is_question
                else None
            ),
            current_node_text=(
                target_node.text
                if is_question
                else None
            ),
            current_node_text_nl=(
                target_node.text_nl
                if is_question
                else None
            ),
            current_node_text_en=(
                target_node.text_en
                if is_question
                else None
            ),
            current_node_text_pl=(
                target_node.text_pl
                if is_question
                else None
            ),
            current_node_type=(
                target_node.node_type
                if is_question
                else None
            ),

            available_answers=available_answers,

            conclusion_code=analysis.conclusion_code,
            conclusion_label=analysis.conclusion_label,
            conclusion_label_nl=(
                target_node.conclusion_label_nl
                if not is_question
                else None
            ),
            conclusion_label_en=(
                target_node.conclusion_label_en
                if not is_question
                else None
            ),
            conclusion_label_pl=(
                target_node.conclusion_label_pl
                if not is_question
                else None
            ),

            recommendation_code=(
                analysis.recommendation_code
            ),
            recommendation_label=(
                analysis.recommendation_label
            ),
            recommendation_label_nl=(
                target_node.recommendation_label_nl
                if not is_question
                else None
            ),
            recommendation_label_en=(
                target_node.recommendation_label_en
                if not is_question
                else None
            ),
            recommendation_label_pl=(
                target_node.recommendation_label_pl
                if not is_question
                else None
            ),
        )

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

# ========================================================
# JUST CULTURE — RETOUR À LA QUESTION PRÉCÉDENTE
# ========================================================

@router.post(
    "/events/{event_id}/back",
    response_model=EventJustCultureDetailResponse,
)
def back_event_just_culture(
    event_id: int,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        analysis, previous_node = (
            back_event_just_culture_question(
                db=db,
                event_id=event_id,
            )
        )

        available_answers = build_available_answers(
            db=db,
            node=previous_node,
        )

        write_audit_log(
            db=db,
            session=session,
            action="BACK",
            entity_type="EVENT_JUST_CULTURE_ANALYSIS",
            entity_id=analysis.id,
            after_data={
                "event_id": event_id,
                "current_node_code": previous_node.code,
                "status": analysis.status,
            },
            details=(
                "Retour à la question précédente "
                "dans l'analyse Just Culture."
            ),
        )

        db.commit()

        return EventJustCultureDetailResponse(
            analysis_id=analysis.id,
            event_id=analysis.event_id,
            status=analysis.status,

            tree_version_id=analysis.tree_version_id,
            tree_code="",
            tree_version="",

            current_node_code=previous_node.code,
            current_node_text=previous_node.text,
            current_node_text_nl=previous_node.text_nl,
            current_node_text_en=previous_node.text_en,
            current_node_text_pl=previous_node.text_pl,
            current_node_type=previous_node.node_type,

            available_answers=available_answers,

            conclusion_code=None,
            conclusion_label=None,
            conclusion_label_nl=None,
            conclusion_label_en=None,
            conclusion_label_pl=None,

            recommendation_code=None,
            recommendation_label=None,
            recommendation_label_nl=None,
            recommendation_label_en=None,
            recommendation_label_pl=None,

            completed_at=None,
            history=[],
        )

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

# ========================================================
# JUST CULTURE — VALIDER UNE ANALYSE
# ========================================================

@router.post(
    "/events/{event_id}/validate",
)
def validate_event_just_culture(
    event_id: int,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        analysis = db.scalar(
            select(models.EventJustCultureAnalysis)
            .where(
                models.EventJustCultureAnalysis.event_id
                == event_id
            )
        )

        if analysis is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Aucune analyse Just Culture "
                    "n'existe pour cet événement."
                ),
            )

        if analysis.status != "COMPLETED":
            raise HTTPException(
                status_code=400,
                detail=(
                    "L'analyse Just Culture doit atteindre "
                    "une conclusion avant validation."
                ),
            )

        if analysis.validated:
            raise HTTPException(
                status_code=400,
                detail="L'analyse Just Culture est déjà validée.",
            )

        analysis.validated = True
        analysis.validated_at = datetime.now()
        analysis.validated_by_person_id = session["person_id"]

        write_audit_log(
            db=db,
            session=session,
            action="VALIDATE",
            entity_type="EVENT_JUST_CULTURE_ANALYSIS",
            entity_id=analysis.id,
            after_data={
                "event_id": event_id,
                "status": analysis.status,
                "validated": True,
                "validated_at": (
                    analysis.validated_at.isoformat()
                ),
                "validated_by_person_id": (
                    analysis.validated_by_person_id
                ),
                "conclusion_code": analysis.conclusion_code,
                "recommendation_code": (
                    analysis.recommendation_code
                ),
            },
            details="Validation de l'analyse Just Culture.",
        )

        db.commit()

        return {
            "analysis_id": analysis.id,
            "event_id": event_id,
            "validated": analysis.validated,
            "validated_at": analysis.validated_at,
            "validated_by_person_id": (
                analysis.validated_by_person_id
            ),
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

# ========================================================
# JUST CULTURE — RÉOUVRIR UNE ANALYSE VALIDÉE
# ========================================================

@router.post(
    "/events/{event_id}/reopen",
)
def reopen_event_just_culture(
    event_id: int,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        analysis = db.scalar(
            select(models.EventJustCultureAnalysis)
            .where(
                models.EventJustCultureAnalysis.event_id
                == event_id
            )
        )

        if analysis is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Aucune analyse Just Culture "
                    "n'existe pour cet événement."
                ),
            )

        if not analysis.validated:
            raise HTTPException(
                status_code=400,
                detail=(
                    "L'analyse Just Culture "
                    "n'est pas validée."
                ),
            )

        previous_validation = {
            "validated": analysis.validated,
            "validated_at": (
                analysis.validated_at.isoformat()
                if analysis.validated_at
                else None
            ),
            "validated_by_person_id": (
                analysis.validated_by_person_id
            ),
            "conclusion_code": analysis.conclusion_code,
            "recommendation_code": (
                analysis.recommendation_code
            ),
        }

        analysis.validated = False
        analysis.validated_at = None
        analysis.validated_by_person_id = None

        write_audit_log(
            db=db,
            session=session,
            action="REOPEN",
            entity_type="EVENT_JUST_CULTURE_ANALYSIS",
            entity_id=analysis.id,
            before_data=previous_validation,
            after_data={
                "event_id": event_id,
                "status": analysis.status,
                "validated": False,
                "validated_at": None,
                "validated_by_person_id": None,
                "conclusion_code": analysis.conclusion_code,
                "recommendation_code": (
                    analysis.recommendation_code
                ),
            },
            details=(
                "Réouverture de l'analyse Just Culture "
                "après validation."
            ),
        )

        db.commit()

        return {
            "analysis_id": analysis.id,
            "event_id": event_id,
            "validated": analysis.validated,
            "validated_at": analysis.validated_at,
            "validated_by_person_id": (
                analysis.validated_by_person_id
            ),
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

# ========================================================
# JUST CULTURE — CONSULTER UNE ANALYSE
# ========================================================

@router.get(
    "/events/{event_id}",
    response_model=EventJustCultureDetailResponse,
)
def get_event_just_culture(
    event_id: int,
):
    db = SessionLocal()

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

        available_answers = build_available_answers(
            db=db,
            node=current_node,
        )

        conclusion_node = None

        if (
            analysis.status == "COMPLETED"
            and analysis.conclusion_code
        ):
            conclusion_node = db.scalar(
                select(models.JustCultureNode)
                .where(
                    models.JustCultureNode.tree_version_id
                    == analysis.tree_version_id,
                    models.JustCultureNode.conclusion_code
                    == analysis.conclusion_code,
                )
            )      

        # ========================================================
        # JUST CULTURE — HISTORIQUE MULTILINGUE
        # ========================================================

        translated_history = []

        for item in history:
            source_node = db.scalar(
                select(models.JustCultureNode)
                .where(
                    models.JustCultureNode.tree_version_id
                    == analysis.tree_version_id,
                    models.JustCultureNode.code
                    == item.node_code,
                )
            )

            source_transition = db.scalar(
                select(models.JustCultureTransition)
                .where(
                    models.JustCultureTransition.source_node_id
                    == source_node.id,
                    models.JustCultureTransition.target_node_id
                    == db.scalar(
                        select(models.JustCultureNode.id)
                        .where(
                            models.JustCultureNode.tree_version_id
                            == analysis.tree_version_id,
                            models.JustCultureNode.code
                            == item.target_node_code,
                        )
                    ),
                )
            ) if source_node is not None else None

            translated_history.append(
                EventJustCultureHistoryStep(
                    step_order=item.step_order,
                    node_code=item.node_code,

                    question_text=item.question_text,
                    question_text_nl=(
                        source_node.text_nl
                        if source_node is not None
                        else None
                    ),
                    question_text_en=(
                        source_node.text_en
                        if source_node is not None
                        else None
                    ),
                    question_text_pl=(
                        source_node.text_pl
                        if source_node is not None
                        else None
                    ),

                    answer_label=item.answer_label,
                                       answer_label_nl=(
                        source_transition.answer_label_nl
                        if source_transition is not None
                        else None
                    ),
                    answer_label_en=(
                        source_transition.answer_label_en
                        if source_transition is not None
                        else None
                    ),
                    answer_label_pl=(
                        source_transition.answer_label_pl
                        if source_transition is not None
                        else None
                    ),

                    target_node_code=item.target_node_code,
                )
            )

        return EventJustCultureDetailResponse(
            analysis_id=analysis.id,
            event_id=analysis.event_id,
            status=analysis.status,

            tree_version_id=tree_version.id,
            tree_code=tree_version.code,
            tree_version=tree_version.version,

            current_node_code=(
                current_node.code
                if current_node
                else None
            ),
            current_node_text=(
                current_node.text
                if current_node
                else None
            ),
            current_node_text_nl=(
                current_node.text_nl
                if current_node
                else None
            ),
            current_node_text_en=(
                current_node.text_en
                if current_node
                else None
            ),
            current_node_text_pl=(
                current_node.text_pl
                if current_node
                else None
            ),
            current_node_type=(
                current_node.node_type
                if current_node
                else None
            ),

            available_answers=available_answers,

            conclusion_code=analysis.conclusion_code,
            conclusion_label=analysis.conclusion_label,
            conclusion_label_nl=(
                conclusion_node.conclusion_label_nl
                if conclusion_node
                else None
            ),
            conclusion_label_en=(
                conclusion_node.conclusion_label_en
                if conclusion_node
                else None
            ),
            conclusion_label_pl=(
                conclusion_node.conclusion_label_pl
                if conclusion_node
                else None
            ),

            recommendation_code=(
                analysis.recommendation_code
            ),
            recommendation_label=(
                analysis.recommendation_label
            ),
            recommendation_label_nl=(
                conclusion_node.recommendation_label_nl
                if conclusion_node
                else None
            ),
            recommendation_label_en=(
                conclusion_node.recommendation_label_en
                if conclusion_node
                else None
            ),
            recommendation_label_pl=(
                conclusion_node.recommendation_label_pl
                if conclusion_node
                else None
            ),

            completed_at=analysis.completed_at,

            validated=analysis.validated,
            validated_at=analysis.validated_at,
            validated_by_person_id=(
                analysis.validated_by_person_id
            ),

            history=translated_history,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    finally:
        db.close()