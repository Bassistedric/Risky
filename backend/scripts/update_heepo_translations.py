# ============================================================
# RISKY — TRADUCTIONS DU RÉFÉRENTIEL HEEPO
# FR = label historique / NL = label_nl / EN = label_en
# ============================================================

from backend.database import SessionLocal
from backend.models import HeepoFactor


TRANSLATIONS = {
    # ========================================================
    # HOMME / MENS / HUMAN
    # ========================================================
    "H1": (
        "Collectieve beschermingsmiddelen niet gebruiken / uitschakelen",
        "Not using collective protective equipment / disabling it",
    ),
    "H2": (
        "Persoonlijke beschermingsmiddelen niet of verkeerd gebruiken",
        "Not using personal protective equipment / using it incorrectly",
    ),
    "H3": (
        "Veiligheidsinstructies niet volgen",
        "Not following safety instructions",
    ),
    "H4": (
        "Werkinstructies niet volgen",
        "Not following work instructions",
    ),
    "H5": (
        "Gereedschap verkeerd gebruiken",
        "Incorrect use of tools",
    ),
    "H6": (
        "Verkeerde positie / houding / hantering",
        "Incorrect position / posture / handling",
    ),
    "H7": (
        "Verkeerde handeling / verkeerde belasting",
        "Incorrect action / incorrect loading",
    ),
    "H8": (
        "Haast / nervositeit / conflicten",
        "Rushing / nervousness / conflicts",
    ),
    "H9": (
        "Afleiding / onoplettendheid",
        "Distraction / inattention",
    ),
    "H10": (
        "Werken onder spanning zonder toestemming / procedure",
        "Live electrical work without authorization / procedure",
    ),
    "H11": (
        "Elektrische veiligheidsafstanden niet naleven",
        "Failure to respect electrical safety distances",
    ),
    "H0": (
        "Andere",
        "Other",
    ),

    # ========================================================
    # EQUIPEMENT / UITRUSTING / EQUIPMENT
    # ========================================================
    "E1": (
        "Collectief beschermingsmiddel ontbreekt, is verwijderd of in slechte staat",
        "Collective protective equipment absent, removed or in poor condition",
    ),
    "E2": (
        "Persoonlijk beschermingsmiddel ontbreekt of is in slechte staat",
        "Personal protective equipment absent or in poor condition",
    ),
    "E3": (
        "Gereedschap of machine: in slechte staat",
        "Tool or machine: in poor condition",
    ),
    "E4": (
        "Gereedschap of machine: niet conform",
        "Tool or machine: non-compliant",
    ),
    "E5": (
        "Gereedschap of machine: gevaarlijk ontwerp / gevaarlijke constructie",
        "Tool or machine: hazardous design / construction",
    ),
    "E6": (
        "Ladder: in slechte staat",
        "Ladder: in poor condition",
    ),
    "E7": (
        "Niet-geïsoleerd gereedschap / niet geschikt voor de spanning",
        "Non-insulated tools / unsuitable for the voltage",
    ),
    "E8": (
        "Akoestisch / visueel alarm op machines ontbreekt of werkt niet",
        "Machine audible / visual alarm absent or defective",
    ),
    "E9": (
        "Gaslekdetectie ontbreekt of werkt niet",
        "Gas leak detection absent or not functioning",
    ),
    "E0": (
        "Andere",
        "Other",
    ),

    # ========================================================
    # ENVIRONNEMENT / OMGEVING / ENVIRONMENT
    # ========================================================
    "En1": (
        "Temperatuur / vochtigheid / lawaai / verlichting / trillingen",
        "Temperature / humidity / noise / lighting / vibrations",
    ),
    "En2": (
        "Vlakke vloer: in slechte staat",
        "Level floor: in poor condition",
    ),
    "En3": (
        "Trap of werkplatform: in slechte staat",
        "Stairs or work platform: in poor condition",
    ),
    "En4": (
        "Orde en netheid",
        "Order and cleanliness",
    ),
    "En5": (
        "Uitstekende elementen / stootgevaar",
        "Protruding elements / collision hazard",
    ),
    "En6": (
        "Personen of levende organismen",
        "People or living organisms",
    ),
    "En7": (
        "ATEX-zone of aanwezigheid van gevaarlijke gassen",
        "ATEX zone or presence of hazardous gases",
    ),
    "En8": (
        "Werkzaamheden in besloten ruimten of op daken (blootstelling aan valgevaar / wind)",
        "Work in confined spaces or on roofs (exposure to fall hazards / wind)",
    ),
    "En0": (
        "Andere",
        "Other",
    ),

    # ========================================================
    # PRODUIT / PRODUCT
    # ========================================================
    "P1": (
        "Niet-conform veiligheidsinformatieblad",
        "Non-compliant safety data sheet",
    ),
    "P2": (
        "Aard van het product (zwaar, scherp, glad, ...)",
        "Nature of the product (heavy, sharp, slippery, ...)",
    ),
    "P3": (
        "Gevaarlijke eigenschappen (ontvlambaar, giftig, ...)",
        "Hazardous properties (flammable, toxic, ...)",
    ),
    "P4": (
        "Niet-conforme / beschadigde verpakking",
        "Non-compliant / damaged packaging",
    ),
    "P5": (
        "Ontbrekende etikettering / identificatie van gevaren",
        "Missing labelling / hazard identification",
    ),
    "P6": (
        "Lek van koelmiddel (giftig / ontvlambaar)",
        "Refrigerant leak (toxic / flammable)",
    ),
    "P7": (
        "Gas onder druk",
        "Gas under pressure",
    ),
    "P8": (
        "Ontvlambaar isolatiemateriaal / giftig bij brand",
        "Flammable insulating material / toxic in case of fire",
    ),
    "P0": (
        "Andere",
        "Other",
    ),

    # ========================================================
    # ORGANISATION / ORGANISATIE / ORGANIZATION
    # ========================================================
    "O1": (
        "Slechte organisatie van de werkpost",
        "Poor organization of the workstation",
    ),
    "O2": (
        "Onvoldoende ruimte op de werkpost",
        "Insufficient space at the workstation",
    ),
    "O3": (
        "Gebrek aan instructies",
        "Lack of instructions",
    ),
    "O4": (
        "Gebrek aan opleiding",
        "Lack of training",
    ),
    "O5": (
        "Onjuiste informatie of instructies",
        "Incorrect information or instructions",
    ),
    "O6": (
        "Onvoldoende kennis van het werk",
        "Insufficient knowledge of the work",
    ),
    "O7": (
        "Onvoldoende kennis van de risico's",
        "Insufficient knowledge of the risks",
    ),
    "O8": (
        "Gebrek aan gereedschap",
        "Lack of tools",
    ),
    "O9": (
        "Ergonomie: niet optimaal",
        "Ergonomics: not optimal",
    ),
    "O10": (
        "Geen procedure voor vergrendeling / ontgrendeling",
        "No lockout / release procedure",
    ),
    "O11": (
        "Preventieplan onaangepast of ontbrekend",
        "Prevention plan unsuitable or absent",
    ),
    "O12": (
        "Geen coördinatie met andere vakdisciplines op de werf",
        "No coordination with other trades on site",
    ),
    "O0": (
        "Andere",
        "Other",
    ),
}


# ============================================================
# MISE À JOUR DE LA BASE
# ============================================================

def main() -> None:
    db = SessionLocal()

    try:
        factors = db.query(HeepoFactor).all()

        updated = 0
        missing = []

        for factor in factors:
            translation = TRANSLATIONS.get(factor.code)

            if translation is None:
                missing.append(factor.code)
                continue

            factor.label_nl = translation[0]
            factor.label_en = translation[1]
            updated += 1

        if missing:
            raise RuntimeError(
                "Traductions manquantes pour : "
                + ", ".join(sorted(missing))
            )

        db.commit()

        print(f"{updated} facteurs HEEPO traduits avec succès.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()