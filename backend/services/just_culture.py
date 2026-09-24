from collections import defaultdict

from sqlalchemy import select

from datetime import datetime

from ..schemas.just_culture import (
    JustCultureImportIssue,
    JustCultureImportPreview,
    JustCultureTreeImportFile,
)

from sqlalchemy.orm import Session

from .. import models
from ..schemas.just_culture import JustCultureImportApplyResult


def validate_just_culture_tree(
    data: JustCultureTreeImportFile,
) -> JustCultureImportPreview:

    issues: list[JustCultureImportIssue] = []

    node_codes = [node.code for node in data.nodes]
    node_code_set = set(node_codes)

    nodes_by_code = {
        node.code: node
        for node in data.nodes
    }

    outgoing = defaultdict(list)

    for transition in data.transitions:
        outgoing[transition.source].append(transition.target)

    question_count = sum(
        1
        for node in data.nodes
        if node.node_type == "QUESTION"
    )

    conclusion_count = sum(
        1
        for node in data.nodes
        if node.node_type == "CONCLUSION"
    )

    # ---------------------------------------------------------
    # 1. Codes de nœuds uniques
    # ---------------------------------------------------------
    seen_codes = set()
    duplicates = set()

    for code in node_codes:
        if code in seen_codes:
            duplicates.add(code)
        seen_codes.add(code)

    for code in sorted(duplicates):
        issues.append(
            JustCultureImportIssue(
                level="ERROR",
                code="DUPLICATE_NODE",
                message=f"Nœud dupliqué : {code}",
            )
        )

    # ---------------------------------------------------------
    # 2. Racine existante
    # ---------------------------------------------------------
    if data.tree.root_node_code not in node_code_set:
        issues.append(
            JustCultureImportIssue(
                level="ERROR",
                code="ROOT_NOT_FOUND",
                message=(
                    f"Le nœud racine {data.tree.root_node_code} "
                    "n'existe pas dans l'arbre."
                ),
            )
        )

    # ---------------------------------------------------------
    # 3. Types de nœuds
    # ---------------------------------------------------------
    allowed_types = {"QUESTION", "CONCLUSION"}

    for node in data.nodes:
        if node.node_type not in allowed_types:
            issues.append(
                JustCultureImportIssue(
                    level="ERROR",
                    code="INVALID_NODE_TYPE",
                    message=(
                        f"{node.code} possède un type invalide : "
                        f"{node.node_type}"
                    ),
                )
            )
    # ---------------------------------------------------------
    # 3 bis. Codes métier des réponses
    # ---------------------------------------------------------
    legacy_answer_codes = {
        "OUI": "YES",
        "NON": "NO",
    }

    for transition in data.transitions:
        answer_code = transition.answer_code

        if not answer_code:
            answer_code = legacy_answer_codes.get(
                transition.answer.strip().upper()
            )

        if not answer_code:
            issues.append(
                JustCultureImportIssue(
                    level="ERROR",
                    code="MISSING_ANSWER_CODE",
                    message=(
                        f"La transition {transition.source} → "
                        f"{transition.target} ne possède pas "
                        "de code de réponse stable."
                    ),
                )
            )

    # ---------------------------------------------------------
    # 4. Sources et destinations des transitions
    # ---------------------------------------------------------
    transitions_valid = True

    for transition in data.transitions:

        if transition.source not in node_code_set:
            transitions_valid = False

            issues.append(
                JustCultureImportIssue(
                    level="ERROR",
                    code="TRANSITION_SOURCE_NOT_FOUND",
                    message=(
                        f"Source inexistante : "
                        f"{transition.source}"
                    ),
                )
            )

        if transition.target not in node_code_set:
            transitions_valid = False

            issues.append(
                JustCultureImportIssue(
                    level="ERROR",
                    code="TRANSITION_TARGET_NOT_FOUND",
                    message=(
                        f"Destination inexistante : "
                        f"{transition.target}"
                    ),
                )
            )

    # ---------------------------------------------------------
    # 4 bis. Codes de réponse uniques par question
    # ---------------------------------------------------------
    answer_codes_by_source = defaultdict(set)

    for transition in data.transitions:
        answer_code = transition.answer_code

        if not answer_code:
            answer_code = legacy_answer_codes.get(
                transition.answer.strip().upper()
            )

        if not answer_code:
            continue

        normalized_code = answer_code.strip().upper()

        if normalized_code in answer_codes_by_source[
            transition.source
        ]:
            issues.append(
                JustCultureImportIssue(
                    level="ERROR",
                    code="DUPLICATE_ANSWER_CODE",
                    message=(
                        f"La question {transition.source} possède "
                        f"plusieurs transitions avec le code "
                        f"'{normalized_code}'."
                    ),
                )
            )

        answer_codes_by_source[
            transition.source
        ].add(normalized_code)

    # ---------------------------------------------------------
    # 5. Une QUESTION doit posséder au moins une sortie
    # ---------------------------------------------------------
    for node in data.nodes:
        if (
            node.node_type == "QUESTION"
            and node.code not in outgoing
        ):
            issues.append(
                JustCultureImportIssue(
                    level="ERROR",
                    code="QUESTION_WITHOUT_TRANSITION",
                    message=(
                        f"La question {node.code} "
                        "ne possède aucune transition sortante."
                    ),
                )
            )

    # ---------------------------------------------------------
    # 6. Une CONCLUSION ne doit pas posséder de sortie
    # ---------------------------------------------------------
    for node in data.nodes:
        if (
            node.node_type == "CONCLUSION"
            and node.code in outgoing
        ):
            issues.append(
                JustCultureImportIssue(
                    level="ERROR",
                    code="CONCLUSION_WITH_TRANSITION",
                    message=(
                        f"La conclusion {node.code} "
                        "possède au moins une transition sortante."
                    ),
                )
            )

    # ---------------------------------------------------------
    # 7. Données obligatoires des conclusions
    # ---------------------------------------------------------
    for node in data.nodes:
        if node.node_type != "CONCLUSION":
            continue

        if not node.conclusion_code or not node.conclusion_label:
            issues.append(
                JustCultureImportIssue(
                    level="ERROR",
                    code="INCOMPLETE_CONCLUSION",
                    message=(
                        f"La conclusion {node.code} "
                        "ne possède pas de code ou de libellé."
                    ),
                )
            )

        if not node.recommendation_code or not node.recommendation_label:
            issues.append(
                JustCultureImportIssue(
                    level="WARNING",
                    code="MISSING_RECOMMENDATION",
                    message=(
                        f"La conclusion {node.code} "
                        "ne possède pas de recommandation."
                    ),
                )
            )

    # ---------------------------------------------------------
    # 8. Parcours depuis la racine :
    #    - nœuds inaccessibles
    #    - cycles
    # ---------------------------------------------------------
    if (
        data.tree.root_node_code in node_code_set
        and transitions_valid
    ):

        visited = set()
        active_path = set()
        cycle_nodes = set()

        def walk(node_code: str) -> None:

            if node_code in active_path:
                cycle_nodes.add(node_code)
                return

            if node_code in visited:
                return

            visited.add(node_code)
            active_path.add(node_code)

            for target in outgoing.get(node_code, []):
                walk(target)

            active_path.remove(node_code)

        walk(data.tree.root_node_code)

        for code in sorted(cycle_nodes):
            issues.append(
                JustCultureImportIssue(
                    level="ERROR",
                    code="CYCLE_DETECTED",
                    message=(
                        f"Un cycle a été détecté "
                        f"au niveau du nœud {code}."
                    ),
                )
            )

        unreachable = node_code_set - visited

        for code in sorted(unreachable):
            issues.append(
                JustCultureImportIssue(
                    level="ERROR",
                    code="UNREACHABLE_NODE",
                    message=(
                        f"Le nœud {code} n'est pas accessible "
                        "depuis la racine."
                    ),
                )
            )

    # ---------------------------------------------------------
    # Résultat
    # ---------------------------------------------------------
    return JustCultureImportPreview(
        valid=not any(
            issue.level == "ERROR"
            for issue in issues
        ),
        tree_code=data.tree.code,
        tree_version=data.tree.version,
        root_node_code=data.tree.root_node_code,
        node_count=len(data.nodes),
        question_count=question_count,
        conclusion_count=conclusion_count,
        transition_count=len(data.transitions),
        issues=issues,
    )

