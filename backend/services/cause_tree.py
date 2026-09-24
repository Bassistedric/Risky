from sqlalchemy.orm import Session

from .. import models

from sqlalchemy import select


def create_event_cause_fact(
    db: Session,
    event_id: int,
    description: str,
    fact_type: str = "CIRCUMSTANCE",
    sort_order: int = 0,
):
    # ---------------------------------------------------------
    # 1. Vérifier que l'événement existe
    # ---------------------------------------------------------
    event = db.get(models.Event, event_id)

    if event is None:
        raise ValueError("Événement introuvable.")

    # ---------------------------------------------------------
    # 2. Nettoyer et contrôler le fait
    # ---------------------------------------------------------
    clean_description = description.strip()

    if not clean_description:
        raise ValueError(
            "La description du fait ne peut pas être vide."
        )

    clean_fact_type = fact_type.strip().upper()

    if not clean_fact_type:
        clean_fact_type = "CIRCUMSTANCE"

    # ---------------------------------------------------------
    # 3. Créer le fait
    # ---------------------------------------------------------
    fact = models.EventCauseFact(
        event_id=event_id,
        fact_type=clean_fact_type,
        description=clean_description,
        sort_order=sort_order,
    )

    db.add(fact)
    db.flush()

    return fact

def create_event_cause_relation(
    db: Session,
    event_id: int,
    cause_fact_id: int,
    effect_fact_id: int,
):
    # ---------------------------------------------------------
    # 1. Interdire une relation d'un fait vers lui-même
    # ---------------------------------------------------------
    if cause_fact_id == effect_fact_id:
        raise ValueError(
            "Un fait ne peut pas être sa propre cause."
        )

    # ---------------------------------------------------------
    # 2. Retrouver les deux faits
    # ---------------------------------------------------------
    cause_fact = db.get(
        models.EventCauseFact,
        cause_fact_id,
    )

    effect_fact = db.get(
        models.EventCauseFact,
        effect_fact_id,
    )

    if cause_fact is None:
        raise ValueError("Le fait causal est introuvable.")

    if effect_fact is None:
        raise ValueError("Le fait résultant est introuvable.")

    # ---------------------------------------------------------
    # 3. Vérifier qu'ils appartiennent au bon événement
    # ---------------------------------------------------------
    if cause_fact.event_id != event_id:
        raise ValueError(
            "Le fait causal n'appartient pas à cet événement."
        )

    if effect_fact.event_id != event_id:
        raise ValueError(
            "Le fait résultant n'appartient pas à cet événement."
        )

    # ---------------------------------------------------------
    # Le fait final est l'aboutissement de l'arbre.
    # Il ne peut pas être la cause d'un autre fait.
    # ---------------------------------------------------------
    if cause_fact.fact_type == "FINAL":
        raise ValueError(
            "Le fait final ne peut pas être la cause "
            "d'un autre fait."
        )

    # ---------------------------------------------------------
    # 4. Interdire une relation déjà existante
    # ---------------------------------------------------------
    existing = db.scalar(
        select(models.EventCauseRelation)
        .where(
            models.EventCauseRelation.event_id == event_id,
            models.EventCauseRelation.cause_fact_id
            == cause_fact_id,
            models.EventCauseRelation.effect_fact_id
            == effect_fact_id,
        )
    )

    if existing is not None:
        raise ValueError(
            "Cette relation causale existe déjà."
        )

    # ---------------------------------------------------------
    # 5. Vérifier que la relation ne crée pas de boucle
    #
    # Pour créer A -> B, on vérifie qu'un chemin
    # B -> ... -> A n'existe pas déjà.
    # ---------------------------------------------------------
    relations = db.scalars(
        select(models.EventCauseRelation)
        .where(
            models.EventCauseRelation.event_id == event_id
        )
    ).all()

    adjacency = {}

    for relation in relations:
        adjacency.setdefault(
            relation.cause_fact_id,
            [],
        ).append(
            relation.effect_fact_id
        )

    stack = [effect_fact_id]
    visited = set()

    while stack:
        current = stack.pop()

        if current == cause_fact_id:
            raise ValueError(
                "Cette relation créerait une boucle "
                "dans l'arbre des causes."
            )

        if current in visited:
            continue

        visited.add(current)

        stack.extend(
            adjacency.get(current, [])
        )

    # ---------------------------------------------------------
    # 6. Créer la relation
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # Un élément utilisé comme cause devient automatiquement
    # un fait causal.
    # ---------------------------------------------------------
    if cause_fact.fact_type != "FINAL":
        cause_fact.fact_type = "CAUSE"

        # ---------------------------------------------------------
    # Si le fait résultant était terminal, il ne l'est plus :
    # une nouvelle cause vient maintenant d'être ajoutée en amont.
    # ---------------------------------------------------------

    if effect_fact.is_terminal:
        effect_fact.is_terminal = False
    relation = models.EventCauseRelation(
        event_id=event_id,
        cause_fact_id=cause_fact_id,
        effect_fact_id=effect_fact_id,
    )

    db.add(relation)
    db.flush()

    return relation

