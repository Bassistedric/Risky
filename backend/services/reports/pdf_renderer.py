# ========================================================
# RISKY — RENDU PDF RAPPORT D'ANALYSE
# ========================================================

from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle, Flowable,
)
from reportlab.platypus.tableofcontents import TableOfContents

from backend.services.event_photos import STORAGE_ROOT, get_event_photos


NAVY = colors.HexColor("#17324D")
ORANGE = colors.HexColor("#B85F2B")
LIGHT = colors.HexColor("#EDF2F5")
IVORY = colors.HexColor("#FAF8F4")
BEIGE_BORDER = colors.HexColor("#DED7CA")
MID = colors.HexColor("#D7E0E6")
TEXT = colors.HexColor("#24313B")
MUTED = colors.HexColor("#667782")
GREEN = colors.HexColor("#EAF6EE")
YELLOW = colors.HexColor("#FFF8D9")
ORANGE_LIGHT = colors.HexColor("#FFF0E4")
RED = colors.HexColor("#FDECEC")

I18N = {
    "fr": {
        "report": "RAPPORT D’ANALYSE D’ÉVÉNEMENT", "contents": "Table des matières",
        "summary": "Synthèse & conséquences", "facts": "Relation des faits", "photos": "Photos",
        "classification": "Classification Fedris", "circ_details": "Données complémentaires du rapport circonstancié", "circ_causes": "Analyse complémentaire des causes", "heepo": "HEEPO", "jc": "Just Culture",
        "tree": "Arbre des causes", "actions": "Mesures & actions", "organization": "Organisation",
        "event_type": "Type d’événement", "event_date": "Date de l’événement", "location": "Lieu",
        "analysis": "Type d’analyse", "version": "Version", "generated": "Date de génération",
        "generated_by": "Document généré par RISKY QHSE", "not_applicable": "Non applicable",
        "not_provided": "Non renseigné", "person": "Personne concernée", "status": "Statut",
        "lost_days": "Jours perdus", "modified_days": "Jours de travail adapté",
        "material": "Dommages matériels", "environment": "Dommages environnementaux",
        "client": "Client", "worksite": "Chantier", "witnesses": "Témoins",
        "activity": "Activité avant l’événement", "description": "Description de l’événement",
        "direct_cause": "Cause directe", "deviation": "Déviation", "agent": "Agent matériel",
        "injury": "Nature de la lésion", "injury_location": "Localisation de la lésion",
        "conclusion": "Conclusion", "recommendation": "Recommandation", "action": "Action",
        "responsible": "Responsable", "due": "Échéance", "priority": "Priorité", "progress": "Avancement", "signatures": "Avis & signatures", "name_function": "Initiales", "victim_sign": "Victime", "hierarchy_sign": "Ligne hiérarchique", "date": "Date", "signature": "Signature", "employer_sign": "Employeur / représentant", "prevention_sign": "Conseiller en prévention / SIPP",
    },
    "nl": {
        "report": "ANALYSERAPPORT VAN EEN GEBEURTENIS", "contents": "Inhoudsopgave",
        "summary": "Samenvatting & gevolgen", "facts": "Feitenrelaas", "photos": "Foto’s",
        "classification": "Fedris-classificatie", "circ_details": "Aanvullende gegevens van het omstandig verslag", "circ_causes": "Aanvullende oorzakenanalyse", "heepo": "MUOPO", "jc": "Just Culture",
        "tree": "Oorzakenboom", "actions": "Maatregelen & acties", "organization": "Organisatie",
        "event_type": "Type gebeurtenis", "event_date": "Datum gebeurtenis", "location": "Plaats",
        "analysis": "Type analyse", "version": "Versie", "generated": "Generatiedatum",
        "generated_by": "Document gegenereerd door RISKY QHSE", "not_applicable": "Niet van toepassing",
        "not_provided": "Niet ingevuld", "person": "Betrokken persoon", "status": "Status",
        "lost_days": "Verloren dagen", "modified_days": "Dagen aangepast werk",
        "material": "Materiële schade", "environment": "Milieuschade", "client": "Klant",
        "worksite": "Werf", "witnesses": "Getuigen", "activity": "Activiteit vóór de gebeurtenis",
        "description": "Beschrijving van de gebeurtenis", "direct_cause": "Directe oorzaak",
        "deviation": "Afwijking", "agent": "Materiële agens", "injury": "Aard van het letsel",
        "injury_location": "Plaats van het letsel", "conclusion": "Conclusie",
        "recommendation": "Aanbeveling", "action": "Actie", "responsible": "Verantwoordelijke",
        "due": "Vervaldatum", "priority": "Prioriteit", "progress": "Voortgang", "signatures": "Advies & handtekeningen", "name_function": "Initialen", "victim_sign": "Slachtoffer", "hierarchy_sign": "Hiërarchische lijn", "date": "Datum", "signature": "Handtekening", "employer_sign": "Werkgever / vertegenwoordiger", "prevention_sign": "Preventieadviseur / IDPBW",
    },
    "en": {
        "report": "EVENT ANALYSIS REPORT", "contents": "Table of contents",
        "summary": "Summary & consequences", "facts": "Statement of facts", "photos": "Photos",
        "classification": "Fedris classification", "circ_details": "Additional information for the detailed report", "circ_causes": "Additional cause analysis", "heepo": "HEEPO", "jc": "Just Culture",
        "tree": "Cause tree", "actions": "Measures & actions", "organization": "Organization",
        "event_type": "Event type", "event_date": "Event date", "location": "Location",
        "analysis": "Analysis type", "version": "Version", "generated": "Generation date",
        "generated_by": "Document generated by RISKY QHSE", "not_applicable": "Not applicable",
        "not_provided": "Not provided", "person": "Person concerned", "status": "Status",
        "lost_days": "Lost days", "modified_days": "Modified-duty days", "material": "Material damage",
        "environment": "Environmental damage", "client": "Client", "worksite": "Worksite",
        "witnesses": "Witnesses", "activity": "Activity before the event",
        "description": "Event description", "direct_cause": "Direct cause", "deviation": "Deviation",
        "agent": "Material agent", "injury": "Nature of injury", "injury_location": "Injury location",
        "conclusion": "Conclusion", "recommendation": "Recommendation", "action": "Action",
        "responsible": "Responsible", "due": "Due date", "priority": "Priority", "progress": "Progress", "signatures": "Opinion & signatures", "name_function": "Initials", "victim_sign": "Victim", "hierarchy_sign": "Line management", "date": "Date", "signature": "Signature", "employer_sign": "Employer / representative", "prevention_sign": "Prevention advisor / internal service",
    },
    "pl": {
        "report": "RAPORT Z ANALIZY ZDARZENIA", "contents": "Spis treści",
        "summary": "Podsumowanie i konsekwencje", "facts": "Relacja faktów", "photos": "Zdjęcia",
        "classification": "Klasyfikacja Fedris", "circ_details": "Dane uzupełniające raportu szczegółowego", "circ_causes": "Uzupełniająca analiza przyczyn", "heepo": "HEEPO", "jc": "Just Culture",
        "tree": "Drzewo przyczyn", "actions": "Środki i działania", "organization": "Organizacja",
        "event_type": "Rodzaj zdarzenia", "event_date": "Data zdarzenia", "location": "Miejsce",
        "analysis": "Rodzaj analizy", "version": "Wersja", "generated": "Data wygenerowania",
        "generated_by": "Dokument wygenerowany przez RISKY QHSE", "not_applicable": "Nie dotyczy",
        "not_provided": "Nie podano", "person": "Osoba, której dotyczy", "status": "Status",
        "lost_days": "Dni stracone", "modified_days": "Dni pracy dostosowanej",
        "material": "Szkody materialne", "environment": "Szkody środowiskowe", "client": "Klient",
        "worksite": "Budowa", "witnesses": "Świadkowie", "activity": "Czynność przed zdarzeniem",
        "description": "Opis zdarzenia", "direct_cause": "Przyczyna bezpośrednia",
        "deviation": "Odchylenie", "agent": "Czynnik materialny", "injury": "Rodzaj urazu",
        "injury_location": "Umiejscowienie urazu", "conclusion": "Wniosek",
        "recommendation": "Zalecenie", "action": "Działanie", "responsible": "Odpowiedzialny",
        "due": "Termin", "priority": "Priorytet", "progress": "Postęp", "signatures": "Opinia i podpisy", "name_function": "Inicjały", "victim_sign": "Poszkodowany", "hierarchy_sign": "Linia hierarchiczna", "date": "Data", "signature": "Podpis", "employer_sign": "Pracodawca / przedstawiciel", "prevention_sign": "Doradca ds. prewencji / służba wewnętrzna",
    },
}


