# ============================================================
# RISKY — TRADUCTIONS DES RÉFÉRENTIELS DE CLASSIFICATION
# FR = label historique
# NL = label_nl
# EN = label_en
# PL = label_pl
# ============================================================

import json
from pathlib import Path

from sqlalchemy import select

from backend.database import SessionLocal
from backend.models import EventCodeReference


TRANSLATIONS_FILE = (
    Path(__file__).resolve().parents[2]
    / "imports"
    / "event_code_reference_translations.json"
)


def main() -> None:
    if not TRANSLATIONS_FILE.exists():
        raise FileNotFoundError(
            f"Fichier de traductions introuvable : "
            f"{TRANSLATIONS_FILE}"
        )

    with TRANSLATIONS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    db = SessionLocal()

    updated = 0
    missing = []

    try:
        for category, items in data.items():
            for item in items:
                code = item["code"]

                reference = db.scalar(
                    select(EventCodeReference)
                    .where(
                        EventCodeReference.category
                        == category,
                        EventCodeReference.code
                        == code,
                    )
                )

                if reference is None:
                    missing.append(
                        f"{category} / {code}"
                    )
                    continue

                reference.label_nl = (
                    item.get("label_nl")
                )
                reference.label_en = (
                    item.get("label_en")
                )
                reference.label_pl = (
                    item.get("label_pl")
                )

                updated += 1

        db.commit()

        print(
            f"{updated} référence(s) mise(s) à jour."
        )

        if missing:
            print()
            print(
                "Références absentes de la base :"
            )

            for item in missing:
                print(f"- {item}")

    finally:
        db.close()


if __name__ == "__main__":
    main()