def get_event_cause_tree(
    db: Session,
    event_id: int,
):
    # ---------------------------------------------------------
    # 1. Vérifier que l'événement existe
    # ---------------------------------------------------------
    event = db.get(models.Event, event_id)

    if event is None:
        raise ValueError("Événement introuvable.")

    # ---------------------------------------------------------
    # 2. Charger les faits
    # ---------------------------------------------------------
    facts = db.scalars(
        select(models.EventCauseFact)
        .where(
            models.EventCauseFact.event_id == event_id
        )
        .order_by(
            models.EventCauseFact.sort_order,
            models.EventCauseFact.id,
        )
    ).all()

    # ---------------------------------------------------------
    # 3. Charger les relations
    # ---------------------------------------------------------
    relations = db.scalars(
        select(models.EventCauseRelation)
        .where(
            models.EventCauseRelation.event_id == event_id
        )
        .order_by(
            models.EventCauseRelation.id
        )
    ).all()

    return facts, relations

def delete_event_cause_fact(
    db: Session,
    event_id: int,
    fact_id: int,
):
    fact = db.get(
        models.EventCauseFact,
        fact_id,
    )

    if fact is None or fact.event_id != event_id:
        raise ValueError("Fait introuvable.")

    # ---------------------------------------------------------
    # Relations qui vont disparaître avec le fait
    # ---------------------------------------------------------
    relations = list(
        db.scalars(
            select(models.EventCauseRelation)
            .where(
                models.EventCauseRelation.event_id == event_id,
                (
                    (
                        models.EventCauseRelation.cause_fact_id
                        == fact_id
                    )
                    |
                    (
                        models.EventCauseRelation.effect_fact_id
                        == fact_id
                    )
                ),
            )
        )
    )

    deleted_relation_ids = [
        relation.id
        for relation in relations
    ]

    # ---------------------------------------------------------
    # Mémoriser les causes dont une relation sortante
    # va être supprimée.
    #
    # Exemple :
    #
    # A ─► B ─► C
    #
    # Si B est supprimé, A perd sa relation sortante.
    # Il devra éventuellement redevenir CIRCUMSTANCE.
    # ---------------------------------------------------------
    affected_cause_fact_ids = {
        relation.cause_fact_id
        for relation in relations
        if relation.cause_fact_id != fact_id
    }

    deleted_fact = {
        "id": fact.id,
        "event_id": fact.event_id,
        "fact_type": fact.fact_type,
        "description": fact.description,
        "sort_order": fact.sort_order,
        "is_terminal": fact.is_terminal,
    }

    # ---------------------------------------------------------
    # Supprimer les relations attachées
    # ---------------------------------------------------------
    for relation in relations:
        db.delete(relation)

    db.flush()

    # ---------------------------------------------------------
    # Recalculer le statut des causes affectées
    # ---------------------------------------------------------
    for affected_fact_id in affected_cause_fact_ids:
        remaining_relation = db.scalar(
            select(models.EventCauseRelation)
            .where(
                models.EventCauseRelation.event_id == event_id,
                models.EventCauseRelation.cause_fact_id
                == affected_fact_id,
            )
        )

        if remaining_relation is None:
            affected_fact = db.get(
                models.EventCauseFact,
                affected_fact_id,
            )

            if (
                affected_fact is not None
                and affected_fact.fact_type == "CAUSE"
            ):
                affected_fact.fact_type = "CIRCUMSTANCE"
                affected_fact.is_terminal = False

    # ---------------------------------------------------------
    # Supprimer le fait lui-même
    # ---------------------------------------------------------
    db.delete(fact)
    db.flush()

    return deleted_fact, deleted_relation_ids

