from backend.database import SessionLocal
from backend import models


# ========================================================
# JUST CULTURE — TRADUCTIONS DES NŒUDS
# ========================================================

TRANSLATIONS = {
    "ID 3": {
        "nl": "Waren de handelingen opzettelijk?",
        "en": "Were the actions intentional?",
    },
    "ID 4": {
        "nl": "Waren de resultaten zoals verwacht?",
        "en": "Were the outcomes as expected?",
    },
    "ID 5": {
        "nl": "SABOTAGE of KWAADWILLIGE HANDELING",
        "en": "SABOTAGE or MALICIOUS ACT",
        "conclusion_nl": "Sabotage of kwaadwillige handeling",
        "conclusion_en": "Sabotage or malicious act",
        "recommendation_nl": "Ontslag",
        "recommendation_en": "Dismissal",
    },
    "ID 10": {
        "nl": "Opzettelijke overtreding van veilige werkprocedures?",
        "en": "Deliberate violation of safe operating procedures?",
    },
    "ID 12": {
        "nl": (
            "Waren de procedures:\n"
            "- beschikbaar;\n"
            "- toepasbaar;\n"
            "- begrijpelijk;\n"
            "- correct?"
        ),
        "en": (
            "Were the procedures:\n"
            "- available;\n"
            "- applicable;\n"
            "- understandable;\n"
            "- correct?"
        ),
    },
    "ID 13": {
        "nl": "Roekeloze overtreding",
        "en": "Reckless violation",
    },
    "ID 14": {
        "nl": "Door het systeem veroorzaakte overtreding",
        "en": "System-induced violation",
    },
    "ID 15": {
        "nl": (
            "Doorstaat de substitutie-/gelijkwaardigheidstest?\n"
            "« Zou ik in deze omstandigheden hetzelfde "
            "hebben gedaan? »"
        ),
        "en": (
            "Does the substitution / equivalence test pass?\n"
            "“Would I have done the same thing in these "
            "circumstances?”"
        ),
    },
    "ID 16": {
        "nl": (
            "Tekortkomingen in opleiding, selectie of "
            "gebrek aan ervaring?"
        ),
        "en": (
            "Deficiencies in training, selection or "
            "lack of experience?"
        ),
    },
    "ID 17": {
        "nl": "Nalatigheid",
        "en": "Negligence",
        "conclusion_nl": "Nalatigheid",
        "conclusion_en": "Negligence",
        "recommendation_nl": "Begeleiding",
        "recommendation_en": "Coaching",
    },
    "ID 18": {
        "nl": "Door het systeem veroorzaakte overtreding / fout",
        "en": "System-induced violation / error",
    },
    "ID 19": {
        "nl": (
            "Voorgeschiedenis van onveilige handelingen / "
            "niet-naleving van procedures?"
        ),
        "en": (
            "History of unsafe acts / non-compliance "
            "with procedures?"
        ),
    },
    "ID 20": {
        "nl": (
            "Fout zonder verwijt, maar corrigerende opleiding "
            "of begeleiding is vereist."
        ),
        "en": (
            "Blameless error, but corrective training "
            "or coaching is required."
        ),
    },
    "ID 21": {
        "nl": "Fout zonder verwijt",
        "en": "Blameless error",
    },
    "ID 71": {
        "nl": (
            "Heeft de persoon de handeling, gebeurtenis of "
            "het gedrag gekozen uit persoonlijk belang?"
        ),
        "en": (
            "Did the person choose the action, event or "
            "behavior for personal benefit?"
        ),
    },
    "ID 69": {
        "nl": (
            "Dacht de persoon dat de alternatieve handeling "
            "gunstig zou zijn voor het bedrijf?"
        ),
        "en": (
            "Did the person believe the alternative action "
            "would benefit the company?"
        ),
    },
    "ID 74": {
        "nl": (
            "Was de persoon zich er niet van bewust dat hij/zij "
            "de bestaande procedures niet naleefde?"
        ),
        "en": (
            "Was the person unaware that they were not "
            "following the existing procedures?"
        ),
    },
    "ID 75": {
        "nl": (
            "Is de regel goed bekend, maar is het lokaal "
            "gebruikelijk om deze te negeren?"
        ),
        "en": (
            "Is the rule well known, but is local custom "
            "and practice to disregard it?"
        ),
    },
    "ID 76": {
        "nl": (
            "Persoonlijk voordeel: « Het was voor mij "
            "gemakkelijker om het zo te doen. »"
        ),
        "en": (
            "Personal gain: “It was easier for me "
            "to do it this way.”"
        ),
        "conclusion_nl": "Persoonlijk voordeel",
        "conclusion_en": "Personal gain",
        "recommendation_nl": "Laatste schriftelijke waarschuwing",
        "recommendation_en": "Final written warning",
    },
    "ID 78": {
        "nl": (
            "Voordeel voor het bedrijf: « Ik dacht dat het "
            "beter was voor het bedrijf om het zo te doen. »"
        ),
        "en": (
            "Benefit to the company: “I thought it was better "
            "for the company to do it this way.”"
        ),
        "conclusion_nl": "Voordeel voor het bedrijf",
        "conclusion_en": "Benefit to the company",
        "recommendation_nl": "Eerste schriftelijke waarschuwing",
        "recommendation_en": "First written warning",
    },
    "ID 97": {
        "nl": (
            "Routineovertreding: « Maar iedereen doet het "
            "hier zo. »"
        ),
        "en": (
            "Routine violation: “But everyone does it "
            "this way here.”"
        ),
        "conclusion_nl": "Routineovertreding",
        "conclusion_en": "Routine violation",
        "recommendation_nl": "Eerste schriftelijke waarschuwing",
        "recommendation_en": "First written warning",
    },
    "ID 400": {
        "nl": "Opzettelijke en onregelmatige overtreding",
        "en": "Intentional and irregular violation",
        "conclusion_nl": (
            "Opzettelijke en onregelmatige overtreding"
        ),
        "conclusion_en": (
            "Intentional and irregular violation"
        ),
        "recommendation_nl": "Eerste schriftelijke waarschuwing",
        "recommendation_en": "First written warning",
    },
    "ID 105": {
        "nl": (
            "Gebaseerd op kennis: « Ik was niet op de hoogte / "
            "ik begreep de regel niet. »"
        ),
        "en": (
            "Knowledge-based: “I was not aware / "
            "I did not understand the rule.”"
        ),
        "conclusion_nl": "Kennisgebaseerde fout",
        "conclusion_en": "Knowledge-based error",
        "recommendation_nl": "Begeleiding",
        "recommendation_en": "Coaching",
    },
    "ID 147": {
        "nl": (
            "Denkt de persoon dat hij/zij op de juiste "
            "manier handelde?"
        ),
        "en": (
            "Does the person believe they were acting "
            "appropriately?"
        ),
    },
    "ID 162": {
        "nl": (
            "Fout: « Ik had niet verwacht dat dit "
            "zou gebeuren. »"
        ),
        "en": (
            "Error: “I did not expect this to happen.”"
        ),
        "conclusion_nl": "Fout",
        "conclusion_en": "Error",
        "recommendation_nl": "Begeleiding",
        "recommendation_en": "Coaching",
    },
    "ID 163": {
        "nl": (
            "Onoplettendheidsfout: « Ik had niet door "
            "wat er was gebeurd. »"
        ),
        "en": (
            "Inattention error: “I did not realize "
            "what had happened.”"
        ),
        "conclusion_nl": "Onoplettendheidsfout",
        "conclusion_en": "Inattention error",
        "recommendation_nl": "Begeleiding",
        "recommendation_en": "Coaching",
    },
    "ID 336": {
        "nl": (
            "Is het uitvoeren van deze taak volgens de "
            "vastgestelde procedure aanzienlijk moeilijk "
            "of onveilig?"
        ),
        "en": (
            "Is performing this task in accordance with "
            "the established procedure significantly "
            "difficult or unsafe?"
        ),
    },
    "ID 337": {
        "nl": (
            "Uitzonderlijke overtreding: het is in feite "
            "veiliger om de regel te negeren dan deze te volgen."
        ),
        "en": (
            "Exceptional violation: it is actually safer "
            "to disregard the rule than to follow it."
        ),
        "conclusion_nl": "Uitzonderlijke overtreding",
        "conclusion_en": "Exceptional violation",
        "recommendation_nl": "Mondelinge waarschuwing",
        "recommendation_en": "Verbal warning",
    },
    "ID 345": {
        "nl": (
            "Situationele overtreding: « Ik kan de taak niet "
            "uitvoeren als ik de regels volg, maar ik heb "
            "het toch gedaan. »"
        ),
        "en": (
            "Situational violation: “I cannot complete the "
            "task if I follow the rules, but I did it anyway.”"
        ),
        "conclusion_nl": "Situationele overtreding",
        "conclusion_en": "Situational violation",
        "recommendation_nl": "Mondelinge waarschuwing",
        "recommendation_en": "Verbal warning",
    },
}


