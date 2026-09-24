# ============================================================
# IMPORTS
# ============================================================

from datetime import datetime, timedelta
from typing import Optional

import secrets

from fastapi import Header, HTTPException
from sqlalchemy import select

from ..database import SessionLocal
from .. import models


# ============================================================
# CONFIGURATION
# ============================================================

SESSION_DURATION_DAYS = 30


# ============================================================
# CRÉATION D'UNE SESSION
# ============================================================

def create_session(
    person_id: int,
    initials: str,
    display_name: str,
):
    """
    Crée une session persistante en base de données.

    Les paramètres initials et display_name sont conservés
    dans la signature pour rester compatibles avec le routeur
    existant. L'identité de référence reste Person.
    """

    session_token = secrets.token_urlsafe(32)

    now = datetime.now()

    db = SessionLocal()

    try:
        user_session = models.UserSession(
            token=session_token,
            person_id=person_id,
            created_at=now,
            last_seen_at=now,
            expires_at=(
                now
                + timedelta(
                    days=SESSION_DURATION_DAYS,
                )
            ),
            revoked=False,
        )

        db.add(user_session)
        db.commit()

        return session_token

    finally:
        db.close()


# ============================================================
# RÉCUPÉRATION DES DROITS UTILISATEUR
# ============================================================

def _get_user_access(
    db,
    person_id: int,
):
    grants = db.scalars(
        select(models.UserAccessGrant)
        .where(
            models.UserAccessGrant.person_id
            == person_id,
            models.UserAccessGrant.active.is_(
                True
            ),
        )
    ).all()

    roles = []

    scopes = []

    scope_all = False

    for grant in grants:
        role = grant.role

        if (
            role
            and role.active
            and role.code not in roles
        ):
            roles.append(role.code)

        if grant.scope_all:
            scope_all = True

        if grant.organization_id is not None:
            scopes.append(
                {
                    "organization_id":
                        grant.organization_id,
                    "include_children":
                        grant.include_children,
                    "role":
                        (
                            role.code
                            if role
                            else None
                        ),
                }
            )

    # Pour conserver la compatibilité actuelle :
    # VIEWER seul = lecture seule.
    # Tous les autres rôles actifs = écriture.
    writable_roles = {
        "ADMIN",
        "SIPP",
        "QHSE",
        "MANAGER",
    }

    mode = (
        "WRITE"
        if any(
            role in writable_roles
            for role in roles
        )
        else "READ"
    )

    return {
        "roles": roles,
        "scope_all": scope_all,
        "scopes": scopes,
        "mode": mode,
    }


# ============================================================
# LECTURE D'UNE SESSION
# ============================================================

def get_session_from_token(
    session_token: Optional[str],
):
    if not session_token:
        return None

    db = SessionLocal()

    try:
        user_session = db.scalar(
            select(models.UserSession)
            .where(
                models.UserSession.token
                == session_token
            )
        )

        if not user_session:
            return None

        if user_session.revoked:
            return None

        now = datetime.now()

        if (
            user_session.expires_at
            and user_session.expires_at < now
        ):
            return None

        person = db.get(
            models.Person,
            user_session.person_id,
        )

        if not person:
            return None

        if person.status != "ACTIVE":
            return None

        access = _get_user_access(
            db,
            person.id,
        )

        user_session.last_seen_at = now

        db.commit()

        display_name = (
            f"{person.first_name} "
            f"{person.last_name}"
        )

        return {
            "session_id": user_session.id,
            "person_id": person.id,
            "initials": person.initials,
            "display_name": display_name,
            "mode": access["mode"],
            "roles": access["roles"],
            "scope_all":
                access["scope_all"],
            "scopes": access["scopes"],
            "started_at":
                user_session.created_at,
            "expires_at":
                user_session.expires_at,
        }

    finally:
        db.close()


# ============================================================
# SESSION D'ÉCRITURE OBLIGATOIRE
# ============================================================

def require_write_session(
    x_session_token: str | None = Header(
        default=None,
        alias="X-Session-Token",
    ),
):
    """
    Autorise une opération d'écriture uniquement
    avec une session persistante valide.
    """

    session = get_session_from_token(
        x_session_token
    )

    if not session:
        raise HTTPException(
            status_code=401,
            detail=(
                "Identification requise "
                "pour modifier les données"
            ),
        )

    if session.get("mode") != "WRITE":
        raise HTTPException(
            status_code=403,
            detail="Session en lecture seule",
        )

    return session