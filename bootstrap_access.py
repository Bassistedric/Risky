# ============================================================
# INITIALISATION DES ACCÈS RISKY
# ============================================================

from sqlalchemy import select

from backend.database import (
    Base,
    SessionLocal,
    engine,
)
from backend import models
# Charge les modèles modulaires dans Base.metadata.
from backend import domain_models  # noqa: F401


# ============================================================
# CONFIGURATION
# ============================================================

ADMIN_INITIALS = "Cco"

DEFAULT_ROLES = [
    ("ADMIN", "Administrateur"),
    ("SIPP", "Service interne de prévention"),
    ("QHSE", "QHSE"),
    ("MANAGER", "Ligne hiérarchique"),
    ("VIEWER", "Lecture seule"),
]


# ============================================================
# CRÉATION DES TABLES
# ============================================================

print("Création / vérification des tables...")

Base.metadata.create_all(bind=engine)

print("Tables OK.")


# ============================================================
# INITIALISATION DES RÔLES
# ============================================================

db = SessionLocal()

try:
    for code, name in DEFAULT_ROLES:
        role = db.scalar(
            select(models.AccessRole)
            .where(
                models.AccessRole.code == code
            )
        )

        if role:
            print(f"Rôle déjà présent : {code}")
            continue

        role = models.AccessRole(
            code=code,
            name=name,
            active=True,
        )

        db.add(role)

        print(f"Rôle ajouté : {code}")

    db.commit()


    # ========================================================
    # RECHERCHE DE L'ADMINISTRATEUR
    # ========================================================

    person = db.scalar(
        select(models.Person)
        .where(
            models.Person.initials == ADMIN_INITIALS,
            models.Person.status == "ACTIVE",
        )
    )

    if not person:
        raise RuntimeError(
            f"Utilisateur actif introuvable : "
            f"{ADMIN_INITIALS}"
        )

    admin_role = db.scalar(
        select(models.AccessRole)
        .where(
            models.AccessRole.code == "ADMIN"
        )
    )

    if not admin_role:
        raise RuntimeError(
            "Le rôle ADMIN n'a pas été créé."
        )


    # ========================================================
    # ACCÈS ADMINISTRATEUR GLOBAL
    # ========================================================

    existing_grant = db.scalar(
        select(models.UserAccessGrant)
        .where(
            models.UserAccessGrant.person_id == person.id,
            models.UserAccessGrant.role_id == admin_role.id,
            models.UserAccessGrant.scope_all.is_(True),
            models.UserAccessGrant.active.is_(True),
        )
    )

    if existing_grant:
        print(
            f"Accès ADMIN global déjà présent pour "
            f"{person.first_name} {person.last_name}"
        )

    else:
        grant = models.UserAccessGrant(
            person_id=person.id,
            role_id=admin_role.id,
            organization_id=None,
            scope_all=True,
            include_children=True,
            active=True,
        )

        db.add(grant)
        db.commit()

        print(
            f"Accès ADMIN global créé pour "
            f"{person.first_name} {person.last_name}"
        )


    # ========================================================
    # RÉSUMÉ
    # ========================================================

    print()
    print("Initialisation terminée.")
    print(
        f"Administrateur : "
        f"{person.first_name} {person.last_name}"
    )
    print("Périmètre : toutes les entités")

finally:
    db.close()