def _s(value, fallback="—"):
    if value is None or value == "":
        return fallback
    return str(value)


def _localized(item, base, lang):
    return item.get(f"{base}_{lang}") or item.get(f"{base}_fr") or item.get(base) or "—"


class RiskyDocTemplate(BaseDocTemplate):
    def __init__(self, buffer, event_number, title, **kwargs):
        super().__init__(buffer, **kwargs)
        self.event_number = event_number
        self.report_title = title
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates(PageTemplate(id="risky", frames=frame, onPage=self._page))

    def _page(self, canvas, doc):
        canvas.saveState()
        if doc.page > 2:
            canvas.setFillColor(NAVY)
            canvas.rect(0, A4[1] - 8 * mm, A4[0], 8 * mm, fill=1, stroke=0)
            canvas.setFillColor(ORANGE)
            canvas.rect(0, A4[1] - 8 * mm, 34 * mm, 8 * mm, fill=1, stroke=0)
            canvas.setFont("Helvetica-Bold", 7.5)
            canvas.setFillColor(colors.white)
            canvas.drawString(38 * mm, A4[1] - 5.4 * mm, f"RISKY QHSE  ·  {self.event_number}")
            canvas.setStrokeColor(MID)
            canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
            canvas.setFont("Helvetica", 7.5)
            canvas.setFillColor(MUTED)
            canvas.drawString(18 * mm, 9 * mm, self.report_title[:70])
            canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, f"Page {doc.page}")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            key = flowable.style.name
            if key.startswith("Section"):
                level = 0
                text = flowable.getPlainText()
                self.notify("TOCEntry", (level, text, self.page))



