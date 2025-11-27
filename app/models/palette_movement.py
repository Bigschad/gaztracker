"""
Palette Movement Model

Defines the PaletteMovement model for tracking palette history.
"""

from sqlalchemy import Column, String, Enum as SQLEnum, DateTime, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class MovementAction(str, enum.Enum):
    """
    Types of actions that can be performed on palettes.

    - CREATION: Palette created
    - ASSIGNATION_BON_ENLEVEMENT: Assigned to bon d'enlèvement
    - CHARGEMENT_CENTRE: Loaded at filling center
    - DEPART_CENTRE: Departure from filling center
    - ARRIVEE_DEPOT: Arrival at depot
    - LIVRAISON_DEPOT: Delivered to depot
    - COLLECTE_VIDE: Empty collected
    - ASSIGNATION_BON_RETOUR: Assigned to bon de réception retour
    - DEPART_DEPOT: Departure from depot (return)
    - ARRIVEE_CENTRE: Arrival at filling center
    - CONTROLE_QUALITE: Quality control
    - VALIDATION_RETOUR: Return validated
    - UPDATE_LOCATION: Location updated
    - STATUS_CHANGE: Status changed
    - MISE_HORS_SERVICE: Put out of service
    """
    CREATION = "CREATION"
    ASSIGNATION_BON_ENLEVEMENT = "ASSIGNATION_BON_ENLEVEMENT"
    CHARGEMENT_CENTRE = "CHARGEMENT_CENTRE"
    DEPART_CENTRE = "DEPART_CENTRE"
    ARRIVEE_DEPOT = "ARRIVEE_DEPOT"
    LIVRAISON_DEPOT = "LIVRAISON_DEPOT"
    COLLECTE_VIDE = "COLLECTE_VIDE"
    ASSIGNATION_BON_RETOUR = "ASSIGNATION_BON_RETOUR"
    DEPART_DEPOT = "DEPART_DEPOT"
    ARRIVEE_CENTRE = "ARRIVEE_CENTRE"
    CONTROLE_QUALITE = "CONTROLE_QUALITE"
    VALIDATION_RETOUR = "VALIDATION_RETOUR"
    UPDATE_LOCATION = "UPDATE_LOCATION"
    STATUS_CHANGE = "STATUS_CHANGE"
    MISE_HORS_SERVICE = "MISE_HORS_SERVICE"


class PaletteMovement(Base):
    """
    Palette movement model for tracking palette history and audit trail.

    Attributes:
        id: Unique movement identifier (UUID)
        palette_id: Related palette
        expedition_id: Related expedition (optional)
        user_id: User who performed the action
        action: Type of action performed
        status_before: Status before action
        status_after: Status after action
        location: Location where action was performed
        latitude: GPS latitude (optional)
        longitude: GPS longitude (optional)
        timestamp: When action was performed
        details: Additional details (JSON)
        notes: Additional notes
    """

    __tablename__ = "palette_movements"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
        comment="Unique movement identifier"
    )

    # Foreign Keys
    palette_id = Column(
        UUID(as_uuid=True),
        ForeignKey("palettes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Related palette"
    )

    # Workflow Document References
    bon_enlevement_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bons_enlevement.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Related bon d'enlèvement (optional)"
    )
    
    bon_reception_retour_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bons_reception_retour.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Related bon de réception retour (optional)"
    )
    
    livraison_detail_id = Column(
        UUID(as_uuid=True),
        ForeignKey("livraisons_details.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Related livraison detail (optional)"
    )
    
    # Location References
    depot_id = Column(
        UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Related depot (optional)"
    )
    
    centre_remplisseur_id = Column(
        UUID(as_uuid=True),
        ForeignKey("centres_remplisseurs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Related filling center (optional)"
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who performed the action"
    )

    # Action Information
    action = Column(
        SQLEnum(MovementAction, name="movement_action", create_type=True),
        nullable=False,
        index=True,
        comment="Type of action performed"
    )

    status_before = Column(
        String(50),
        nullable=True,
        comment="Status before action"
    )

    status_after = Column(
        String(50),
        nullable=True,
        comment="Status after action"
    )

    # Location Information
    location = Column(
        String(500),
        nullable=True,
        comment="Location where action was performed"
    )

    latitude = Column(
        String(50),
        nullable=True,
        comment="GPS latitude"
    )

    longitude = Column(
        String(50),
        nullable=True,
        comment="GPS longitude"
    )

    # Timestamp
    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="When action was performed"
    )

    # Additional Information
    details = Column(
        JSON,
        nullable=True,
        comment="Additional details (JSON)"
    )

    notes = Column(
        String(1000),
        nullable=True,
        comment="Additional notes"
    )

    # Relationships
    palette = relationship(
        "Palette",
        back_populates="movements"
    )
    
    bon_enlevement = relationship(
        "BonEnlevement",
        foreign_keys=[bon_enlevement_id]
    )
    
    bon_reception_retour = relationship(
        "BonReceptionRetour",
        back_populates="movements",
        foreign_keys=[bon_reception_retour_id]
    )
    
    livraison_detail = relationship(
        "LivraisonDetail",
        back_populates="movements",
        foreign_keys=[livraison_detail_id]
    )
    
    depot = relationship(
        "Depot",
        foreign_keys=[depot_id]
    )
    
    centre_remplisseur = relationship(
        "CentreRemplisseur",
        foreign_keys=[centre_remplisseur_id]
    )

    user = relationship(
        "User",
        back_populates="palette_movements"
    )

    # Indexes
    __table_args__ = (
        Index("ix_movements_palette_timestamp", "palette_id", "timestamp"),
        Index("ix_movements_bon_enlevement", "bon_enlevement_id", "timestamp"),
        Index("ix_movements_bon_retour", "bon_reception_retour_id", "timestamp"),
        Index("ix_movements_livraison", "livraison_detail_id", "timestamp"),
        Index("ix_movements_action_timestamp", "action", "timestamp"),
        Index("ix_movements_depot", "depot_id", "timestamp"),
        Index("ix_movements_centre", "centre_remplisseur_id", "timestamp"),
    )

    def __repr__(self) -> str:
        """String representation of PaletteMovement."""
        return f"<PaletteMovement(id={self.id}, palette={self.palette_id}, action={self.action})>"

    @property
    def has_location(self) -> bool:
        """Check if movement has geolocation data."""
        return self.latitude is not None and self.longitude is not None
