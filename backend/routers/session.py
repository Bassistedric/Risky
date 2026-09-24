from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import select

from ..database import SessionLocal
from .. import models

from ..schemas.session import UserLoginRequest
from ..services.session import (
    create_session,
    get_session_from_token,
)


router = APIRouter(
    prefix="/session",
    tags=["Session"],
)


@router.post("/login")
def login_user(payload: UserLoginRequest):
    initials = payload.initials.strip()

    if not initials:
        return {
            "status": "error",
            "message": "Les initiales sont obligatoires",
        }

    db = SessionLocal()

    try:
        person = db.scalar(
            select(models.Person)
            .where(
                models.Person.initials == initials,
                models.Person.status == "ACTIVE",
            )
        )

        if not person:
            return {
                "status": "error",
                "message": "Initiales inconnues ou utilisateur inactif",
            }

        display_name = (
            f"{person.first_name} {person.last_name}"
        )

        session_token = create_session(
            person_id=person.id,
            initials=person.initials,
            display_name=display_name,
        )
        session = get_session_from_token(
            session_token
        )

        return {
            "status": "authenticated",
            "session_token":
                session_token,
            "mode":
                session["mode"],
            "user": {
                "person_id":
                    person.id,
                "initials":
                    person.initials,
                "display_name":
                    display_name,
            },
            "access": {
                "roles":
                    session["roles"],
                "scope_all":
                    session["scope_all"],
                "scopes":
                    session["scopes"],
            },
        }

    finally:
        db.close()


@router.get("/me")
def get_current_session(
    x_session_token: Optional[str] = Header(default=None),
):
    session = get_session_from_token(
        x_session_token
    )

    if not session:
        return {
            "status": "error",
            "message": "Session inconnue ou expirée",
        }

    return {
        "status": "authenticated",
        "mode": session["mode"],
        "user": {
            "person_id":
                session["person_id"],
            "initials":
                session["initials"],
            "display_name":
                session["display_name"],
        },
        "access": {
            "roles":
                session["roles"],
            "scope_all":
                session["scope_all"],
            "scopes":
                session["scopes"],
        },
        "started_at":
            session["started_at"],
        "expires_at":
            session["expires_at"],
        }
# ============================================================
# DÉCONNEXION
# ============================================================

@router.post("/logout")
def logout_user(
    x_session_token: Optional[str] = Header(
        default=None,
        alias="X-Session-Token",
    ),
):
    if not x_session_token:
        raise HTTPException(
            status_code=401,
            detail="Aucune session active",
        )

    db = SessionLocal()

    try:
        user_session = db.scalar(
            select(models.UserSession)
            .where(
                models.UserSession.token
                == x_session_token
            )
        )

        if not user_session:
            raise HTTPException(
                status_code=401,
                detail="Session inconnue",
            )

        user_session.revoked = True

        db.commit()

        return {
            "status": "disconnected",
        }

    finally:
        db.close()