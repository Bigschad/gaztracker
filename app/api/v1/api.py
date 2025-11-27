"""
API v1 Router

Registers all API endpoints for version 1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    groupes,
    centres_remplisseurs,
    depots,
    bons_enlevement,
    bons_reception_retour,
    uploads,
    theme
)


api_router = APIRouter()

# Hierarchy endpoints
api_router.include_router(
    groupes.router,
    prefix="/groupes",
    tags=["Groupes"]
)

api_router.include_router(
    centres_remplisseurs.router,
    prefix="/centres-remplisseurs",
    tags=["Centres Remplisseurs"]
)

api_router.include_router(
    depots.router,
    prefix="/depots",
    tags=["Dépôts"]
)

# Workflow endpoints
api_router.include_router(
    bons_enlevement.router,
    prefix="/bons-enlevement",
    tags=["Bons d'Enlèvement"]
)

api_router.include_router(
    bons_reception_retour.router,
    prefix="/bons-reception-retour",
    tags=["Bons de Réception Retour"]
)

# Uploads endpoints
api_router.include_router(
    uploads.router,
    prefix="/uploads",
    tags=["Uploads"]
)

# Theme endpoints
api_router.include_router(
    theme.router,
    prefix="/theme",
    tags=["Theme"]
)