def apply_just_culture_tree(
    db: Session,
    data: JustCultureTreeImportFile,
) -> JustCultureImportApplyResult:

    # ---------------------------------------------------------
    # 1. Validation complète avant toute écriture
    # ---------------------------------------------------------
    preview = validate_just_culture_tree(data)

    if not preview.valid:
        errors = [
            issue.message
            for issue in preview.issues
            if issue.level == "ERROR"
        ]

        raise ValueError(
            "Import Just Culture invalide : "
            + " | ".join(errors)
        )

    # ---------------------------------------------------------
    # 2. Vérifier si cette version existe déjà
    # ---------------------------------------------------------
    existing = (
        db.query(models.JustCultureTreeVersion)
        .filter(
            models.JustCultureTreeVersion.code == data.tree.code,
            models.JustCultureTreeVersion.version == data.tree.version,
        )
        .first()
    )

    if existing:
        node_count = (
            db.query(models.JustCultureNode)
            .filter(
                models.JustCultureNode.tree_version_id == existing.id
            )
            .count()
        )

        transition_count = (
            db.query(models.JustCultureTransition)
            .join(
                models.JustCultureNode,
                models.JustCultureTransition.source_node_id
                == models.JustCultureNode.id,
            )
            .filter(
                models.JustCultureNode.tree_version_id == existing.id
            )
            .count()
        )

        return JustCultureImportApplyResult(
            success=True,
            action="UNCHANGED",
            tree_version_id=existing.id,
            tree_code=existing.code,
            tree_version=existing.version,
            nodes_created=0,
            transitions_created=0,
            message=(
                "Cette version de l'arbre Just Culture "
                f"existe déjà ({node_count} nœuds, "
                f"{transition_count} transitions)."
            ),
        )

    # ---------------------------------------------------------
    # 3. Créer la version de l'arbre
    # ---------------------------------------------------------
    tree_version = models.JustCultureTreeVersion(
        code=data.tree.code,
        name=data.tree.name,
        name_nl=data.tree.name_nl,
        name_en=data.tree.name_en,
        version=data.tree.version,
        language=data.tree.language,
        root_node_code=data.tree.root_node_code,
        description=data.tree.description,
        description_nl=data.tree.description_nl,
        description_en=data.tree.description_en,
        source_title=data.tree.source_title,
        source_author=data.tree.source_author,
        source_organization=data.tree.source_organization,
        source_reference=data.tree.source_reference,
        source_url=data.tree.source_url,
        active=data.tree.active,
    )

    db.add(tree_version)
    db.flush()

    # ---------------------------------------------------------
    # 4. Créer les nœuds
    # ---------------------------------------------------------
    created_nodes = {}

    for node_data in data.nodes:

        node = models.JustCultureNode(
            tree_version_id=tree_version.id,
            code=node_data.code,
            text=node_data.text,
            text_nl=node_data.text_nl,
            text_en=node_data.text_en,
            text_pl=node_data.text_pl,
            node_type=node_data.node_type,
            conclusion_code=node_data.conclusion_code,
            conclusion_label=node_data.conclusion_label,
            conclusion_label_nl=node_data.conclusion_label_nl,
            conclusion_label_en=node_data.conclusion_label_en,
            conclusion_label_pl=node_data.conclusion_label_pl,
            recommendation_code=node_data.recommendation_code,
            recommendation_label=node_data.recommendation_label,
            recommendation_label_nl=(
                node_data.recommendation_label_nl
            ),
            recommendation_label_en=(
                node_data.recommendation_label_en
            ),
            recommendation_label_pl=(
                node_data.recommendation_label_pl
            ),
            active=node_data.active,
        )

        db.add(node)
        db.flush()

        created_nodes[node_data.code] = node

    # ---------------------------------------------------------
    # 5. Créer les transitions
    # ---------------------------------------------------------
    legacy_answer_codes = {
        "OUI": "YES",
        "NON": "NO",
    }

    for transition_data in data.transitions:

        answer_code = transition_data.answer_code

        if not answer_code:
            answer_code = legacy_answer_codes.get(
                transition_data.answer.strip().upper()
            )

        if not answer_code:
            raise ValueError(
                "Code de réponse stable introuvable pour "
                f"{transition_data.source} → "
                f"{transition_data.target}."
            )

        transition = models.JustCultureTransition(
            source_node_id=created_nodes[
                transition_data.source
            ].id,
            answer_code=answer_code.strip().upper(),
            answer_label=transition_data.answer,
            answer_label_nl=transition_data.answer_nl,
            answer_label_en=transition_data.answer_en,
            answer_label_pl=transition_data.answer_pl,
            target_node_id=created_nodes[
                transition_data.target
            ].id,
            sort_order=transition_data.sort_order,
            active=True,
        )

        db.add(transition)

    # ---------------------------------------------------------
    # 6. Transaction
    # ---------------------------------------------------------
    db.flush()
    db.refresh(tree_version)  

    return JustCultureImportApplyResult(
        success=True,
        action="CREATED",
        tree_version_id=tree_version.id,
        tree_code=tree_version.code,
        tree_version=tree_version.version,
        nodes_created=len(data.nodes),
        transitions_created=len(data.transitions),
        message="Arbre Just Culture importé avec succès.",
    )

