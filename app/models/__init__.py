"""
Models Package

This package contains all SQLAlchemy models for the GazTracker application.
"""

from app.models.user import User, UserRole
from app.models.palette import Palette, PaletteType, PaletteStatus, livraison_palettes
from app.models.rfid_tag import RFIDTag, RFIDTagStatus
from app.models.expedition import Expedition, ExpeditionStatus
from app.models.palette_movement import PaletteMovement, MovementAction
from app.models.notification import Notification, NotificationType, NotificationStatus, NotificationChannel
from app.models.audit import AuditLog
from app.models.partner import Partner, PartnerType
from app.models.contact import Contact

# New models for restructured workflow
from app.models.groupe import Groupe
from app.models.grand_distributeur import GrandDistributeur
from app.models.centre_remplisseur import CentreRemplisseur
from app.models.depot import Depot
from app.models.bon_enlevement import BonEnlevement, BonEnlevementStatus
from app.models.livraison_detail import LivraisonDetail, LivraisonStatus
from app.models.collecte_vide import CollecteVide
from app.models.bon_reception_retour import BonReceptionRetour, BonReceptionRetourStatus
from app.models.detail_retour import DetailRetour, DetailRetourType, DetailRetourEtat


__all__ = [
    # Core Models
    "User",
    "Palette",
    "RFIDTag",
    "Expedition",  # To be deprecated
    "PaletteMovement",
    "Notification",
    "AuditLog",
    "Partner",
    "Contact",
    
    # New Hierarchy Models
    "Groupe",
    "GrandDistributeur",
    "CentreRemplisseur",
    "Depot",
    
    # New Workflow Models
    "BonEnlevement",
    "LivraisonDetail",
    "CollecteVide",
    "BonReceptionRetour",
    "DetailRetour",
    
    # Association Tables
    "livraison_palettes",

    # Core Enums
    "UserRole",
    "PaletteType",
    "PaletteStatus",
    "RFIDTagStatus",
    "ExpeditionStatus",  # To be deprecated
    "MovementAction",
    "NotificationType",
    "NotificationStatus",
    "NotificationChannel",
    "PartnerType",
    
    # New Workflow Enums
    "BonEnlevementStatus",
    "LivraisonStatus",
    "BonReceptionRetourStatus",
    "DetailRetourType",
    "DetailRetourEtat",
]
