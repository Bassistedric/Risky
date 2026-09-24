# ========================================================
# RISKY — ROUTES RAPPORTS ÉVÉNEMENT
# ========================================================

from fastapi import (
    APIRouter,
    HTTPException,
)

from backend.database import SessionLocal
from backend.schemas.event_reports import (
    EventReportPreviewResponse,
)
from backend.services.reports.accident_report import (
    build_accident_report_preview,
)


router = APIRouter(
    prefix="/events",
    tags=["Events - Reports"],
)


# ========================================================
# APERÇU DES DONNÉES DU RAPPORT
# ========================================================

@router.get(
    "/{event_id}/reports/analysis/preview",
    response_model=EventReportPreviewResponse,
)
def preview_analysis_report(
    event_id: int,
):
    db = SessionLocal()

    try:
        return build_accident_report_preview(
            db=db,
            event_id=event_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    finally:
        db.close()