# ========================================================
# JUST CULTURE — RÉPONSES DISPONIBLES
# ========================================================

def get_just_culture_available_answers(
    db: Session,
    node: models.JustCultureNode,
):
    transitions = db.scalars(
        select(models.JustCultureTransition)
        .where(
            models.JustCultureTransition.source_node_id
            == node.id,
            models.JustCultureTransition.active.is_(True),
        )
        .order_by(
            models.JustCultureTransition.sort_order,
            models.JustCultureTransition.id,
        )
    ).all()

    return transitions

def start_event_just_culture_analysis(
    db: Session,
    event_id: int,
):
    # ---------------------------------------------------------
    # 1. Vérifier l'événement
    # ---------------------------------------------------------
    event = db.get(models.Event, event_id)

    if event is None:
        raise ValueError("Événement introuvable.")

    # ---------------------------------------------------------
    # 2. Just Culture uniquement pour une analyse approfondie
    # ---------------------------------------------------------
    if event.analysis_type != "ADVANCED":
        raise ValueError(
            "L'analyse Just Culture nécessite "
            "une analyse approfondie (ADVANCED)."
        )

    # ---------------------------------------------------------
    # 3. Une seule analyse Just Culture par événement
    # ---------------------------------------------------------
    existing = db.scalar(
        select(models.EventJustCultureAnalysis)
        .where(
            models.EventJustCultureAnalysis.event_id == event_id
        )
    )

    if existing is not None:
        raise ValueError(
            "Une analyse Just Culture existe déjà "
            "pour cet événement."
        )

    # ---------------------------------------------------------
    # 4. Chercher l'arbre actif
    # ---------------------------------------------------------
    tree_version = db.scalar(
        select(models.JustCultureTreeVersion)
        .where(
            models.JustCultureTreeVersion.active.is_(True)
        )
        .order_by(
            models.JustCultureTreeVersion.id.desc()
        )
    )

    if tree_version is None:
        raise ValueError(
            "Aucun arbre Just Culture actif n'est disponible."
        )

    if not tree_version.root_node_code:
        raise ValueError(
            "L'arbre Just Culture actif ne possède pas de racine."
        )

    # ---------------------------------------------------------
    # 5. Vérifier la racine
    # ---------------------------------------------------------
    root_node = db.scalar(
        select(models.JustCultureNode)
        .where(
            models.JustCultureNode.tree_version_id
            == tree_version.id,
            models.JustCultureNode.code
            == tree_version.root_node_code,
            models.JustCultureNode.active.is_(True),
        )
    )

    if root_node is None:
        raise ValueError(
            "Le nœud racine de l'arbre Just Culture "
            "est introuvable ou inactif."
        )

    if root_node.node_type != "QUESTION":
        raise ValueError(
            "Le nœud racine de l'arbre Just Culture "
            "doit être une question."
        )

    # ---------------------------------------------------------
    # 6. Créer l'analyse
    # ---------------------------------------------------------
    analysis = models.EventJustCultureAnalysis(
        event_id=event.id,
        tree_version_id=tree_version.id,
        status="IN_PROGRESS",
        current_node_code=root_node.code,
    )

    db.add(analysis)
    db.flush()

    return analysis, tree_version, root_node
