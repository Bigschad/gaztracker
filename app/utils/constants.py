"""
Application Constants

This module contains all constants used throughout the application.
"""

from typing import List
from app.models.user import UserRole
from app.models.palette import PaletteType, PaletteStatus
from app.models.expedition import ExpeditionStatus
from app.models.palette_movement import MovementAction
from app.models.notification import NotificationType, NotificationStatus, NotificationChannel


# =============================================================================
# User & Auth Constants
# =============================================================================

USER_ROLES: List[str] = [role.value for role in UserRole]

# Role hierarchy (higher number = more permissions)
ROLE_HIERARCHY = {
    UserRole.ADMIN: 100,
    UserRole.RESPONSABLE_LOGISTIQUE: 80,
    UserRole.OPERATEUR_USINE: 60,
    UserRole.CHAUFFEUR: 40,
}

# Password requirements
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

# Token expiration defaults (in minutes)
DEFAULT_ACCESS_TOKEN_EXPIRE = 30
DEFAULT_REFRESH_TOKEN_EXPIRE = 10080  # 7 days


# =============================================================================
# Palette Constants
# =============================================================================

PALETTE_TYPES: List[str] = [ptype.value for ptype in PaletteType]
PALETTE_STATUSES: List[str] = [status.value for status in PaletteStatus]

# RFID Tag Configuration
RFID_PREFIX = "GAZ"
RFID_LENGTH = 12

# Palette status workflow transitions (allowed transitions)
PALETTE_STATUS_TRANSITIONS = {
    PaletteStatus.CREATION: [PaletteStatus.AU_CENTRE, PaletteStatus.OUT],
    PaletteStatus.AU_CENTRE: [PaletteStatus.EN_CHARGEMENT, PaletteStatus.OUT],
    PaletteStatus.EN_CHARGEMENT: [PaletteStatus.EN_ROUTE_LIVRAISON, PaletteStatus.AU_CENTRE],
    PaletteStatus.EN_ROUTE_LIVRAISON: [PaletteStatus.AU_DEPOT, PaletteStatus.OUT],
    PaletteStatus.AU_DEPOT: [PaletteStatus.EN_ROUTE_RETOUR, PaletteStatus.OUT],
    PaletteStatus.EN_ROUTE_RETOUR: [PaletteStatus.EN_CONTROLE, PaletteStatus.AU_DEPOT],
    PaletteStatus.EN_CONTROLE: [PaletteStatus.VALIDEE, PaletteStatus.AU_DEPOT],
    PaletteStatus.VALIDEE: [PaletteStatus.AU_CENTRE, PaletteStatus.OUT],
    PaletteStatus.OUT: [],  # Terminal state
}


# =============================================================================
# Expedition Constants
# =============================================================================

EXPEDITION_STATUSES: List[str] = [status.value for status in ExpeditionStatus]

# Expedition status workflow transitions
EXPEDITION_STATUS_TRANSITIONS = {
    ExpeditionStatus.CREATION: [ExpeditionStatus.EN_ATTENTE, ExpeditionStatus.ANNULEE],
    ExpeditionStatus.EN_ATTENTE: [ExpeditionStatus.CREEE, ExpeditionStatus.ANNULEE],
    ExpeditionStatus.CREEE: [ExpeditionStatus.EN_TRANSIT, ExpeditionStatus.ANNULEE],
    ExpeditionStatus.EN_TRANSIT: [ExpeditionStatus.ARRIVEE, ExpeditionStatus.PROBLEME],
    ExpeditionStatus.ARRIVEE: [ExpeditionStatus.LIVREE, ExpeditionStatus.PROBLEME],
    ExpeditionStatus.LIVREE: [],  # Terminal state
    ExpeditionStatus.PROBLEME: [ExpeditionStatus.EN_TRANSIT, ExpeditionStatus.ANNULEE],
    ExpeditionStatus.ANNULEE: [],  # Terminal state
}

# Reference number format
EXPEDITION_REF_PREFIX = "EXP"
EXPEDITION_REF_LENGTH = 15

# OTP Configuration
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 15

# Delay alert threshold (hours)
DELIVERY_DELAY_THRESHOLD = 48


# =============================================================================
# Movement Constants
# =============================================================================

MOVEMENT_ACTIONS: List[str] = [action.value for action in MovementAction]


# =============================================================================
# Notification Constants
# =============================================================================

NOTIFICATION_TYPES: List[str] = [ntype.value for ntype in NotificationType]
NOTIFICATION_STATUSES: List[str] = [status.value for status in NotificationStatus]
NOTIFICATION_CHANNELS: List[str] = [channel.value for channel in NotificationChannel]

# Notification retry configuration
MAX_NOTIFICATION_RETRIES = 3
NOTIFICATION_RETRY_DELAY = 60  # seconds


# =============================================================================
# API Constants
# =============================================================================

# Pagination
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Rate limiting
DEFAULT_RATE_LIMIT = 60  # requests per minute