# ========================================================
# JUST CULTURE — TRADUCTION DE L'ARBRE
# ========================================================

TREE_TRANSLATION = {
    "name_nl": "Beslissingsboom Just Culture",
    "name_en": "Just Culture Decision Tree",
    "description_nl": (
        "Gestructureerde analyse van gedrag in het kader "
        "van Just Culture. De conclusie en aanbeveling zijn "
        "beslissingsondersteunend en vervangen geen "
        "leidinggevende, HR- of juridische beoordeling."
    ),
    "description_en": (
        "Structured behavioral analysis within the Just Culture "
        "framework. The conclusion and recommendation provide "
        "decision support and do not replace managerial, HR "
        "or legal judgment."
    ),
}


# ========================================================
# JUST CULTURE — MISE À JOUR
# ========================================================

def main() -> None:
    db = SessionLocal()

    try:
        tree = (
            db.query(models.JustCultureTreeVersion)
            .filter(
                models.JustCultureTreeVersion.code
                == "JUST_CULTURE_REASON_FR",
                models.JustCultureTreeVersion.version
                == "1.0",
            )
            .first()
        )

        if tree is None:
            raise RuntimeError(
                "Arbre Just Culture 1.0 introuvable."
            )

        tree.name_nl = TREE_TRANSLATION["name_nl"]
        tree.name_en = TREE_TRANSLATION["name_en"]
        tree.description_nl = (
            TREE_TRANSLATION["description_nl"]
        )
        tree.description_en = (
            TREE_TRANSLATION["description_en"]
        )

        nodes = (
            db.query(models.JustCultureNode)
            .filter(
                models.JustCultureNode.tree_version_id
                == tree.id
            )
            .all()
        )

        updated_nodes = 0

        for node in nodes:
            translation = TRANSLATIONS.get(node.code)

            if translation is None:
                raise RuntimeError(
                    f"Traduction manquante pour {node.code}."
                )

            node.text_nl = translation["nl"]
            node.text_en = translation["en"]

            node.conclusion_label_nl = (
                translation.get("conclusion_nl")
            )
            node.conclusion_label_en = (
                translation.get("conclusion_en")
            )

            node.recommendation_label_nl = (
                translation.get("recommendation_nl")
            )
            node.recommendation_label_en = (
                translation.get("recommendation_en")
            )

            updated_nodes += 1

        # ----------------------------------------------------
        # Réponses OUI / NON
        # ----------------------------------------------------
        transitions = (
            db.query(models.JustCultureTransition)
            .join(
                models.JustCultureNode,
                models.JustCultureTransition.source_node_id
                == models.JustCultureNode.id,
            )
            .filter(
                models.JustCultureNode.tree_version_id
                == tree.id
            )
            .all()
        )

        updated_transitions = 0

        for transition in transitions:
            if transition.answer_code == "YES":
                transition.answer_label_nl = "JA"
                transition.answer_label_en = "YES"

            elif transition.answer_code == "NO":
                transition.answer_label_nl = "NEE"
                transition.answer_label_en = "NO"

            else:
                raise RuntimeError(
                    "Code de réponse inattendu : "
                    f"{transition.answer_code}"
                )

            updated_transitions += 1

        db.commit()

        print(
            f"{updated_nodes} nœuds Just Culture traduits."
        )
        print(
            f"{updated_transitions} transitions traduites."
        )
        print(
            "Arbre Just Culture FR/NL/EN mis à jour avec succès."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
    