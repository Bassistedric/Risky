from backend.database import SessionLocal
from backend.services.cause_tree import (
    close_event_cause_branch,
    create_event_cause_fact,
    create_event_cause_relation,
)


def test_terminal_fact_resets_when_new_upstream_cause_is_added():
    db = SessionLocal()

    try:
        # -----------------------------------------------------
        # 1. Créer un effet temporaire
        # -----------------------------------------------------
        effect = create_event_cause_fact(
            db=db,
            event_id=2,
            description="Effet temporaire",
            sort_order=0,
        )

        # -----------------------------------------------------
        # 2. Créer une cause temporaire
        # -----------------------------------------------------
        terminal_cause = create_event_cause_fact(
            db=db,
            event_id=2,
            description="Cause terminale temporaire",
            sort_order=0,
        )

        # -----------------------------------------------------
        # 3. Relier la cause à l'effet
        #
        # La relation transforme automatiquement
        # terminal_cause en CAUSE.
        # -----------------------------------------------------
        create_event_cause_relation(
            db=db,
            event_id=2,
            cause_fact_id=terminal_cause.id,
            effect_fact_id=effect.id,
        )

        assert terminal_cause.fact_type == "CAUSE"
        assert terminal_cause.is_terminal is False

        # -----------------------------------------------------
        # 4. Terminer explicitement cette branche
        #
        # terminal_cause n'a aucune cause en amont :
        # la fermeture doit donc être autorisée.
        # -----------------------------------------------------
        closed_fact, _ = close_event_cause_branch(
            db=db,
            event_id=2,
            fact_id=terminal_cause.id,
        )

        assert closed_fact.is_terminal is True

        # -----------------------------------------------------
        # 5. Ajouter ensuite une nouvelle cause en amont
        # -----------------------------------------------------
        upstream_cause = create_event_cause_fact(
            db=db,
            event_id=2,
            description="Nouvelle cause en amont",
            sort_order=0,
        )

        create_event_cause_relation(
            db=db,
            event_id=2,
            cause_fact_id=upstream_cause.id,
            effect_fact_id=terminal_cause.id,
        )

        # -----------------------------------------------------
        # 6. La branche n'est plus terminale :
        # l'ajout d'une cause en amont doit automatiquement
        # réinitialiser is_terminal.
        # -----------------------------------------------------
        assert terminal_cause.is_terminal is False

    finally:
        db.rollback()
        db.close()