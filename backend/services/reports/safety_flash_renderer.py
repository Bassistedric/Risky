# ========================================================
# RISKY — RENDERER PDF SAFETY FLASH CFE
# ========================================================

from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph
from reportlab.pdfgen import canvas

from backend.services.event_photos import STORAGE_ROOT

CFE_ORANGE = colors.HexColor("#C6530B")
CFE_BLUE = colors.HexColor("#153B70")
BLACK = colors.black
YELLOW = colors.HexColor("#FFF200")

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
    "fr": {"title":"CFE Safety Flash","what":"Quoi :","incident":"Incident","accident":"Accident","near":"Presqu’accident","subject":"Sujet :","facts":"Les faits:","explanations":"Explications:","support":"Support d’information (Photos / docs…..) :","photo":"Photo:","actions":"Action corrective/ Recommandations:","internal":"Internal use only."},
    "nl": {"title":"CFE Safety Flash","what":"Wat :","incident":"Incident","accident":"Ongeval","near":"Bijna-ongeval","subject":"Onderwerp :","facts":"De feiten:","explanations":"Toelichting:","support":"Informatiemateriaal (foto’s / documenten…) :","photo":"Foto:","actions":"Corrigerende acties / Aanbevelingen:","internal":"Internal use only."},
    "en": {"title":"CFE Safety Flash","what":"What:","incident":"Incident","accident":"Accident","near":"Near miss","subject":"Subject:","facts":"Facts:","explanations":"Explanations:","support":"Information support (Photos / documents…) :","photo":"Photo:","actions":"Corrective actions / Recommendations:","internal":"Internal use only."},
    "pl": {"title":"CFE Safety Flash","what":"Co:","incident":"Incydent","accident":"Wypadek","near":"Zdarzenie potencjalnie wypadkowe","subject":"Temat:","facts":"Fakty:","explanations":"Wyjaśnienia:","support":"Materiały informacyjne (zdjęcia / dokumenty…) :","photo":"Zdjęcie:","actions":"Działania korygujące / Zalecenia:","internal":"Internal use only."},
}


def _para(text, size=10, bold=False, leading=None):
    return Paragraph(
        escape(str(text or "")).replace("\n", "<br/>"),
        ParagraphStyle("sf", fontName=FONT_BOLD if bold else FONT, fontSize=size,
                       leading=leading or size*1.22, textColor=BLACK),
    )


def _fit_image(path: Path, max_w: float, max_h: float):
    img = Image(str(path))
    scale = min(max_w/img.imageWidth, max_h/img.imageHeight)
    img.drawWidth, img.drawHeight = img.imageWidth*scale, img.imageHeight*scale
    return img