def delete_event_cause_relation(
    db: Session,
    event_id: int,
    relation_id: int,
):
    # ---------------------------------------------------------
    # 1. Retrouver la relation
    # ---------------------------------------------------------
    relation = db.get(
        models.EventCauseRelation,
        relation_id,
    )

    if relation is None:
        raise ValueError(
            "La relation causale est introuvable."
        )

    # ---------------------------------------------------------
    # 2. Vérifier l'événement
    # ---------------------------------------------------------
    if relation.event_id != event_id:
        raise ValueError(
            "Cette relation n'appartient pas à cet événement."
        )

    # ---------------------------------------------------------
    # 3. Conserver les données pour l'audit
    # ---------------------------------------------------------
    deleted_relation = {
        "id": relation.id,
        "event_id": relation.event_id,
        "cause_fact_id": relation.cause_fact_id,
        "effect_fact_id": relation.effect_fact_id,
    }

    # ---------------------------------------------------------
    # 4. Supprimer
    # ---------------------------------------------------------
    db.delete(relation)
    db.flush()

    # ---------------------------------------------------------
    # 5. Vérifier si l'ancien fait causal possède encore
    #    au moins une relation sortante
    # ---------------------------------------------------------
    remaining_relation = db.scalar(
        select(models.EventCauseRelation)
        .where(
            models.EventCauseRelation.event_id == event_id,
            models.EventCauseRelation.cause_fact_id
            == deleted_relation["cause_fact_id"],
        )
    )

    # ---------------------------------------------------------
    # 6. Sans relation causale sortante, une ancienne CAUSE
    #    redevient une CIRCUMSTANCE
    # ---------------------------------------------------------
    if remaining_relation is None:
        cause_fact = db.get(
            models.EventCauseFact,
            deleted_relation["cause_fact_id"],
        )

        if (
            cause_fact is not None
            and cause_fact.fact_type == "CAUSE"
        ):
            cause_fact.fact_type = "CIRCUMSTANCE"
            cause_fact.is_terminal = False

    db.flush()

    return deleted_relation

def update_event_cause_fact(
    db: Session,
    event_id: int,
    fact_id: int,
    description: str,
    sort_order: int = 0,
):
    fact = db.get(
        models.EventCauseFact,
        fact_id,
    )

    if fact is None or fact.event_id != event_id:
        raise ValueError("Fait introuvable.")

    clean_description = description.strip()

    if not clean_description:
        raise ValueError(
            "La description du fait ne peut pas être vide."
        )

    before_data = {
        "id": fact.id,
        "event_id": fact.event_id,
        "fact_type": fact.fact_type,
        "description": fact.description,
        "sort_order": fact.sort_order,
        "is_terminal": fact.is_terminal,
    }

    # ---------------------------------------------------------
    # Seules les données éditables par l'utilisateur
    # sont modifiées ici.
    #
    # fact_type et is_terminal restent sous le contrôle
    # exclusif des règles métier de RISKY.
    # ---------------------------------------------------------
    fact.description = clean_description
    fact.sort_order = sort_order

    db.flush()

    return fact, before_data

