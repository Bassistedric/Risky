from backend.database import SessionLocal
from backend.services.cause_tree import (
    set_event_cause_final_fact,
)


db = SessionLocal()

try:
    # ---------------------------------------------------------
    # 1. Désigner le fait 2 comme fait final
    # ---------------------------------------------------------
    final_fact, before = set_event_cause_final_fact(
        db=db,
        event_id=2,
        fact_id=2,
    )

    print(
        "FIRST FINAL:",
        final_fact.id,
        final_fact.fact_type,
    )

    # ---------------------------------------------------------
    # 2. Tenter de désigner le fait 1 comme second fait final
    # ---------------------------------------------------------
    try:
        set_event_cause_final_fact(
            db=db,
            event_id=2,
            fact_id=1,
        )

        print("ERROR: second final accepted")

    except ValueError as exc:
        print(
            "SECOND FINAL REFUSED:",
            str(exc),
        )

finally:
    db.rollback()
    db.close()