# =============================================================================
# Geolocation Constants
# =============================================================================

# Maximum distance for location validation (km)
MAX_GEOLOCATION_DISTANCE = 5.0

# Default coordinates (factory location - to be configured)
DEFAULT_FACTORY_LATITUDE = 0.0
DEFAULT_FACTORY_LONGITUDE = 0.0


# =============================================================================
# File Upload Constants
# =============================================================================

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif"]
ALLOWED_DOCUMENT_EXTENSIONS = [".pdf", ".doc", ".docx"]
ALLOWED_UPLOAD_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS + ALLOWED_DOCUMENT_EXTENSIONS


# =============================================================================
# Email Templates
# =============================================================================

EMAIL_TEMPLATES = {
    "welcome": "Welcome to GazTracker",
    "expedition_created": "New Expedition Created",
    "expedition_departed": "Expedition Departed",
    "expedition_arrived": "Expedition Arrived",
    "expedition_delivered": "Expedition Delivered",
    "delay_alert": "Delivery Delay Alert",
    "problem_alert": "Expedition Problem Alert",
}


# =============================================================================
# HTTP Status Codes
# =============================================================================

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_500_INTERNAL_SERVER_ERROR = 500


# =============================================================================
# Error Messages
# =============================================================================

ERROR_MESSAGES = {
    # Authentication
    "INVALID_CREDENTIALS": "Email ou mot de passe incorrect",
    "INACTIVE_USER": "Compte utilisateur inactif",
    "EMAIL_ALREADY_EXISTS": "Cette adresse email est déjà utilisée",
    "INVALID_TOKEN": "Token invalide ou expiré",
    "INSUFFICIENT_PERMISSIONS": "Permissions insuffisantes",

    # Palette
    "PALETTE_NOT_FOUND": "Palette introuvable",
    "RFID_ALREADY_EXISTS": "Cette étiquette RFID est déjà utilisée",
    "INVALID_PALETTE_STATUS": "Statut de palette invalide",
    "PALETTE_NOT_AVAILABLE": "Palette non disponible",

    # Expedition
    "EXPEDITION_NOT_FOUND": "Expédition introuvable",
    "INVALID_EXPEDITION_STATUS": "Statut d'expédition invalide",
    "EXPEDITION_ALREADY_DEPARTED": "L'expédition est déjà partie",
    "INVALID_OTP": "Code OTP invalide ou expiré",
    "NO_PALETTES_IN_EXPEDITION": "Aucune palette dans l'expédition",

    # General
    "RESOURCE_NOT_FOUND": "Ressource introuvable",
    "VALIDATION_ERROR": "Erreur de validation",
    "DATABASE_ERROR": "Erreur de base de données",
    "INTERNAL_ERROR": "Erreur interne du serveur",
}


# =============================================================================
# Success Messages
# =============================================================================

SUCCESS_MESSAGES = {
    # Authentication
    "LOGIN_SUCCESS": "Connexion réussie",
    "LOGOUT_SUCCESS": "Déconnexion réussie",
    "USER_CREATED": "Utilisateur créé avec succès",
    "USER_UPDATED": "Utilisateur mis à jour avec succès",
    "USER_DELETED": "Utilisateur supprimé avec succès",

    # Palette
    "PALETTE_CREATED": "Palette créée avec succès",
    "PALETTE_UPDATED": "Palette mise à jour avec succès",
    "PALETTE_DELETED": "Palette supprimée avec succès",
    "PALETTE_SCANNED": "Palette scannée avec succès",

    # Expedition
    "EXPEDITION_CREATED": "Expédition créée avec succès",
    "EXPEDITION_UPDATED": "Expédition mise à jour avec succès",
    "EXPEDITION_DELETED": "Expédition supprimée avec succès",
    "EXPEDITION_VALIDATED": "Expédition validée avec succès",
    "DELIVERY_CONFIRMED": "Livraison confirmée avec succès",

    # Notification
    "NOTIFICATION_SENT": "Notification envoyée avec succès",
}


# =============================================================================
# Audit Actions
# =============================================================================

AUDIT_ACTIONS = {
    "CREATE": "CREATE",
    "READ": "READ",
    "UPDATE": "UPDATE",
    "DELETE": "DELETE",
    "LOGIN": "LOGIN",
    "LOGOUT": "LOGOUT",
    "SCAN": "SCAN",
    "VALIDATE": "VALIDATE",
    "ASSIGN": "ASSIGN",
}


# =============================================================================
# Cache Keys & TTL
# =============================================================================

CACHE_TTL = {
    "USER": 3600,  # 1 hour
    "PALETTE": 1800,  # 30 minutes
    "EXPEDITION": 1800,  # 30 minutes
    "OTP": 900,  # 15 minutes
}

CACHE_KEY_PREFIXES = {
    "USER": "user:",
    "PALETTE": "palette:",
    "EXPEDITION": "expedition:",
    "OTP": "otp:",
    "SESSION": "session:",
    "RATE_LIMIT": "rate_limit:",
}