def answer_event_just_culture_question(
    db: Session,
    event_id: int,
    answer_code: str,
):
    # ---------------------------------------------------------
    # 1. Retrouver l'analyse de l'événement
    # ---------------------------------------------------------
    analysis = db.scalar(
        select(models.EventJustCultureAnalysis)
        .where(
            models.EventJustCultureAnalysis.event_id == event_id
        )
    )

    if analysis is None:
        raise ValueError(
            "Aucune analyse Just Culture n'existe pour cet événement."
        )

    if analysis.status != "IN_PROGRESS":
        raise ValueError(
            "Cette analyse Just Culture est déjà terminée."
        )

    if not analysis.current_node_code:
        raise ValueError(
            "L'analyse Just Culture ne possède pas de nœud courant."
        )

    # ---------------------------------------------------------
    # 2. Retrouver la question courante
    # ---------------------------------------------------------
    current_node = db.scalar(
        select(models.JustCultureNode)
        .where(
            models.JustCultureNode.tree_version_id
            == analysis.tree_version_id,
            models.JustCultureNode.code
            == analysis.current_node_code,
            models.JustCultureNode.active.is_(True),
        )
    )

    if current_node is None:
        raise ValueError(
            "Le nœud courant de l'analyse Just Culture est introuvable."
        )

    if current_node.node_type != "QUESTION":
        raise ValueError(
            "Le nœud courant n'est pas une question."
        )

    # ---------------------------------------------------------
    # 3. Normaliser et rechercher la transition
    # ---------------------------------------------------------
    normalized_answer_code = answer_code.strip().upper()

    if not normalized_answer_code:
        raise ValueError(
            "Le code de réponse ne peut pas être vide."
        )

    transition = db.scalar(
        select(models.JustCultureTransition)
        .where(
            models.JustCultureTransition.source_node_id
            == current_node.id,
            models.JustCultureTransition.answer_code
            == normalized_answer_code,
            models.JustCultureTransition.active.is_(True),
        )
    )

    if transition is None:
        raise ValueError(
            f"La réponse '{normalized_answer_code}' "
            f"n'est pas disponible pour le nœud "
            f"{current_node.code}."
        )
    
    # ---------------------------------------------------------
    # 4. Retrouver le nœud cible
    # ---------------------------------------------------------
    target_node = db.get(
        models.JustCultureNode,
        transition.target_node_id,
    )

    if target_node is None or not target_node.active:
        raise ValueError(
            "Le nœud cible de la transition est introuvable ou inactif."
        )

    # ---------------------------------------------------------
    # 5. Déterminer le numéro de l'étape
    # ---------------------------------------------------------
    previous_steps = db.scalars(
        select(models.EventJustCultureAnswer)
        .where(
            models.EventJustCultureAnswer.analysis_id
            == analysis.id
        )
    ).all()

    step_order = len(previous_steps) + 1

    # ---------------------------------------------------------
    # 6. Enregistrer le snapshot question/réponse
    # ---------------------------------------------------------
    answer_record = models.EventJustCultureAnswer(
        analysis_id=analysis.id,
        step_order=step_order,
        node_code=current_node.code,
        question_text=current_node.text,
        answer_label=transition.answer_label,
        target_node_code=target_node.code,
    )

    db.add(answer_record)

    # ---------------------------------------------------------
    # 7. Continuer ou terminer l'analyse
    # ---------------------------------------------------------
    if target_node.node_type == "QUESTION":
        analysis.current_node_code = target_node.code

    elif target_node.node_type == "CONCLUSION":
        analysis.status = "COMPLETED"
        analysis.current_node_code = None

        analysis.conclusion_code = target_node.conclusion_code
        analysis.conclusion_label = target_node.conclusion_label

        analysis.recommendation_code = (
            target_node.recommendation_code
        )
        analysis.recommendation_label = (
            target_node.recommendation_label
        )

        analysis.completed_at = datetime.now()

    else:
        raise ValueError(
            f"Type de nœud Just Culture inconnu : "
            f"{target_node.node_type}."
        )

    db.flush()

    return (
        analysis,
        answer_record,
        current_node,
        target_node,
    )