CIRC_CAUSE_LABELS = {
    "fr": {
        "product": "Produits",
        "machine": "Machines",
        "tool": "Outils",
        "orderCleanliness": "Ordre et propreté",
        "transport": "Moyens de transport",
        "materialOther": "Autres facteurs matériels",
        "collectiveAbsent": "EPC absent",
        "collectiveMissing": "EPC manquant ou enlevé",
        "collectiveDisabled": "EPC court-circuité",
        "collectiveOther": "Autre défaut d’EPC",
        "ppeMisuse": "Mauvais emploi de l’EPI",
        "ppeAbsent": "EPI absent",
        "ppeUnsuitable": "EPI pas adapté",
        "ppeOther": "Autre défaut d’EPI",
        "lighting": "Éclairage",
        "noise": "Bruit",
        "temperature": "Température",
        "environmentOther": "Autre facteur environnemental",
        "riskAnalysis": "Analyse de risque non effectuée ou incomplète",
        "instructions": "Instructions manquantes ou incomplètes",
        "sippOperation": "Fonctionnement du SIPP",
        "organizationOther": "Autre cause organisationnelle",
        "followupControl": "Contrôle lacunaire du suivi des instructions",
        "trainingGap": "Manque de formation",
        "communicationOther": "Autre cause de communication",
        "distraction": "Distraction",
        "intentionalNegligence": "Négligence intentionnelle",
        "fatigue": "Fatigue",
        "incompetence": "Incompétence",
        "haste": "Précipitation",
        "humanOther": "Autre facteur humain",
        "designManufacturing": "Faute de conception ou de fabrication d’une machine",
        "noncompliantEquipment": "Utilisation d’un équipement de travail non conforme",
        "badAdvice": "Mauvais avis",
        "instructionsNotFollowed": "Non-suivi des instructions",
        "sitePressure": "Pression de chantier",
        "thirdOrganizationOther": "Autre cause organisationnelle chez un tiers"
    },
    "pl": {
        "product": "Produits",
        "machine": "Machines",
        "tool": "Outils",
        "orderCleanliness": "Ordre et propreté",
        "transport": "Moyens de transport",
        "materialOther": "Autres facteurs matériels",
        "collectiveAbsent": "EPC absent",
        "collectiveMissing": "EPC manquant ou enlevé",
        "collectiveDisabled": "EPC court-circuité",
        "collectiveOther": "Autre défaut d’EPC",
        "ppeMisuse": "Mauvais emploi de l’EPI",
        "ppeAbsent": "EPI absent",
        "ppeUnsuitable": "EPI pas adapté",
        "ppeOther": "Autre défaut d’EPI",
        "lighting": "Éclairage",
        "noise": "Bruit",
        "temperature": "Température",
        "environmentOther": "Autre facteur environnemental",
        "riskAnalysis": "Analyse de risque non effectuée ou incomplète",
        "instructions": "Instructions manquantes ou incomplètes",
        "sippOperation": "Fonctionnement du SIPP",
        "organizationOther": "Autre cause organisationnelle",
        "followupControl": "Contrôle lacunaire du suivi des instructions",
        "trainingGap": "Manque de formation",
        "communicationOther": "Autre cause de communication",
        "distraction": "Distraction",
        "intentionalNegligence": "Négligence intentionnelle",
        "fatigue": "Fatigue",
        "incompetence": "Incompétence",
        "haste": "Précipitation",
        "humanOther": "Autre facteur humain",
        "designManufacturing": "Faute de conception ou de fabrication d’une machine",
        "noncompliantEquipment": "Utilisation d’un équipement de travail non conforme",
        "badAdvice": "Mauvais avis",
        "instructionsNotFollowed": "Non-suivi des instructions",
        "sitePressure": "Pression de chantier",
        "thirdOrganizationOther": "Autre cause organisationnelle chez un tiers"
    },
    "en": {
        "product": "Produits",
        "machine": "Machines",
        "tool": "Outils",
        "orderCleanliness": "Ordre et propreté",
        "transport": "Moyens de transport",
        "materialOther": "Autres facteurs matériels",
        "collectiveAbsent": "EPC absent",
        "collectiveMissing": "EPC manquant ou enlevé",
        "collectiveDisabled": "EPC court-circuité",
        "collectiveOther": "Autre défaut d’EPC",
        "ppeMisuse": "Mauvais emploi de l’EPI",
        "ppeAbsent": "EPI absent",
        "ppeUnsuitable": "EPI pas adapté",
        "ppeOther": "Autre défaut d’EPI",
        "lighting": "Éclairage",
        "noise": "Bruit",
        "temperature": "Température",
        "environmentOther": "Autre facteur environnemental",
        "riskAnalysis": "Analyse de risque non effectuée ou incomplète",
        "instructions": "Instructions manquantes ou incomplètes",
        "sippOperation": "Fonctionnement du SIPP",
        "organizationOther": "Autre cause organisationnelle",
        "followupControl": "Contrôle lacunaire du suivi des instructions",
        "trainingGap": "Manque de formation",
        "communicationOther": "Autre cause de communication",
        "distraction": "Distraction",
        "intentionalNegligence": "Négligence intentionnelle",
        "fatigue": "Fatigue",
        "incompetence": "Incompétence",
        "haste": "Précipitation",
        "humanOther": "Autre facteur humain",
        "designManufacturing": "Faute de conception ou de fabrication d’une machine",
        "noncompliantEquipment": "Utilisation d’un équipement de travail non conforme",
        "badAdvice": "Mauvais avis",
        "instructionsNotFollowed": "Non-suivi des instructions",
        "sitePressure": "Pression de chantier",
        "thirdOrganizationOther": "Autre cause organisationnelle chez un tiers"
    },
    "nl": {
        "product": "Produits",
        "machine": "Machines",
        "tool": "Outils",
        "orderCleanliness": "Ordre et propreté",
        "transport": "Moyens de transport",
        "materialOther": "Autres facteurs matériels",
        "collectiveAbsent": "EPC absent",
        "collectiveMissing": "EPC manquant ou enlevé",
        "collectiveDisabled": "EPC court-circuité",
        "collectiveOther": "Autre défaut d’EPC",
        "ppeMisuse": "Mauvais emploi de l’EPI",
        "ppeAbsent": "EPI absent",
        "ppeUnsuitable": "EPI pas adapté",
        "ppeOther": "Autre défaut d’EPI",
        "lighting": "Éclairage",
        "noise": "Bruit",
        "temperature": "Température",
        "environmentOther": "Autre facteur environnemental",
        "riskAnalysis": "Analyse de risque non effectuée ou incomplète",
        "instructions": "Instructions manquantes ou incomplètes",
        "sippOperation": "Fonctionnement du SIPP",
        "organizationOther": "Autre cause organisationnelle",
        "followupControl": "Contrôle lacunaire du suivi des instructions",
        "trainingGap": "Manque de formation",
        "communicationOther": "Autre cause de communication",
        "distraction": "Distraction",
        "intentionalNegligence": "Négligence intentionnelle",
        "fatigue": "Fatigue",
        "incompetence": "Incompétence",
        "haste": "Précipitation",
        "humanOther": "Autre facteur humain",
        "designManufacturing": "Faute de conception ou de fabrication d’une machine",
        "noncompliantEquipment": "Utilisation d’un équipement de travail non conforme",
        "badAdvice": "Mauvais avis",
        "instructionsNotFollowed": "Non-suivi des instructions",
        "sitePressure": "Pression de chantier",
        "thirdOrganizationOther": "Autre cause organisationnelle chez un tiers"
    }
}


