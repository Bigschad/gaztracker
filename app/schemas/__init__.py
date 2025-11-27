"""
Schemas Package

This package contains all Pydantic schemas for request/response validation.
"""

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    LoginRequest,
    LoginResponse,
    PasswordChange,
)

from app.schemas.rfid_tag import (
    RFIDTagCreate,
    RFIDTagUpdate,
    RFIDTagResponse,
    RFIDTagDetailResponse,
    RFIDTagListResponse,
    RFIDTagStatistics,
)

from app.schemas.palette import (
    PaletteCreate,
    PaletteUpdate,
    PaletteResponse,
    PaletteListResponse,
    PaletteScanRequest,
    PaletteScanResponse,
    PaletteStatistics,
)

from app.schemas.expedition import (
    ExpeditionCreate,
    ExpeditionUpdate,
    ExpeditionResponse,
    ExpeditionListResponse,
    ExpeditionDepartRequest,
    ExpeditionValidateRequest,
    ExpeditionStatistics,
)

from app.schemas.notification import (
    NotificationCreate,
    NotificationSendEmail,
    NotificationSendSMS,
    NotificationRetry,
    NotificationResponse,
    NotificationListResponse,
    NotificationStatistics,
)

# New hierarchy schemas
from app.schemas.groupe import (
    GroupeCreate,
    GroupeUpdate,
    GroupeRead,
    GroupeList,
    GroupeDetail,
)

from app.schemas.grand_distributeur import (
    GrandDistributeurCreate,
    GrandDistributeurUpdate,
    GrandDistributeurRead,
    GrandDistributeurList,
    GrandDistributeurDetail,
)

from app.schemas.centre_remplisseur import (
    CentreRemplisseurCreate,
    CentreRemplisseurUpdate,
    CentreRemplisseurRead,
    CentreRemplisseurList,
    CentreRemplisseurDetail,
)

from app.schemas.depot import (
    DepotCreate,
    DepotUpdate,
    DepotRead,
    DepotList,
    DepotDetail,
    DepotLocation,
)

# New workflow schemas
from app.schemas.bon_enlevement import (
    BonEnlevementCreate,
    BonEnlevementUpdate,
    BonEnlevementRead,
    BonEnlevementList,
    BonEnlevementDetail,
    BonEnlevementStatusUpdate,
    BonEnlevementValidation,
    BonEnlevementChargement,
    BonEnlevementDepart,
    BonEnlevementReception,
)

from app.schemas.livraison_detail import (
    LivraisonDetailCreate,
    LivraisonDetailUpdate,
    LivraisonDetailRead,
    LivraisonDetailList,
    LivraisonDetailDetail,
    LivraisonDetailStatusUpdate,
    LivraisonDetailArrivee,
    LivraisonDetailCompletion,
    LivraisonDetailProbleme,
)

from app.schemas.collecte_vide import (
    CollecteVideCreate,
    CollecteVideUpdate,
    CollecteVideRead,
    CollecteVideList,
    CollecteVideDetail,
    CollecteVideBulk,
)

from app.schemas.bon_reception_retour import (
    BonReceptionRetourCreate,
    BonReceptionRetourUpdate,
    BonReceptionRetourRead,
    BonReceptionRetourList,
    BonReceptionRetourDetail,
    BonReceptionRetourStatusUpdate,
    BonReceptionRetourDepart,
    BonReceptionRetourArrivee,
    BonReceptionRetourControle,
    BonReceptionRetourValidation,
    BonReceptionRetourRefus,
)

from app.schemas.detail_retour import (
    DetailRetourCreate,
    DetailRetourUpdate,
    DetailRetourRead,
    DetailRetourList,
    DetailRetourDetail,
    DetailRetourControle,
    DetailRetourBulkCreate,
)


__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    "LoginRequest",
    "LoginResponse",
    "PasswordChange",

    # RFID Tag schemas
    "RFIDTagCreate",
    "RFIDTagUpdate",
    "RFIDTagResponse",
    "RFIDTagDetailResponse",
    "RFIDTagListResponse",
    "RFIDTagStatistics",

    # Palette schemas
    "PaletteCreate",
    "PaletteUpdate",
    "PaletteResponse",
    "PaletteListResponse",
    "PaletteScanRequest",
    "PaletteScanResponse",
    "PaletteStatistics",

    # Expedition schemas
    "ExpeditionCreate",
    "ExpeditionUpdate",
    "ExpeditionResponse",
    "ExpeditionListResponse",
    "ExpeditionDepartRequest",
    "ExpeditionValidateRequest",
    "ExpeditionStatistics",

    # Notification schemas
    "NotificationCreate",
    "NotificationSendEmail",
    "NotificationSendSMS",
    "NotificationRetry",
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationStatistics",
    
    # Groupe schemas
    "GroupeCreate",
    "GroupeUpdate",
    "GroupeRead",
    "GroupeList",
    "GroupeDetail",
    
    # GrandDistributeur schemas
    "GrandDistributeurCreate",
    "GrandDistributeurUpdate",
    "GrandDistributeurRead",
    "GrandDistributeurList",
    "GrandDistributeurDetail",
    
    # CentreRemplisseur schemas
    "CentreRemplisseurCreate",
    "CentreRemplisseurUpdate",
    "CentreRemplisseurRead",
    "CentreRemplisseurList",
    "CentreRemplisseurDetail",
    
    # Depot schemas
    "DepotCreate",
    "DepotUpdate",
    "DepotRead",
    "DepotList",
    "DepotDetail",
    "DepotLocation",
    
    # BonEnlevement schemas
    "BonEnlevementCreate",
    "BonEnlevementUpdate",
    "BonEnlevementRead",
    "BonEnlevementList",
    "BonEnlevementDetail",
    "BonEnlevementStatusUpdate",
    "BonEnlevementValidation",
    "BonEnlevementChargement",
    "BonEnlevementDepart",
    "BonEnlevementReception",
    
    # LivraisonDetail schemas
    "LivraisonDetailCreate",
    "LivraisonDetailUpdate",
    "LivraisonDetailRead",
    "LivraisonDetailList",
    "LivraisonDetailDetail",
    "LivraisonDetailStatusUpdate",
    "LivraisonDetailArrivee",
    "LivraisonDetailCompletion",
    "LivraisonDetailProbleme",
    
    # CollecteVide schemas
    "CollecteVideCreate",
    "CollecteVideUpdate",
    "CollecteVideRead",
    "CollecteVideList",
    "CollecteVideDetail",
    "CollecteVideBulk",
    
    # BonReceptionRetour schemas
    "BonReceptionRetourCreate",
    "BonReceptionRetourUpdate",
    "BonReceptionRetourRead",
    "BonReceptionRetourList",
    "BonReceptionRetourDetail",
    "BonReceptionRetourStatusUpdate",
    "BonReceptionRetourDepart",
    "BonReceptionRetourArrivee",
    "BonReceptionRetourControle",
    "BonReceptionRetourValidation",
    "BonReceptionRetourRefus",
    
    # DetailRetour schemas
    "DetailRetourCreate",
    "DetailRetourUpdate",
    "DetailRetourRead",
    "DetailRetourList",
    "DetailRetourDetail",
    "DetailRetourControle",
    "DetailRetourBulkCreate",
]
