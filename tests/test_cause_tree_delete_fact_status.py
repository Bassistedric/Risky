from backend.database import SessionLocal
from backend import models
from backend.services.cause_tree import (
    delete_event_cause_fact,
)


db = SessionLocal()

try:
    # ---------------------------------------------------------
    # Situation réelle avant test :
    #
    # 3 ─► 1 ─► 2
    #
    # 3 = Pression de chantier
    # 1 = Le sol était humide
    # 2 = Fait FINAL
    #
    # Si on supprime le fait 1 :
    #
    # - la relation 3 ─► 1 disparaît
    # - la relation 1 ─► 2 disparaît
    # - le fait 3 n'a plus aucune relation sortante
    # - il doit donc redevenir CIRCUMSTANCE
    # ---------------------------------------------------------

    fact_3_before = db.get(
        models.EventCauseFact,
        3,
    )

    print(
        "AVANT:",
        fact_3_before.id,
        fact_3_before.fact_type,
    )

    deleted_fact, deleted_relation_ids = (
        delete_event_cause_fact(
            db=db,
            event_id=2,
            fact_id=1,
        )
    )

    fact_3_after = db.get(
        models.EventCauseFact,
        3,
    )

    print(
        "FAIT SUPPRIME:",
        deleted_fact["id"],
    )

    print(
        "RELATIONS SUPPRIMEES:",
        deleted_relation_ids,
    )

    print(
        "APRES:",
        fact_3_after.id,
        fact_3_after.fact_type,
    )

    assert fact_3_before.id == 3
    assert fact_3_after.fact_type == "CIRCUMSTANCE"

    print(
        "OK: la dernière relation sortante a disparu, "
        "le fait 3 est redevenu CIRCUMSTANCE."
    )

finally:
    db.rollback()
    db.close()