class CauseTreeFlowable(Flowable):
    """Arbre vectoriel vertical : causes en haut, fait final en bas."""

    def __init__(self, tree, width=153 * mm):
        super().__init__()
        self.tree = tree or {}
        self.width = width
        count = len(self.tree.get("facts") or [])
        self.height = min(150 * mm, max(72 * mm, (62 + count * 9) * mm))

    def wrap(self, availWidth, availHeight):
        self._draw_width = min(self.width, availWidth)
        self._draw_height = min(self.height, max(55 * mm, availHeight))
        return self._draw_width, self._draw_height

    def draw(self):
        facts = self.tree.get("facts") or []
        relations = self.tree.get("relations") or []
        if not facts:
            return
        by_id = {f["id"]: f for f in facts}
        effects = {r.get("effect_fact_id") for r in relations}
        causes = {r.get("cause_fact_id") for r in relations}
        finals = [f for f in facts if str(f.get("fact_type") or "").upper() == "FINAL"]
        if not finals:
            finals = [f for f in facts if f["id"] in effects and f["id"] not in causes]
        final_id = finals[0]["id"] if finals else facts[0]["id"]
        depth = {final_id: 0}
        changed = True
        while changed:
            changed = False
            for rel in relations:
                cause_id, effect_id = rel.get("cause_fact_id"), rel.get("effect_fact_id")
                if effect_id in depth:
                    nd = depth[effect_id] + 1
                    if depth.get(cause_id, -1) < nd:
                        depth[cause_id] = nd
                        changed = True
        for fact in facts:
            depth.setdefault(fact["id"], int(fact.get("level") or 0))
        max_depth = max(depth.values()) if depth else 0
        node_w, node_h = 43 * mm, 20 * mm
        margin_y = 4 * mm
        usable_h = self._draw_height - 2 * margin_y
        positions = {}
        for d in range(max_depth, -1, -1):
            items = sorted([f for f in facts if depth.get(f["id"]) == d], key=lambda x:(x.get("sort_order") or 0,x.get("id") or 0))
            if not items: continue
            y = margin_y + (max_depth - d) * (usable_h - node_h) / max(1, max_depth)
            slot = self._draw_width / len(items)
            for idx, fact in enumerate(items):
                positions[fact["id"]] = (idx * slot + (slot-node_w)/2, y)
        canvas=self.canv; canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#667C98")); canvas.setLineWidth(1.15)
        for rel in relations:
            a,b=positions.get(rel.get("cause_fact_id")),positions.get(rel.get("effect_fact_id"))
            if not a or not b: continue
            x1,y1=a[0]+node_w/2,a[1]; x2,y2=b[0]+node_w/2,b[1]+node_h
            canvas.line(x1,y1,x2,y2)
        node_style=ParagraphStyle("CauseTreeNode",fontName="Helvetica",fontSize=7.6,leading=9.2,textColor=TEXT)
        label_style=ParagraphStyle("CauseTreeLabel",fontName="Helvetica-Bold",fontSize=6.2,leading=7,textColor=colors.HexColor("#456078"))
        for fact_id,(x,y) in positions.items():
            fact=by_id[fact_id]; is_final=fact_id==final_id; is_terminal=bool(fact.get("is_terminal"))
            border=NAVY if is_final else ORANGE if is_terminal else colors.HexColor("#C7D3DC")
            canvas.setFillColor(IVORY); canvas.setStrokeColor(border); canvas.setLineWidth(1.3 if (is_final or is_terminal) else .7)
            canvas.roundRect(x,y,node_w,node_h,5,fill=1,stroke=1)
            label="FAIT FINAL" if is_final else ("CAUSE TERMINALE" if is_terminal else "CAUSE")
            lp=Paragraph(label,label_style); _,lh=lp.wrap(node_w-5*mm,5*mm); lp.drawOn(canvas,x+2.5*mm,y+node_h-lh-2*mm)
            p=Paragraph(escape(_s(fact.get("description"))),node_style); _,ph=p.wrap(node_w-5*mm,node_h-8*mm); p.drawOn(canvas,x+2.5*mm,y+2.5*mm)
        canvas.restoreState()



