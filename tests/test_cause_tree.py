from backend.database import SessionLocal
from backend.services.cause_tree import (
    create_event_cause_fact,
    create_event_cause_relation,
)


db = SessionLocal()

try:
    # Fait 1 existe déjà en base :
    # "Le sol était humide"

    fact_b = create_event_cause_fact(
        db=db,
        event_id=2,
        description="Perte d'adhérence",
        sort_order=2,
    )

    fact_c = create_event_cause_fact(
        db=db,
        event_id=2,
        description="Chute du travailleur",
        sort_order=3,
    )

    relation_1 = create_event_cause_relation(
        db=db,
        event_id=2,
        cause_fact_id=1,
        effect_fact_id=fact_b.id,
    )

    relation_2 = create_event_cause_relation(
        db=db,
        event_id=2,
        cause_fact_id=fact_b.id,
        effect_fact_id=fact_c.id,
    )

    print(
        "CHAIN:",
        1,
        "->",
        fact_b.id,
        "->",
        fact_c.id,
    )

    print(
        "RELATIONS:",
        relation_1.id,
        relation_2.id,
    )

    try:
        create_event_cause_relation(
            db=db,
            event_id=2,
            cause_fact_id=fact_c.id,
            effect_fact_id=1,
        )

        print("ERROR: boucle acceptée")

    except ValueError as exc:
        print("LOOP REFUSED:", exc)

finally:
    db.rollback()
    db.close()