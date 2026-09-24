from backend.database import SessionLocal
from backend import models


# ============================================================
# TRADUCTIONS POLONAISES HEEPO
# ============================================================

TRANSLATIONS = {
    # HOMME
    "H0": "Inne",
    "H1": "Nieużywanie środków ochrony zbiorowej (EPC) / ich wyłączanie",
    "H2": "Nieużywanie środków ochrony indywidualnej (ŚOI) / ich niewłaściwe używanie",
    "H3": "Nieprzestrzeganie instrukcji bezpieczeństwa",
    "H4": "Nieprzestrzeganie instrukcji pracy",
    "H5": "Niewłaściwe używanie narzędzia",
    "H6": "Niewłaściwa pozycja / postawa / manipulacja",
    "H7": "Niewłaściwe działanie / niewłaściwe obciążenie",
    "H8": "Pośpiech / zdenerwowanie / konflikty",
    "H9": "Rozproszenie uwagi / nieuwaga",
    "H10": "Praca pod napięciem bez upoważnienia / procedury",
    "H11": "Nieprzestrzeganie bezpiecznych odległości elektrycznych",

    # EQUIPEMENT
    "E0": "Inne",
    "E1": "Brak środków ochrony zbiorowej (EPC), ich usunięcie lub zły stan",
    "E2": "Brak środków ochrony indywidualnej (ŚOI) lub ich zły stan",
    "E3": "Narzędzie lub maszyna: w złym stanie",
    "E4": "Narzędzie lub maszyna: niezgodne z wymaganiami",
    "E5": "Narzędzie lub maszyna: niebezpieczny projekt / konstrukcja",
    "E6": "Drabina: w złym stanie",
    "E7": "Narzędzia nieizolowane / niedostosowane do napięcia",
    "E8": "Brak lub awaria alarmu dźwiękowego / świetlnego w maszynach",
    "E9": "Brak lub niesprawny system wykrywania wycieku gazu",

    # ENVIRONNEMENT
    "En0": "Inne",
    "En1": "Temperatura / wilgotność / hałas / oświetlenie / drgania",
    "En2": "Płaska podłoga: w złym stanie",
    "En3": "Schody lub podest roboczy: w złym stanie",
    "En4": "Porządek i czystość",
    "En5": "Wystające elementy / ryzyko uderzenia",
    "En6": "Ludzie lub organizmy żywe",
    "En7": "Strefa ATEX lub obecność niebezpiecznych gazów",
    "En8": "Praca w przestrzeni zamkniętej lub na dachu (narażenie na upadek / wiatr)",

    # ORGANISATION
    "O0": "Inne",
    "O1": "Niewłaściwa organizacja stanowiska pracy",
    "O2": "Brak wystarczającej przestrzeni na stanowisku pracy",
    "O3": "Brak instrukcji",
    "O4": "Brak szkoleń",
    "O5": "Nieprawidłowe informacje lub instrukcje",
    "O6": "Niewystarczająca znajomość wykonywanej pracy",
    "O7": "Niewystarczająca znajomość zagrożeń",
    "O8": "Brak narzędzi",
    "O9": "Ergonomia: nieoptymalna",
    "O10": "Brak procedury odłączania i zabezpieczania energii / przywracania zasilania",
    "O11": "Nieodpowiedni lub brak planu zapobiegania zagrożeniom",
    "O12": "Brak koordynacji z innymi branżami na budowie",

    # PRODUIT
    "P0": "Inne",
    "P1": "Niezgodna karta charakterystyki",
    "P2": "Charakter produktu (ciężki, ostry, śliski, ...)",
    "P3": "Niebezpieczne właściwości (łatwopalny, toksyczny, ...)",
    "P4": "Niezgodne / uszkodzone opakowanie",
    "P5": "Brak oznakowania / identyfikacji zagrożeń",
    "P6": "Wyciek czynnika chłodniczego (toksycznego / łatwopalnego)",
    "P7": "Gaz pod ciśnieniem",
    "P8": "Łatwopalny materiał izolacyjny / toksyczny w przypadku pożaru",
}


# ============================================================
# MISE À JOUR DU RÉFÉRENTIEL
# ============================================================

db = SessionLocal()

try:
    factors = db.query(models.HeepoFactor).all()

    updated = 0
    missing = []

    for factor in factors:
        translation = TRANSLATIONS.get(factor.code)

        if translation is None:
            missing.append(
                f"{factor.family} / {factor.code}"
            )
            continue

        factor.label_pl = translation
        updated += 1

    if missing:
        raise RuntimeError(
            "Traductions manquantes : "
            + ", ".join(missing)
        )

    if updated != len(TRANSLATIONS):
        raise RuntimeError(
            f"Incohérence : {updated} facteurs mis à jour "
            f"pour {len(TRANSLATIONS)} traductions."
        )

    db.commit()

    print(
        f"OK - {updated} facteurs HEEPO "
        "traduits en polonais."
    )

except Exception:
    db.rollback()
    raise

finally:
    db.close()