def render_accident_report_pdf(data: dict, db, language: str = "fr") -> bytes:
    lang = language.split("-")[0].lower()
    if lang not in I18N:
        lang = "fr"
    tr = I18N[lang]
    event = data["event"]
    buffer = BytesIO()

    doc = RiskyDocTemplate(
        buffer,
        event_number=data["event_number"],
        title=event.get("description") or "",
        pagesize=A4,
        rightMargin=18 * mm, leftMargin=18 * mm, topMargin=18 * mm, bottomMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    body = ParagraphStyle("BodyRisky", parent=styles["BodyText"], fontName="Helvetica", fontSize=9, leading=13, textColor=TEXT)
    small = ParagraphStyle("SmallRisky", parent=body, fontSize=7.5, leading=10, textColor=MUTED)
    section = ParagraphStyle("SectionRisky", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=NAVY, spaceBefore=4 * mm, spaceAfter=5 * mm)
    subsection = ParagraphStyle("SubRisky", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10, textColor=NAVY, spaceBefore=3 * mm, spaceAfter=2 * mm)

    story = []

    # ========================================================
    # COUVERTURE
    # ========================================================
    story += [Spacer(1, 12 * mm)]
    cover_bar = Table([["RISKY", "QHSE"]], colWidths=[105 * mm, 35 * mm], rowHeights=[16 * mm])
    cover_bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), NAVY), ("BACKGROUND", (1, 0), (1, 0), ORANGE),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white), ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (0, 0), 24), ("FONTSIZE", (1, 0), (1, 0), 12),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 6 * mm),
    ]))
    story += [cover_bar, Spacer(1, 7 * mm)]
    accent = Table([[""]], colWidths=[140 * mm], rowHeights=[2.2 * mm])
    accent.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ORANGE)]))
    story += [accent, Spacer(1, 19 * mm)]
    story.append(Paragraph(escape(tr["report"]), ParagraphStyle("CoverTitle", parent=section, fontSize=25, leading=30, spaceAfter=10 * mm)))
    story.append(Paragraph(escape(data["event_number"]), ParagraphStyle("CoverNo", parent=body, fontName="Helvetica-Bold", fontSize=17, textColor=ORANGE, spaceAfter=6 * mm)))
    story.append(Paragraph(escape(_s(event.get("description"))), ParagraphStyle("CoverEvent", parent=body, fontName="Helvetica-Bold", fontSize=20, leading=25, textColor=TEXT, spaceAfter=16 * mm)))

    cover_rows = [
        [tr["organization"], _s(event.get("organization_name"))],
        [tr["event_type"], _s(event.get("event_type"))],
        [tr["event_date"], _s(event.get("event_date"))],
        [tr["location"], _s(event.get("location"))],
        [tr["analysis"], _s(event.get("analysis_type"))],
    ]
    ct = Table([[Paragraph(f"<b>{escape(a)}</b>", body), Paragraph(escape(b), body)] for a, b in cover_rows], colWidths=[48 * mm, 92 * mm])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT), ("BOX", (0, 0), (-1, -1), .5, BEIGE_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), .35, MID), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story += [ct, Spacer(1, 22 * mm)]
    story.append(Paragraph(f"{escape(tr['version'])} 1.0&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;{escape(tr['generated'])}: {__import__('datetime').date.today().isoformat()}", small))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(escape(tr["generated_by"]), small))
    story.append(PageBreak())

    # ========================================================
    # TABLE DES MATIÈRES
    # ========================================================
    story.append(Paragraph(escape(tr["contents"]), ParagraphStyle("ContentsTitle", parent=section, fontSize=20)))
    story.append(Spacer(1, 5 * mm))
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("TOC0", fontName="Helvetica", fontSize=10, leading=18, leftIndent=0, firstLineIndent=0, textColor=TEXT)]
    story += [toc, PageBreak()]

    def heading(no, key):
        number = Paragraph(
            f"<b>{no:02d}</b>",
            ParagraphStyle(
                f"SectionNumber{no}", parent=body, fontName="Helvetica-Bold",
                fontSize=10, textColor=ORANGE, alignment=TA_CENTER,
            ),
        )
        title = Paragraph(
            f"<b>{escape(tr[key])}</b>",
            ParagraphStyle(
                f"SectionRisky{no}", parent=section, fontSize=14, leading=17,
                textColor=NAVY, spaceBefore=0, spaceAfter=0,
            ),
        )
        banner = Table([[number, title]], colWidths=[12 * mm, 141 * mm], hAlign="LEFT")
        banner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
            ("LINEBELOW", (0, 0), (-1, -1), .6, MID),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (0, 0), 0),
            ("LEFTPADDING", (1, 0), (1, 0), 2 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.extend([banner, Spacer(1, 4 * mm)])

    def info_table(rows):
        """Grille de cartes, calquée sur l'aperçu web du rapport."""
        usable = [(a, b) for a, b in rows if b not in (None, "")]
        if not usable:
            story.append(Paragraph(escape(tr["not_provided"]), body))
            return

        cells = []
        label_style = ParagraphStyle("CardLabel", parent=small, fontSize=7.2, leading=9, textColor=MUTED)
        value_style = ParagraphStyle("CardValue", parent=body, fontName="Helvetica-Bold", fontSize=9.2, leading=12)
        for label, value in usable:
            card = Table(
                [[Paragraph(escape(_s(label)), label_style)],
                 [Paragraph(escape(_s(value)), value_style)]],
                colWidths=[72.5 * mm],
            )
            card.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), IVORY),
                ("BOX", (0, 0), (-1, -1), .55, BEIGE_BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 7),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                ("TOPPADDING", (0, 1), (-1, 1), 2),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            cells.append(card)

        rows_out = []
        for i in range(0, len(cells), 2):
            row = cells[i:i + 2]
            if len(row) == 1:
                row.append("")
            rows_out.append(row)
        grid = Table(rows_out, colWidths=[76.5 * mm, 76.5 * mm], hAlign="LEFT")
        grid.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(grid)

    # 01
    heading(1, "summary")
    info_table([
        (tr["description"], event.get("description")),
        (tr["event_type"], event.get("event_type")), (tr["event_date"], event.get("event_date")),
        (tr["person"], event.get("person_name")), ("Catégorie", event.get("person_category")),
        (tr["organization"], event.get("organization_name")), (tr["location"], event.get("location")),
        ("Project Manager", event.get("project_manager")), ("Chef de chantier", event.get("site_supervisor")),
        ("Dégâts matériels", "Oui" if event.get("material_damage") else "Non"),
        ("Dégâts environnementaux", "Oui" if event.get("environmental_damage") else "Non"),
        (tr["analysis"], "Circonstancié" if data.get("circumstantial_report") else event.get("analysis_type")),
        ("Arrêt de travail", f"Oui — {event.get('lost_days') or 0} jours" if event.get("lost_time") else "Non"),
        ("Travail adapté", f"Oui — {event.get('modified_duty_days') or 0} jours" if event.get("modified_duty") else "Non"),
        ("Incapacité permanente", "Oui" if event.get("permanent_injury") else "Non"),
        ("Décès", "Oui" if event.get("fatal") else "Non"),
        ("Coût dégâts matériels (€)", event.get("material_damage_cost") if event.get("material_damage") else tr["not_applicable"]),
    ])

    # 02
    heading(2, "facts")
    facts = data.get("facts") or {}
    info_table([
        (tr["client"], facts.get("client")), (tr["worksite"], facts.get("worksite")),
        (tr["witnesses"], facts.get("witnesses")), (tr["activity"], facts.get("activity_before_event")),
        (tr["description"], facts.get("event_description")), (tr["direct_cause"], facts.get("direct_cause")),
    ])

    # 03 — DONNÉES COMPLÉMENTAIRES DU CIRCONSTANCIÉ
    circ = data.get("circumstantial_report")
    if circ:
        heading(3, "circ_details")
        info_table([
            ("Adresse de la victime", circ.get("victim_address")),
            ("Date de naissance", circ.get("victim_birth_date")),
            ("Ancienneté dans l’entreprise", circ.get("victim_company_seniority")),
            ("Ancienneté dans la fonction", circ.get("victim_job_seniority")),
            ("Employeur", circ.get("employer_name")),
            ("Adresse de l’employeur", circ.get("employer_address")),
            ("Assureur accidents du travail", circ.get("insurer_name")),
            ("N° de police", circ.get("insurance_policy_number")),
            ("Conseiller en prévention", circ.get("prevention_advisor")),
            ("Responsable SIPP", circ.get("sipp_manager")),
            ("SEPP", circ.get("sepp_name")),
            ("Coordonnées SEPP", circ.get("sepp_contact")),
            ("Personnes ayant participé à l’élaboration", circ.get("report_contributors")),
            ("Destinataires du rapport", circ.get("report_recipients")),
        ])

    # 04
    heading(4, "photos")
    photos = get_event_photos(db=db, event_id=data["event_id"])
    if not photos:
        story.append(Paragraph(escape(tr["not_provided"]), body))
    else:
        cells = []
        storage_root = STORAGE_ROOT.parent.parent
        for photo in photos:
            p = storage_root / photo.storage_path
            if p.exists():
                # Une liste/KeepTogether dans une cellule de Table peut être
                # mesurée par ReportLab comme une hauteur quasi infinie.
                # Une sous-table donne une hauteur déterministe et conserve
                # image + légende ensemble.
                img = Image(str(p))
                img._restrictSize(68 * mm, 48 * mm)
                caption = Paragraph(
                    escape(photo.caption or photo.original_filename),
                    small,
                )
                cell = Table(
                    [[img], [caption]],
                    colWidths=[70 * mm],
                )
                cell.setStyle(TableStyle([
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]))
                cells.append(cell)
        for i in range(0, len(cells), 2):
            row = cells[i:i+2]
            if len(row) == 1:
                row.append("")
            table = Table([row], colWidths=[78 * mm, 78 * mm])
            table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 0), (-1, -1), .4, MID),
                ("INNERGRID", (0, 0), (-1, -1), .25, MID),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]))
            story += [table, Spacer(1, 3 * mm)]

    # 05
    heading(5, "classification")
    cl = data.get("classification") or {}
    info_table([
        (tr["deviation"], f"{_s(cl.get('deviation_code'))} — {_s(_localized(cl, 'deviation_label', lang))}"),
        (tr["agent"], f"{_s(cl.get('material_agent_code'))} — {_s(_localized(cl, 'material_agent_label', lang))}"),
        (tr["injury"], f"{_s(cl.get('injury_nature_code'))} — {_s(_localized(cl, 'injury_nature_label', lang))}"),
        (tr["injury_location"], f"{_s(cl.get('injury_location_code'))} — {_s(_localized(cl, 'injury_location_label', lang))}"),
    ])

    # 06 — ANALYSE COMPLÉMENTAIRE DES CAUSES
    if circ:
        import json
        heading(6, "circ_causes")
        try:
            selected = set(json.loads(circ.get("cause_selections_json") or "[]"))
        except (TypeError, ValueError, json.JSONDecodeError):
            selected = set()
        groups = [
            ("Causes primaires · matérielles", ["product","machine","tool","orderCleanliness","transport","materialOther","collectiveAbsent","collectiveMissing","collectiveDisabled","collectiveOther","ppeMisuse","ppeAbsent","ppeUnsuitable","ppeOther","lighting","noise","temperature","environmentOther"], circ.get("primary_details")),
            ("Causes secondaires · organisationnelles", ["riskAnalysis","instructions","sippOperation","organizationOther","followupControl","trainingGap","communicationOther","distraction","intentionalNegligence","fatigue","incompetence","haste","humanOther"], circ.get("secondary_details")),
            ("Causes tertiaires · tiers", ["designManufacturing","noncompliantEquipment","badAdvice","instructionsNotFollowed","sitePressure","thirdOrganizationOther"], circ.get("tertiary_details")),
        ]
        for title, codes, details in groups:
            chosen = [code for code in codes if code in selected]
            labels = CIRC_CAUSE_LABELS.get(lang, CIRC_CAUSE_LABELS["fr"])
            content = "   ".join(f"✓ {labels.get(code, code)}" for code in chosen) if chosen else tr["not_provided"]
            rows = [[Paragraph(f"<b>{escape(title)}</b>", body)], [Paragraph(escape(content), body)]]
            if details:
                rows.append([Paragraph(escape(_s(details)), small)])
            card = Table(rows, colWidths=[153 * mm])
            card.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),IVORY),("BOX",(0,0),(-1,-1),.5,BEIGE_BORDER),
                ("PADDING",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"TOP")
            ]))
            story += [card, Spacer(1, 3 * mm)]

    # 07
    heading(7, "heepo")
    heepo = data.get("heepo") or []
    if not heepo:
        story.append(Paragraph(escape(tr["not_provided"]), body))
    else:
        rows = [["", ""]]
        rows = [[Paragraph("<b>Famille</b>", body), Paragraph("<b>Facteur</b>", body)]]
        for item in heepo:
            label = item.get("other_text") if item.get("factor_code") == "OTHER" else _localized(item, "factor_label", lang)
            rows.append([Paragraph(escape(_s(item.get("family"))), body), Paragraph(escape(_s(label)), body)])
        table = Table(rows, colWidths=[42 * mm, 111 * mm], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), NAVY), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("BOX",(0,0),(-1,-1),.4,MID), ("INNERGRID",(0,0),(-1,-1),.25,MID), ("VALIGN",(0,0),(-1,-1),"TOP"), ("PADDING",(0,0),(-1,-1),6)]))
        story.append(table)

    # 08
    heading(8, "jc")
    jc = data.get("just_culture")
    if not jc:
        story.append(Paragraph(escape(tr["not_applicable"]), body))
    else:
        conclusion = _localized(jc, "conclusion_label", lang)
        recommendation = _localized(jc, "recommendation_label", lang)
        code = jc.get("recommendation_code")
        bg = GREEN if code == "ACCOMPAGNEMENT" else YELLOW if code == "AVERTISSEMENT_VERBAL" else ORANGE_LIGHT if code in {"PREMIER_AVERTISSEMENT_ECRIT","DERNIER_AVERTISSEMENT_ECRIT"} else RED if code == "LICENCIEMENT" else LIGHT
        table = Table([
            [Paragraph(f"<b>{escape(tr['conclusion'])}</b>", body), Paragraph(escape(_s(conclusion)), body)],
            [Paragraph(f"<b>{escape(tr['recommendation'])}</b>", body), Paragraph(escape(_s(recommendation)), body)],
        ], colWidths=[45 * mm, 108 * mm])
        table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),("BOX",(0,0),(-1,-1),.7,ORANGE),("INNERGRID",(0,0),(-1,-1),.3,MID),("PADDING",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"TOP")]))
        story.append(table)

    # 09 — ARBRE DES CAUSES : hauteur adaptative dans le flux
    heading(9, "tree")
    tree = data.get("cause_tree")
    if not tree or not tree.get("facts"):
        story.append(Paragraph(escape(tr["not_provided"]), body))
    else:
        story.append(CauseTreeFlowable(tree))
        story.append(Spacer(1, 5 * mm))

    # 10
    heading(10, "actions")
    actions = data.get("actions") or []
    if not actions:
        story.append(Paragraph(escape(tr["not_provided"]), body))
    else:
        rows = [[Paragraph(f"<b>{escape(tr[k])}</b>", small) for k in ("action","responsible","due","priority","progress")]]
        for a in actions:
            pct = a.get("progress_percent")
            progress = f"{pct} %" if pct is not None else (a.get("process_code") or "—")
            if isinstance(pct, (int, float)):
                pct_safe = max(0, min(100, pct))
                filled = max(0.1, 18 * mm * pct_safe / 100)
                empty = max(0.1, 18 * mm - filled)
                progress_cell = Table(
                    [[Paragraph(f"<b>{escape(progress)}</b>", small)], ["", ""]],
                    colWidths=[filled, empty],
                    rowHeights=[5 * mm, 2.2 * mm],
                )
                progress_cell.setStyle(TableStyle([
                    ("SPAN", (0, 0), (1, 0)),
                    ("BACKGROUND", (0, 1), (0, 1), ORANGE if pct_safe < 100 else colors.HexColor("#2E8B57")),
                    ("BACKGROUND", (1, 1), (1, 1), MID),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]))
            else:
                progress_cell = Paragraph(escape(progress), small)
            rows.append([
                Paragraph(escape(_s(a.get("description"))), small), Paragraph(escape(_s(a.get("responsible_text"))), small),
                Paragraph(escape(_s(a.get("due_date"))), small), Paragraph(escape(_s(a.get("priority"))), small),
                progress_cell,
            ])
        table = Table(rows, colWidths=[65 * mm, 32 * mm, 22 * mm, 20 * mm, 20 * mm], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),("BOX",(0,0),(-1,-1),.4,MID),("INNERGRID",(0,0),(-1,-1),.25,MID),("VALIGN",(0,0),(-1,-1),"TOP"),("PADDING",(0,0),(-1,-1),5)]))
        story.append(table)

    # 11 — AVIS & SIGNATURES, UNIQUEMENT POUR UN CIRCONSTANCIÉ
    if circ:
        story.append(PageBreak())
        heading(11, "signatures")
        sign_cards = []
        for role in (tr["victim_sign"], tr["hierarchy_sign"], tr["prevention_sign"], tr["employer_sign"]):
            card = Table([
                [Paragraph(f"<b>{escape(role)}</b>", body)],
                [Paragraph(f"{escape(tr['name_function'])}: ____________________", small)],
                [Paragraph(f"{escape(tr['date'])}: ____________________", small)],
                [Spacer(1, 18 * mm)],
                [Paragraph(escape(tr["signature"]), small)],
            ], colWidths=[72.5 * mm], rowHeights=[None, None, None, 20 * mm, None])
            card.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), IVORY), ("BOX", (0, 0), (-1, -1), .6, BEIGE_BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            sign_cards.append(card)
        sign_grid = Table([sign_cards[:2], sign_cards[2:]], colWidths=[76.5 * mm, 76.5 * mm])
        sign_grid.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(sign_grid)

    doc.multiBuild(story)
    return buffer.getvalue()
