from backend.database import SessionLocal
from backend.services.cause_tree import (
    create_event_cause_fact,
    create_event_cause_relation,
    delete_event_cause_relation,
)


db = SessionLocal()

try:
    # ---------------------------------------------------------
    # 1. Créer une cause temporaire
    # ---------------------------------------------------------
    cause = create_event_cause_fact(
        db=db,
        event_id=2,
        description="Cause temporaire multi-relation",
        sort_order=20,
    )

    print(
        "AFTER CREATE:",
        cause.fact_type,
    )

    # ---------------------------------------------------------
    # 2. Créer deux relations sortantes
    # ---------------------------------------------------------
    relation_1 = create_event_cause_relation(
        db=db,
        event_id=2,
        cause_fact_id=cause.id,
        effect_fact_id=1,
    )

    relation_2 = create_event_cause_relation(
        db=db,
        event_id=2,
        cause_fact_id=cause.id,
        effect_fact_id=2,
    )

    print(
        "AFTER TWO RELATIONS:",
        cause.fact_type,
    )

    # ---------------------------------------------------------
    # 3. Supprimer seulement la première relation
    # ---------------------------------------------------------
    delete_event_cause_relation(
        db=db,
        event_id=2,
        relation_id=relation_1.id,
    )

    print(
        "AFTER FIRST DELETE:",
        cause.fact_type,
    )

    # ---------------------------------------------------------
    # 4. Supprimer la dernière relation
    # ---------------------------------------------------------
    delete_event_cause_relation(
        db=db,
        event_id=2,
        relation_id=relation_2.id,
    )

    print(
        "AFTER LAST DELETE:",
        cause.fact_type,
    )

finally:
    db.rollback()
    db.close()