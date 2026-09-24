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
from backend.services.reports.safety_flash import build_safety_flash_preview
from backend.services.reports.safety_flash_renderer import render_safety_flash_pdf


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


# ========================================================
# SAFETY FLASH CFE
# ========================================================

@router.get("/{event_id}/reports/safety-flash/preview")
def preview_safety_flash(event_id: int):
    db = SessionLocal()
    try:
        return build_safety_flash_preview(db=db, event_id=event_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    finally:
        db.close()


@router.post("/{event_id}/reports/safety-flash/pdf")
def generate_safety_flash_pdf(
    event_id: int,
    payload: dict,
    language: str = "fr",
):
    db = SessionLocal()
    try:
        base = build_safety_flash_preview(db=db, event_id=event_id)
        editable = {
            **base,
            "event_type": payload.get("event_type", base.get("event_type")),
            "subject": payload.get("subject", base.get("subject")),
            "facts": payload.get("facts", base.get("facts")),
            "explanations": payload.get("explanations", base.get("explanations")),
            "recommendations": payload.get("recommendations", base.get("recommendations")),
            "photos": payload.get("photos", base.get("photos")),
        }
        pdf = render_safety_flash_pdf(editable, language=language)
        filename = f"RISKY_{base['event_number']}_Safety_Flash.pdf"
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    finally:
        db.close()
