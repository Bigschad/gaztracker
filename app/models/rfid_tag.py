"""
RFID Tag Model

Représente un tag RFID qui peut être attaché à une palette.
Les tags sont créés séparément avant d'être assignés à des palettes.
"""

from sqlalchemy import Column, String, Enum as SQLEnum, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from uuid import uuid4
import enum

from app.database import Base
from app.models.mixins import TimestampMixin


class RFIDTagStatus(str, enum.Enum):
    """Statuts possibles pour un tag RFID"""
    NOT_ASSIGNED = "NOT_ASSIGNED"      # Créé mais pas attaché à palette
    ASSIGNED = "ASSIGNED"               # Attaché à une palette
    LOST = "LOST"                       # Perdu
    DAMAGED = "DAMAGED"                 # Endommagé


class RFIDTag(Base, TimestampMixin):
    """
    Modèle pour les tags RFID.

    Un tag RFID est créé indépendamment et peut ensuite être assigné à une palette.
    Chaque tag a un numéro unique et un statut.
    """

    __tablename__ = "rfid_tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identifiant unique du tag RFID (fourni par le lecteur)
    tag_number = Column(String(50), unique=True, nullable=False, index=True)

    # Libellé du tag (nom personnalisé)
    label = Column(String(255), nullable=True, index=True)

    # Statut du tag
    status = Column(SQLEnum(RFIDTagStatus), default=RFIDTagStatus.NOT_ASSIGNED, nullable=False, index=True)

    # Qui a créé/enregistré le tag
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", foreign_keys=[created_by_id], backref="created_rfid_tags")

    # Relation avec palette (optionnelle, si assigné)
    # Note: back_populates sera défini dans le modèle Palette
    palette = relationship("Palette", uselist=False, back_populates="rfid_tag")

    # Métadonnées
    notes = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamp d'assignation à une palette
    assigned_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<RFIDTag {self.tag_number} ({self.status})>"

    def assign_to_palette(self):
        """Marquer le tag comme assigné"""
        self.status = RFIDTagStatus.ASSIGNED
        self.assigned_at = datetime.utcnow()

    def unassign_from_palette(self):
        """Libérer le tag d'une palette"""
        self.status = RFIDTagStatus.NOT_ASSIGNED
        self.assigned_at = None

    def mark_as_lost(self):
        """Marquer le tag comme perdu"""
        self.status = RFIDTagStatus.LOST

    def mark_as_damaged(self):
        """Marquer le tag comme endommagé"""
        self.status = RFIDTagStatus.DAMAGED

    @property
    def is_assignable(self) -> bool:
        """Vérifie si le tag peut être assigné à une palette"""
        return self.status == RFIDTagStatus.NOT_ASSIGNED and self.is_active
