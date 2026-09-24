from backend.database import SessionLocal
from backend import models
from backend.services.serious_accidents import evaluate_serious_accident


db = SessionLocal()

try:
    event = db.get(models.Event, 2)

    classification = (
        db.query(models.EventClassification)
        .filter(
            models.EventClassification.event_id == 2
        )
        .first()
    )

    result = evaluate_serious_accident(
        db,
        event,
        classification,
    )

    print(result)

finally:
    db.close()