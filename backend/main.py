from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import (
    personnel,
    competencies,
    authorizations,
    session,
    safety_statistics,
)

from .routers.accident import (
    events,
    event_facts,
    event_classification,
    event_heepo,
    event_serious_accident,
    event_references,
    event_photos,
    event_actions,
    event_reports,
    just_culture,
    cause_tree,
)

from .routers.actions import actions

app = FastAPI(
    title="RISKY API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session.router)

# ========================================================
# ROUTES ACTIONS TRANSVERSES
# ========================================================

app.include_router(actions.router)

# ========================================================
# ROUTES ACCIDENT — ROUTES SPÉCIFIQUES AVANT /{event_id}
# ========================================================

app.include_router(event_heepo.router)
app.include_router(event_references.router)
app.include_router(event_classification.router)
app.include_router(event_facts.router)
app.include_router(event_serious_accident.router)
app.include_router(just_culture.router)
app.include_router(cause_tree.router)
app.include_router(event_photos.router)
app.include_router(event_actions.router)
app.include_router(event_reports.router)

# Routes génériques événement en dernier
app.include_router(events.router)

# ========================================================
# ROUTES STATISTIQUES SÉCURITÉ
# ========================================================

app.include_router(safety_statistics.router)

app.include_router(personnel.router)
app.include_router(competencies.router)
app.include_router(authorizations.router)


@app.get("/")
def root():
    return {
        "app": "RISKY",
        "status": "ok",
        "version": "0.1.0",
    }
