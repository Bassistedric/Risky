from pathlib import Path

ROOT = Path("src")

REPLACEMENTS = {
    "Ã©": "é",
    "Ã¨": "è",
    "Ãª": "ê",
    "Ã«": "ë",
    "Ã ": "à",
    "Ã ": "à",
    "Ã¢": "â",
    "Ã®": "î",
    "Ã¯": "ï",
    "Ã´": "ô",
    "Ã¶": "ö",
    "Ã¹": "ù",
    "Ã»": "û",
    "Ã¼": "ü",
    "Ã§": "ç",
    "Ã‰": "É",
    "Ã€": "À",
    "Ã‡": "Ç",

    "â€™": "’",
    "â€œ": "“",
    "â€": "”",
    "â€¦": "…",
    "â€“": "–",
    "â€”": "—",

    "â†": "←",
    "â†’": "→",
    "âŒ„": "⌄",
    "âŒƒ": "⌃",
    "â€º": "›",

    "Â°": "°",
    "Â·": "·",
    "Â ": " ",
    "ÃŠ": "Ê",
    "â—‡": "◇",

}

extensions = {
    ".tsx",
    ".ts",
    ".css",
    ".json",
}

changed_files = []

for path in ROOT.rglob("*"):
    if (
        not path.is_file()
        or path.suffix.lower() not in extensions
    ):
        continue

    content = path.read_text(
        encoding="utf-8",
    )

    original = content

    for bad, good in REPLACEMENTS.items():
        content = content.replace(
            bad,
            good,
        )

    if content != original:
        path.write_text(
            content,
            encoding="utf-8",
        )

        changed_files.append(path)

print()
print("Fichiers corrigés :")

for path in changed_files:
    print(f" - {path}")

print()
print(
    f"Terminé : {len(changed_files)} "
    "fichier(s) modifié(s)."
)