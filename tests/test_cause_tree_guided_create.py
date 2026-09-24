from backend.database import SessionLocal
from backend.services.cause_tree import (
    create_event_cause_fact_guided,
)


db = SessionLocal()

try:
    # ---------------------------------------------------------
    # Créer "Pression de chantier"
    # et le rattacher au fait final 2
    # ---------------------------------------------------------
    fact, relations = create_event_cause_fact_guided(
        db=db,
        event_id=2,
        description="Pression de chantier",
        sort_order=10,
        effect_fact_ids=[2],
    )

    print(
        "FACT:",
        fact.id,
        fact.description,
        fact.fact_type,
    )

    print(
        "RELATIONS:",
        len(relations),
    )

    for relation in relations:
        print(
            "RELATION:",
            relation.cause_fact_id,
            "->",
            relation.effect_fact_id,
        )

finally:
    db.rollback()
    db.close()