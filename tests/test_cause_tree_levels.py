from backend.database import SessionLocal
from backend.services.cause_tree import (
    calculate_event_cause_levels,
)


db = SessionLocal()

try:
    levels = calculate_event_cause_levels(
        db=db,
        event_id=2,
    )

    print("NIVEAUX:", levels)

    assert levels[2] == 0
    assert levels[1] == 1
    assert levels[3] == 2

    print(
        "OK: les niveaux sont correctement "
        "calculés depuis le fait FINAL."
    )

finally:
    db.close()
    