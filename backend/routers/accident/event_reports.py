# ========================================================
# RISKY — ROUTES RAPPORTS ÉVÉNEMENT
# ========================================================

from fastapi import (
    APIRouter,
    HTTPException,
    Response,
)

from backend.database import SessionLocal
from backend.schemas.event_reports import (
    EventReportPreviewResponse,
)
from backend.services.reports.accident_report import (
    build_accident_report_preview,
)
from backend.services.reports.pdf_renderer import (
    render_accident_report_pdf,
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

# ========================================================
# PDF RAPPORT D'ANALYSE
# ========================================================

@router.get("/{event_id}/reports/analysis/pdf")
def generate_analysis_report_pdf(
    event_id: int,
    language: str = "fr",
):
    db = SessionLocal()
    try:
        data = build_accident_report_preview(db=db, event_id=event_id)
        pdf = render_accident_report_pdf(data=data, db=db, language=language)
        filename = f"RISKY_{data['event_number']}_rapport_analyse.pdf"
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    finally:
        db.close()
