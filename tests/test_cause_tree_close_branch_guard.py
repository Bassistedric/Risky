from backend.database import SessionLocal
from backend.services.cause_tree import (
    close_event_cause_branch,
)


db = SessionLocal()

try:
    # ---------------------------------------------------------
    # 1. Le fait 3 est une CAUSE sans cause en amont.
    #    Il doit pouvoir terminer sa branche.
    # ---------------------------------------------------------
    fact_3, _ = close_event_cause_branch(
        db=db,
        event_id=2,
        fact_id=3,
    )

    print(
        "CAUSE:",
        fact_3.id,
        fact_3.fact_type,
        "terminal =",
        fact_3.is_terminal,
    )

    assert fact_3.fact_type == "CAUSE"
    assert fact_3.is_terminal is True

    # ---------------------------------------------------------
    # 2. Le fait 2 est FINAL.
    #    Il ne peut jamais être terminal.
    # ---------------------------------------------------------
    try:
        close_event_cause_branch(
            db=db,
            event_id=2,
            fact_id=2,
        )

        raise AssertionError(
            "Le fait FINAL aurait dû être refusé."
        )

    except ValueError as exc:
        print(
            "FINAL REFUSE:",
            str(exc),
        )

        assert (
            "Seule une cause peut terminer"
            in str(exc)
        )

    print(
        "OK: seule une CAUSE peut terminer une branche."
    )

finally:
    db.rollback()
    db.close()