def get_event_just_culture_analysis(
    db: Session,
    event_id: int,
):
    # ---------------------------------------------------------
    # 1. Retrouver l'analyse
    # ---------------------------------------------------------
    analysis = db.scalar(
        select(models.EventJustCultureAnalysis)
        .where(
            models.EventJustCultureAnalysis.event_id == event_id
        )
    )

    if analysis is None:
        raise ValueError(
            "Aucune analyse Just Culture n'existe pour cet événement."
        )

    # ---------------------------------------------------------
    # 2. Retrouver la version de l'arbre utilisée
    # ---------------------------------------------------------
    tree_version = db.get(
        models.JustCultureTreeVersion,
        analysis.tree_version_id,
    )

    if tree_version is None:
        raise ValueError(
            "La version de l'arbre Just Culture utilisée "
            "par cette analyse est introuvable."
        )

    # ---------------------------------------------------------
    # 3. Retrouver le nœud courant si analyse en cours
    # ---------------------------------------------------------
    current_node = None

    if analysis.current_node_code:
        current_node = db.scalar(
            select(models.JustCultureNode)
            .where(
                models.JustCultureNode.tree_version_id
                == analysis.tree_version_id,
                models.JustCultureNode.code
                == analysis.current_node_code,
            )
        )

        if current_node is None:
            raise ValueError(
                "Le nœud courant de l'analyse Just Culture "
                "est introuvable."
            )

    # ---------------------------------------------------------
    # 4. Charger l'historique dans l'ordre du parcours
    # ---------------------------------------------------------
    history = db.scalars(
        select(models.EventJustCultureAnswer)
        .where(
            models.EventJustCultureAnswer.analysis_id
            == analysis.id
        )
        .order_by(
            models.EventJustCultureAnswer.step_order
        )
    ).all()

    return analysis, tree_version, current_node, history

