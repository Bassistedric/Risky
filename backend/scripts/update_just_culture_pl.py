from sqlalchemy import select

from backend.database import SessionLocal
from backend import models


NODE_TEXT_PL = {
    "ID 3": "Czy działania były zamierzone?",
    "ID 4": "Czy skutki były zgodne z oczekiwaniami?",
    "ID 5": "SABOTAŻ lub DZIAŁANIE W ZŁEJ WIERZE",
    "ID 10": "Czy doszło do świadomego naruszenia bezpiecznych procedur pracy?",
    "ID 12": "Czy procedury były:\n- dostępne;\n- możliwe do zastosowania;\n- zrozumiałe;\n- prawidłowe?",
    "ID 13": "Lekkomyślne naruszenie",
    "ID 14": "Naruszenie wywołane przez system",
    "ID 15": "Czy osoba przechodzi test substytucji / równoważności?\n„Czy w tych okolicznościach zrobił(a)bym to samo?”",
    "ID 16": "Czy występowały braki w szkoleniu, doborze pracownika lub brak doświadczenia?",
    "ID 17": "Zaniedbanie",
    "ID 18": "Naruszenie / błąd wywołany przez system",
    "ID 19": "Czy występowały wcześniej niebezpieczne działania / nieprzestrzeganie procedur?",
    "ID 20": "Błąd bez winy, ale wymagane jest szkolenie korygujące lub wsparcie.",
    "ID 21": "Błąd bez winy",
    "ID 71": "Czy osoba wybrała działanie, zdarzenie lub zachowanie dla własnej korzyści?",
    "ID 69": "Czy osoba uważała, że alternatywne działanie będzie korzystne dla przedsiębiorstwa?",
    "ID 74": "Czy osoba nie zdawała sobie sprawy, że nie przestrzega obowiązujących procedur?",
    "ID 75": "Czy zasada jest dobrze znana, ale lokalny zwyczaj i praktyka polegają na jej ignorowaniu?",
    "ID 76": "Korzyść osobista: „Tak było mi łatwiej.”",
    "ID 78": "Korzyść dla przedsiębiorstwa: „Uznałem(-am), że takie postępowanie będzie lepsze dla przedsiębiorstwa.”",
    "ID 97": "Naruszenie rutynowe: „Ale tutaj wszyscy tak robią.”",
    "ID 400": "Zamierzone i nieregularne naruszenie",
    "ID 105": "Oparte na wiedzy: „Nie wiedziałem(-am) / nie rozumiałem(-am) tej zasady.”",
    "ID 147": "Czy osoba uważa, że postępowała właściwie?",
    "ID 162": "Błąd: „Nie spodziewałem(-am) się, że to się wydarzy.”",
    "ID 163": "Błąd nieuwagi: „Nie zauważyłem(-am), co się wydarzyło.”",
    "ID 336": "Czy wykonanie tego zadania zgodnie z ustaloną procedurą jest bardzo trudne lub niebezpieczne?",
    "ID 337": "Naruszenie wyjątkowe: w rzeczywistości bezpieczniej jest zignorować zasadę niż jej przestrzegać.",
    "ID 345": "Naruszenie sytuacyjne: „Nie mogę wykonać zadania, jeśli przestrzegam zasad, ale mimo to je wykonałem(-am).”",
}


CONCLUSION_PL = {
    "SABOTAGE_ACTE_MALVEILLANT": "Sabotaż lub działanie w złej wierze",
    "NEGLIGENCE": "Zaniedbanie",
    "GAIN_PERSONNEL": "Korzyść osobista",
    "GAIN_ENTREPRISE": "Korzyść dla przedsiębiorstwa",
    "VIOLATION_ROUTINE": "Naruszenie rutynowe",
    "VIOLATION_INTENTIONNELLE_IRREGULIERE": "Zamierzone i nieregularne naruszenie",
    "BASE_CONNAISSANCE": "Naruszenie wynikające z braku wiedzy",
    "ERREUR": "Błąd",
    "ERREUR_INATTENTION": "Błąd nieuwagi",
    "VIOLATION_EXCEPTIONNELLE": "Naruszenie wyjątkowe",
    "VIOLATION_SITUATIONNELLE": "Naruszenie sytuacyjne",
}


RECOMMENDATION_PL = {
    "ACCOMPAGNEMENT": "Wsparcie / coaching",
    "AVERTISSEMENT_VERBAL": "Upomnienie ustne",
    "PREMIER_AVERTISSEMENT_ECRIT": "Pierwsze pisemne ostrzeżenie",
    "DERNIER_AVERTISSEMENT_ECRIT": "Ostatnie pisemne ostrzeżenie",
    "LICENCIEMENT": "Zwolnienie",
}


def main() -> None:
    db = SessionLocal()

    try:
        nodes = db.scalars(
            select(models.JustCultureNode)
        ).all()

        node_count = 0
        missing_nodes = []

        for code, text_pl in NODE_TEXT_PL.items():
            matches = [
                node
                for node in nodes
                if node.code == code
            ]

            if not matches:
                missing_nodes.append(code)
                continue

            for node in matches:
                node.text_pl = text_pl

                if node.conclusion_code:
                    node.conclusion_label_pl = (
                        CONCLUSION_PL.get(
                            node.conclusion_code
                        )
                    )

                if node.recommendation_code:
                    node.recommendation_label_pl = (
                        RECOMMENDATION_PL.get(
                            node.recommendation_code
                        )
                    )

                node_count += 1

        transitions = db.scalars(
            select(models.JustCultureTransition)
        ).all()

        transition_count = 0

        for transition in transitions:
            answer_code = (
                transition.answer_code or ""
            ).strip().upper()

            if answer_code == "YES":
                transition.answer_label_pl = "Tak"
                transition_count += 1

            elif answer_code == "NO":
                transition.answer_label_pl = "Nie"
                transition_count += 1

        db.commit()

        print(
            f"{node_count} nœud(s) Just Culture "
            "mis à jour en polonais."
        )
        print(
            f"{transition_count} transition(s) "
            "mise(s) à jour en polonais."
        )

        if missing_nodes:
            print(
                "Nœuds absents : "
                + ", ".join(missing_nodes)
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()
