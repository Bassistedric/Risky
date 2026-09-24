from backend.database import SessionLocal
from backend.services.cause_tree import (
    set_event_cause_final_fact,
)
from backend import models


db = SessionLocal()

try:
    # ---------------------------------------------------------
    # 1. Retirer temporairement le statut FINAL du fait 2
    # ---------------------------------------------------------
    fact_2 = db.get(
        models.EventCauseFact,
        2,
    )

    fact_2.fact_type = "CAUSE"
    db.flush()

    # ---------------------------------------------------------
    # 2. Tenter de rendre le fait 1 FINAL
    #    alors qu'il est déjà cause du fait 2
    # ---------------------------------------------------------
    try:
        set_event_cause_final_fact(
            db=db,
            event_id=2,
            fact_id=1,
        )

        print(
            "ERROR: outgoing relation guard failed"
        )

    except ValueError as exc:
        print(
            "FINAL REFUSED:",
            str(exc),
        )

finally:
    db.rollback()
    db.close()