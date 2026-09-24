from backend.database import SessionLocal
from backend.services.cause_tree import (
    create_event_cause_fact,
    create_event_cause_relation,
)


db = SessionLocal()

try:
    # ---------------------------------------------------------
    # 1. Créer un nouvel élément sans relation
    # ---------------------------------------------------------
    new_fact = create_event_cause_fact(
        db=db,
        event_id=2,
        description="Pression de chantier temporaire",
        sort_order=10,
    )

    print(
        "AFTER CREATE:",
        new_fact.id,
        new_fact.fact_type,
    )

    # ---------------------------------------------------------
    # 2. Le relier comme cause au fait 2
    # ---------------------------------------------------------
    create_event_cause_relation(
        db=db,
        event_id=2,
        cause_fact_id=new_fact.id,
        effect_fact_id=2,
    )

    print(
        "AFTER RELATION:",
        new_fact.id,
        new_fact.fact_type,
    )

finally:
    db.rollback()
    db.close()