def render_safety_flash_pdf(data: dict, language: str = "fr") -> bytes:
    tr = TEXT.get(language, TEXT["fr"])
    out = BytesIO()
    c = canvas.Canvas(out, pagesize=A4)
    w, h = A4
    assets = Path(__file__).resolve().parents[3] / "frontend" / "src" / "assets" / "images"
    vma = assets / "vma_logo.jpg"
    zero = assets / "Go_for_zero.jpg"

    def header():
        if vma.exists():
            im=_fit_image(vma,47*mm,14*mm); im.drawOn(c,4*mm,h-20*mm)
        if zero.exists():
            im=_fit_image(zero,29*mm,18*mm); im.drawOn(c,w-33*mm,h-21*mm)
        c.setFillColor(CFE_ORANGE); c.setFont(FONT,29)
        c.drawCentredString(w/2,h-18*mm,tr["title"])
        c.setLineWidth(1.1); c.line(w/2-39*mm,h-21*mm,w/2+39*mm,h-21*mm)
        c.setFillColor(BLACK); c.setFont(FONT,6.5); c.drawString(2*mm,5*mm,tr["internal"])

    def orange_label(x,y,label,size=9):
        c.setFillColor(CFE_ORANGE); c.setFont(FONT_BOLD,size); c.drawString(x,y,label)
        width=c.stringWidth(label,FONT_BOLD,size); c.setLineWidth(.35); c.line(x,y-.7*mm,x+width,y-.7*mm)

    def bordered_box(x,y,bw,bh):
        c.setStrokeColor(CFE_BLUE); c.setLineWidth(.45); c.rect(x,y,bw,bh,fill=0,stroke=1)

    def text_in_box(text,x,y,bw,bh,top=5*mm,size=9.5):
        p=_para(text,size=size,leading=size*1.25); _,ph=p.wrap(bw-5*mm,bh-top-3*mm)
        p.drawOn(c,x+2.5*mm,y+bh-top-ph)

    # PAGE 1 — arrangement CFE
    header()
    top=h-37*mm
    left_x=4*mm; what_w=32*mm; gap=3*mm; subj_x=left_x+what_w+gap; right=4*mm
    row_h=19*mm
    bordered_box(left_x,top-row_h,what_w,row_h)
    bordered_box(subj_x,top-row_h,w-subj_x-right,row_h)
    orange_label(left_x+2*mm,top-5.5*mm,tr["what"],8.5)
    event=(data.get("event_type") or "").upper()
    labels=[("INCIDENT",tr["incident"]),("ACCIDENT",tr["accident"]),("NEAR_MISS",tr["near"])]
    yy=top-5.5*mm
    for code,label in labels:
        if code=="NEAR_MISS" and event!="NEAR_MISS": continue
        if code==event:
            tw=c.stringWidth(label,FONT_BOLD,8.5); c.setFillColor(YELLOW); c.rect(left_x+13*mm,yy-2.5*mm,tw+1.5*mm,4.2*mm,fill=1,stroke=0)
        c.setFillColor(BLACK); c.setFont(FONT_BOLD if code==event else FONT,8.5); c.drawString(left_x+13.5*mm,yy,label)
        yy-=6*mm
    orange_label(subj_x+2*mm,top-5.5*mm,tr["subject"],8.5)
    p=_para(data.get("subject"),9.5,bold=True); p.wrapOn(c,w-subj_x-right-19*mm,8*mm); p.drawOn(c,subj_x+15*mm,top-8.2*mm)

    facts_y=top-row_h-4*mm-31*mm; facts_h=31*mm
    bordered_box(left_x,facts_y,w-left_x-right,facts_h)
    orange_label(left_x+2*mm,facts_y+facts_h-5.5*mm,tr["facts"],8.5)
    text_in_box(data.get("facts"),left_x,facts_y,w-left_x-right,facts_h,8*mm,9.3)

    exp_y=50*mm; exp_h=facts_y-7*mm-exp_y
    bordered_box(left_x,exp_y,w-left_x-right,exp_h)
    orange_label(left_x+2*mm,exp_y+exp_h-5.5*mm,tr["explanations"],8.5)
    text_in_box(data.get("explanations"),left_x,exp_y,w-left_x-right,exp_h,9*mm,9.2)
    c.showPage()

    # PAGE 2 — actions first, then support/photos
    header()
    actions_top=h-35*mm; actions_h=45*mm; x=7*mm; bw=w-14*mm
    bordered_box(x,actions_top-actions_h,bw,actions_h)
    orange_label(x+2*mm,actions_top-5.5*mm,tr["actions"],8.5)
    text_in_box(data.get("recommendations"),x,actions_top-actions_h,bw,actions_h,9*mm,9.2)

    support_top=actions_top-actions_h-6*mm
    support_y=17*mm; support_h=support_top-support_y
    bordered_box(4*mm,support_y,w-8*mm,support_h)
    orange_label(6*mm,support_top-5.5*mm,tr["support"],8.5)
    orange_label(11*mm,support_top-23*mm,tr["photo"],8.5)

    photos=data.get("photos") or []
    event_dir=STORAGE_ROOT/str(data.get("event_id"))
    for idx,photo in enumerate(photos[:4]):
        filename=photo.get("filename")
        path=event_dir/filename if filename else None
        if not path or not path.exists(): continue
        col=idx%4; slot_w=43*mm; px=14*mm+col*45*mm
        try:
            im=_fit_image(path,slot_w,65*mm)
            im.drawOn(c,px+(slot_w-im.drawWidth)/2,support_y+5*mm+(65*mm-im.drawHeight)/2)
        except Exception:
            pass
    c.save()
    return out.getvalue()
