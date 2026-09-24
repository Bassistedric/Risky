# ========================================================
# RISKY — RENDERER PDF SAFETY FLASH CFE
# ========================================================

from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, Table, TableStyle
from reportlab.pdfgen import canvas

from backend.services.event_photos import STORAGE_ROOT


ORANGE = colors.HexColor("#F28C00")
NAVY = colors.HexColor("#17384A")
GREY = colors.HexColor("#5F666D")
LIGHT = colors.HexColor("#F4F5F6")
WHITE = colors.white

_FONT_CANDIDATES = [
    (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")),
    (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
]
FONT, FONT_BOLD = "Helvetica", "Helvetica-Bold"
for regular, bold in _FONT_CANDIDATES:
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("SafetyFlashSans", str(regular)))
        pdfmetrics.registerFont(TTFont("SafetyFlashSans-Bold", str(bold)))
        FONT, FONT_BOLD = "SafetyFlashSans", "SafetyFlashSans-Bold"
        break


TEXT = {
    "fr": {"title":"CFE Safety Flash","what":"Quoi","incident":"Incident","accident":"Accident","near":"Presqu’accident","subject":"Sujet","facts":"Les faits","explanations":"Explications","support":"Support d’information (Photos / docs….)","photo":"Photo","actions":"Action corrective / Recommandations","internal":"Internal use only."},
    "nl": {"title":"CFE Safety Flash","what":"Wat","incident":"Incident","accident":"Ongeval","near":"Bijna-ongeval","subject":"Onderwerp","facts":"De feiten","explanations":"Toelichting","support":"Informatiemateriaal (foto’s / documenten…)","photo":"Foto","actions":"Corrigerende acties / Aanbevelingen","internal":"Internal use only."},
    "en": {"title":"CFE Safety Flash","what":"What","incident":"Incident","accident":"Accident","near":"Near miss","subject":"Subject","facts":"Facts","explanations":"Explanations","support":"Information support (Photos / documents…)","photo":"Photo","actions":"Corrective actions / Recommendations","internal":"Internal use only."},
    "pl": {"title":"CFE Safety Flash","what":"Co","incident":"Incydent","accident":"Wypadek","near":"Zdarzenie potencjalnie wypadkowe","subject":"Temat","facts":"Fakty","explanations":"Wyjaśnienia","support":"Materiały informacyjne (zdjęcia / dokumenty…)","photo":"Zdjęcie","actions":"Działania korygujące / Zalecenia","internal":"Internal use only."},
}


def _p(text, size=10, bold=False, color=GREY, leading=None):
    return Paragraph(
        escape(str(text or "")).replace("\n", "<br/>"),
        ParagraphStyle("sf", fontName=FONT_BOLD if bold else FONT, fontSize=size,
                       leading=leading or size * 1.25, textColor=color),
    )


def _fit_image(path: Path, max_w: float, max_h: float):
    img = Image(str(path))
    scale = min(max_w / img.imageWidth, max_h / img.imageHeight)
    img.drawWidth = img.imageWidth * scale
    img.drawHeight = img.imageHeight * scale
    return img


def render_safety_flash_pdf(data: dict, language: str = "fr") -> bytes:
    lang = language if language in TEXT else "fr"
    tr = TEXT[lang]
    out = BytesIO()
    c = canvas.Canvas(out, pagesize=A4)
    w, h = A4

    logo_candidates = [
        Path(__file__).resolve().parents[3] / "frontend" / "src" / "assets" / "images" / "vma_logo.jpg",
        Path.cwd() / "frontend" / "src" / "assets" / "images" / "vma_logo.jpg",
    ]
    logo_path = next((p for p in logo_candidates if p.exists()), None)

    def header(page_no: int):
        if logo_path:
            img = _fit_image(logo_path, 42*mm, 16*mm)
            img.drawOn(c, 18*mm, h-25*mm)
        c.setFont(FONT_BOLD, 20)
        c.setFillColor(ORANGE)
        c.drawRightString(w-18*mm, h-18*mm, tr["title"])
        c.setStrokeColor(ORANGE)
        c.setLineWidth(2)
        c.line(18*mm, h-30*mm, w-18*mm, h-30*mm)
        c.setFillColor(GREY)
        c.setFont(FONT, 7)
        c.drawString(18*mm, 10*mm, tr["internal"])
        c.drawRightString(w-18*mm, 10*mm, str(page_no))

    def section(label, value, y, height, accent=ORANGE):
        c.setFillColor(accent)
        c.rect(18*mm, y+height-9*mm, 174*mm, 9*mm, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(FONT_BOLD, 10)
        c.drawString(22*mm, y+height-6.2*mm, label)
        body = _p(value, size=10, color=GREY, leading=13)
        body.wrapOn(c, 166*mm, height-14*mm)
        body.drawOn(c, 22*mm, y+5*mm)

    # PAGE 1
    header(1)
    y = h - 45*mm
    event_type = (data.get("event_type") or "").upper()
    options = [("INCIDENT",tr["incident"]),("ACCIDENT",tr["accident"]),("NEAR_MISS",tr["near"])]
    c.setFont(FONT_BOLD, 11); c.setFillColor(GREY); c.drawString(18*mm,y,tr["what"]+":")
    x=45*mm
    for code,label in options:
        c.setStrokeColor(GREY); c.rect(x,y-3*mm,4*mm,4*mm,fill=0,stroke=1)
        if event_type==code:
            c.setFillColor(ORANGE); c.rect(x+.7*mm,y-2.3*mm,2.6*mm,2.6*mm,fill=1,stroke=0)
        c.setFillColor(GREY); c.setFont(FONT,9); c.drawString(x+6*mm,y-1.5*mm,label)
        x += 45*mm

    section(tr["subject"], data.get("subject"), h-86*mm, 25*mm)
    section(tr["facts"], data.get("facts"), h-164*mm, 68*mm)
    section(tr["explanations"], data.get("explanations"), 25*mm, h-199*mm)
    c.showPage()

    # PAGE 2
    header(2)
    c.setFillColor(ORANGE); c.rect(18*mm,h-50*mm,174*mm,9*mm,fill=1,stroke=0)
    c.setFillColor(WHITE); c.setFont(FONT_BOLD,10); c.drawString(22*mm,h-47*mm,tr["support"])
    photos=data.get("photos") or []
    photo_y=h-137*mm
    if photos:
        slots=[(20*mm,photo_y),(107*mm,photo_y)]
        for photo,(px,py) in zip(photos[:2],slots):
            # EventPhoto storage is storage/event_photos/<event_id>/<stored filename>.
            # Preview intentionally carries only id; resolve by common extensions if needed.
            event_dir=STORAGE_ROOT/str(data.get("event_id"))
            candidates=[]
            if event_dir.exists():
                candidates=sorted(event_dir.iterdir())
            # sort order in preview corresponds to stored order; safest available mapping for renderer
            idx=photos.index(photo)
            if idx < len(candidates):
                try:
                    img=_fit_image(candidates[idx],80*mm,68*mm)
                    img.drawOn(c,px+(80*mm-img.drawWidth)/2,py+(68*mm-img.drawHeight)/2)
                except Exception:
                    pass
    else:
        c.setStrokeColor(colors.HexColor("#D5D8DB")); c.rect(20*mm,photo_y,170*mm,68*mm,fill=0,stroke=1)
        c.setFillColor(GREY); c.setFont(FONT,9); c.drawCentredString(w/2,photo_y+32*mm,tr["photo"])

    section(tr["actions"], data.get("recommendations"), 25*mm, 92*mm)
    c.save()
    return out.getvalue()