# ========================================================
# JUST CULTURE — RETOUR À LA QUESTION PRÉCÉDENTE
# ========================================================

def back_event_just_culture_question(
    db: Session,
    event_id: int,
):
    # ---------------------------------------------------------
    # 1. Retrouver l'analyse
    # ---------------------------------------------------------
    analysis = db.scalar(
        select(models.EventJustCultureAnalysis)
        .where(
            models.EventJustCultureAnalysis.event_id == event_id
        )
    )

    if analysis is None:
        raise ValueError(
            "Aucune analyse Just Culture n'existe pour cet événement."
        )

    # ---------------------------------------------------------
    # 2. Retrouver la dernière réponse enregistrée
    # ---------------------------------------------------------
    last_answer = db.scalar(
        select(models.EventJustCultureAnswer)
        .where(
            models.EventJustCultureAnswer.analysis_id == analysis.id
        )
        .order_by(
            models.EventJustCultureAnswer.step_order.desc()
        )
    )

    if last_answer is None:
        raise ValueError(
            "Aucune réponse précédente n'est disponible."
        )

    # ---------------------------------------------------------
    # 3. Retrouver la question à réafficher
    # ---------------------------------------------------------
    previous_node = db.scalar(
        select(models.JustCultureNode)
        .where(
            models.JustCultureNode.tree_version_id
            == analysis.tree_version_id,
            models.JustCultureNode.code
            == last_answer.node_code,
            models.JustCultureNode.active.is_(True),
        )
    )

    if previous_node is None:
        raise ValueError(
            "La question précédente est introuvable."
        )

    if previous_node.node_type != "QUESTION":
        raise ValueError(
            "Le nœud précédent n'est pas une question."
        )

    # ---------------------------------------------------------
    # 4. Supprimer la dernière réponse
    # ---------------------------------------------------------
    db.delete(last_answer)

    # ---------------------------------------------------------
    # 5. Repositionner l'analyse
    # ---------------------------------------------------------
    analysis.status = "IN_PROGRESS"
    analysis.current_node_code = previous_node.code

    analysis.conclusion_code = None
    analysis.conclusion_label = None

    analysis.recommendation_code = None
    analysis.recommendation_label = None

    analysis.completed_at = None

    db.flush()

    return analysis, previous_node