from backend.database import SessionLocal
from backend.services.cause_tree import (
    create_event_cause_fact,
    create_event_cause_relation,
    calculate_event_cause_levels,
)


db = SessionLocal()

try:
    # ---------------------------------------------------------
    # Créer deux faits temporaires
    # ---------------------------------------------------------
    fact_a = create_event_cause_fact(
        db=db,
        event_id=2,
        description="Cause A temporaire",
        fact_type="CIRCUMSTANCE",
        sort_order=100,
    )

    fact_b = create_event_cause_fact(
        db=db,
        event_id=2,
        description="Cause B temporaire",
        fact_type="CIRCUMSTANCE",
        sort_order=101,
    )

    # ---------------------------------------------------------
    # Construire :
    #
    # A ───────► FINAL (2)
    # │
    # └──► B ──► FINAL (2)
    #
    # A est donc accessible par deux chemins.
    # ---------------------------------------------------------
    create_event_cause_relation(
        db=db,
        event_id=2,
        cause_fact_id=fact_a.id,
        effect_fact_id=2,
    )

    create_event_cause_relation(
        db=db,
        event_id=2,
        cause_fact_id=fact_a.id,
        effect_fact_id=fact_b.id,
    )

    create_event_cause_relation(
        db=db,
        event_id=2,
        cause_fact_id=fact_b.id,
        effect_fact_id=2,
    )

    # ---------------------------------------------------------
    # Calculer les niveaux
    # ---------------------------------------------------------
    levels = calculate_event_cause_levels(
        db=db,
        event_id=2,
    )

    print(
        "A:",
        fact_a.id,
        "niveau =",
        levels[fact_a.id],
    )

    print(
        "B:",
        fact_b.id,
        "niveau =",
        levels[fact_b.id],
    )

    print(
        "FINAL:",
        2,
        "niveau =",
        levels[2],
    )

    # ---------------------------------------------------------
    # Vérifications
    # ---------------------------------------------------------
    assert levels[2] == 0
    assert levels[fact_b.id] == 1

    # A possède un chemin de longueur 1
    # et un autre de longueur 2.
    # On doit retenir la distance minimale.
    assert levels[fact_a.id] == 1

    print(
        "OK: la distance minimale au FINAL "
        "est correctement calculée."
    )

finally:
    db.rollback()
    db.close()