def close_event_cause_branch(
    db: Session,
    event_id: int,
    fact_id: int,
):
    fact = db.get(
        models.EventCauseFact,
        fact_id,
    )

    if fact is None or fact.event_id != event_id:
        raise ValueError("Fait introuvable.")

    # ---------------------------------------------------------
    # Seule une CAUSE peut terminer une branche.
    #
    # CIRCUMSTANCE → jamais terminale
    # CAUSE        → peut être terminale
    # FINAL        → jamais terminal
    # ---------------------------------------------------------
    if fact.fact_type != "CAUSE":
        raise ValueError(
            "Seule une cause peut terminer "
            "une branche de l'arbre des causes."
        )

    # ---------------------------------------------------------
    # Une branche ne peut être déclarée terminée que si
    # aucune cause supplémentaire n'est déjà renseignée
    # en amont de ce fait.
    # ---------------------------------------------------------
    upstream_relation = db.scalar(
        select(models.EventCauseRelation)
        .where(
            models.EventCauseRelation.event_id == event_id,
            models.EventCauseRelation.effect_fact_id == fact_id,
        )
    )

    if upstream_relation is not None:
        raise ValueError(
            "Cette branche ne peut pas être terminée : "
            "ce fait possède déjà au moins une cause en amont."
        )

    before_data = {
        "id": fact.id,
        "event_id": fact.event_id,
        "fact_type": fact.fact_type,
        "description": fact.description,
        "sort_order": fact.sort_order,
        "is_terminal": fact.is_terminal,
    }

    fact.is_terminal = True

    db.flush()

    return fact, before_data

def reopen_event_cause_branch(
    db: Session,
    event_id: int,
    fact_id: int,
):
    fact = db.get(
        models.EventCauseFact,
        fact_id,
    )

    if fact is None or fact.event_id != event_id:
        raise ValueError("Fait introuvable.")

    # ---------------------------------------------------------
    # Seule une CAUSE peut être rouverte.
    # ---------------------------------------------------------
    if fact.fact_type != "CAUSE":
        raise ValueError(
            "Seule une cause peut être rouverte "
            "dans l'arbre des causes."
        )

    # ---------------------------------------------------------
    # La branche doit être actuellement déclarée terminale.
    # ---------------------------------------------------------
    if not fact.is_terminal:
        raise ValueError(
            "Cette branche n'est pas actuellement terminée."
        )

    before_data = {
        "id": fact.id,
        "event_id": fact.event_id,
        "fact_type": fact.fact_type,
        "description": fact.description,
        "sort_order": fact.sort_order,
        "is_terminal": fact.is_terminal,
    }

    fact.is_terminal = False

    db.flush()

    return fact, before_data

def set_event_cause_final_fact(
    db: Session,
    event_id: int,
    fact_id: int,
):
    # ---------------------------------------------------------
    # 1. Vérifier l'événement
    # ---------------------------------------------------------
    event = db.get(
        models.Event,
        event_id,
    )

    if event is None:
        raise ValueError(
            "Événement introuvable."
        )

    # ---------------------------------------------------------
    # 2. Retrouver le fait à désigner comme final
    # ---------------------------------------------------------
    fact = db.get(
        models.EventCauseFact,
        fact_id,
    )

    if fact is None:
        raise ValueError(
            "Le fait est introuvable."
        )

    if fact.event_id != event_id:
        raise ValueError(
            "Ce fait n'appartient pas à cet événement."
        )

    # ---------------------------------------------------------
    # 3. Vérifier qu'il n'existe pas déjà un autre fait final
    # ---------------------------------------------------------
    existing_final = db.scalar(
        select(models.EventCauseFact)
        .where(
            models.EventCauseFact.event_id == event_id,
            models.EventCauseFact.fact_type == "FINAL",
            models.EventCauseFact.id != fact_id,
        )
    )

    if existing_final is not None:
        raise ValueError(
            "Cet arbre des causes possède déjà un fait final."
        )


    # ---------------------------------------------------------
    # 4. Vérifier que ce fait n'est pas déjà la cause
    #    d'un autre fait
    # ---------------------------------------------------------
    outgoing_relation = db.scalar(
        select(models.EventCauseRelation)
        .where(
            models.EventCauseRelation.event_id == event_id,
            models.EventCauseRelation.cause_fact_id == fact_id,
        )
    )

    if outgoing_relation is not None:
        raise ValueError(
            "Ce fait ne peut pas devenir le fait final : "
            "il est déjà la cause d'un autre fait."
        )

    # ---------------------------------------------------------
    # 5. Conserver l'état précédent pour l'audit
    # ---------------------------------------------------------
    before_data = {
        "id": fact.id,
        "event_id": fact.event_id,
        "fact_type": fact.fact_type,
        "description": fact.description,
        "sort_order": fact.sort_order,
        "is_terminal": fact.is_terminal,
    }

    # ---------------------------------------------------------
    # 6. Désigner le fait final
    # ---------------------------------------------------------
    fact.fact_type = "FINAL"
    fact.is_terminal = False

    db.flush()

    return fact, before_data

def create_event_cause_fact_guided(
    db: Session,
    event_id: int,
    description: str,
    sort_order: int = 0,
    effect_fact_ids: list[int] | None = None,
):
    # ---------------------------------------------------------
    # 1. Normaliser la liste des rattachements
    # ---------------------------------------------------------
    if effect_fact_ids is None:
        effect_fact_ids = []

    # Éviter de créer deux fois la même relation
    unique_effect_fact_ids = list(
        dict.fromkeys(effect_fact_ids)
    )

    # ---------------------------------------------------------
    # 2. Créer le nouvel élément
    #    Il naît comme CIRCUMSTANCE.
    # ---------------------------------------------------------
    fact = create_event_cause_fact(
        db=db,
        event_id=event_id,
        description=description,
        fact_type="CIRCUMSTANCE",
        sort_order=sort_order,
    )

    # ---------------------------------------------------------
    # 3. Créer les relations demandées
    # ---------------------------------------------------------
    relations = []

    for effect_fact_id in unique_effect_fact_ids:
        relation = create_event_cause_relation(
            db=db,
            event_id=event_id,
            cause_fact_id=fact.id,
            effect_fact_id=effect_fact_id,
        )

        relations.append(relation)

    # ---------------------------------------------------------
    # 4. Les fonctions appelées ont déjà appliqué les règles :
    #
    #    aucune relation → CIRCUMSTANCE
    #    au moins une    → CAUSE
    # ---------------------------------------------------------
    db.flush()

    return fact, relations

def calculate_event_cause_levels(
    db: Session,
    event_id: int,
):
    event = db.get(
        models.Event,
        event_id,
    )

    if event is None:
        raise ValueError("Événement introuvable.")

    facts = list(
        db.scalars(
            select(models.EventCauseFact)
            .where(
                models.EventCauseFact.event_id == event_id,
            )
        )
    )

    relations = list(
        db.scalars(
            select(models.EventCauseRelation)
            .where(
                models.EventCauseRelation.event_id == event_id,
            )
        )
    )

    # ---------------------------------------------------------
    # Trouver le fait FINAL
    # ---------------------------------------------------------
    final_facts = [
        fact
        for fact in facts
        if fact.fact_type == "FINAL"
    ]

    if not final_facts:
        raise ValueError(
            "L'arbre des causes ne possède pas de fait final."
        )

    if len(final_facts) > 1:
        raise ValueError(
            "L'arbre des causes possède plusieurs faits finaux."
        )

    final_fact = final_facts[0]

    # ---------------------------------------------------------
    # Index :
    #
    # effet -> causes directes
    #
    # Pour :
    #
    # A -> B -> FINAL
    #
    # on obtient :
    #
    # FINAL : [B]
    # B     : [A]
    # ---------------------------------------------------------
    causes_by_effect = {}

    for relation in relations:
        causes_by_effect.setdefault(
            relation.effect_fact_id,
            [],
        ).append(
            relation.cause_fact_id
        )

    # ---------------------------------------------------------
    # Parcours depuis FINAL.
    #
    # Le niveau correspond à la distance minimale au FINAL.
    # ---------------------------------------------------------
    levels = {
        final_fact.id: 0,
    }

    queue = [
        final_fact.id,
    ]

    while queue:
        effect_fact_id = queue.pop(0)

        current_level = levels[
            effect_fact_id
        ]

        for cause_fact_id in causes_by_effect.get(
            effect_fact_id,
            [],
        ):
            proposed_level = current_level + 1

            if (
                cause_fact_id not in levels
                or proposed_level
                < levels[cause_fact_id]
            ):
                levels[cause_fact_id] = proposed_level
                queue.append(cause_fact_id)

    return levels