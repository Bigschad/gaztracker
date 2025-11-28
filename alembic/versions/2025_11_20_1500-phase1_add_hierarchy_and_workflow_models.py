"""Phase 1: Add new hierarchy models and workflow documents

Revision ID: phase1_hierarchy
Revises: e5f6a7b8c9d0
Create Date: 2025-11-20 15:00:00.000000

This migration adds:
- New hierarchy models: Groupe, GrandDistributeur, CentreRemplisseur, Depot
- New workflow models: BonEnlevement, LivraisonDetail, CollecteVide, BonReceptionRetour, DetailRetour
- Updates to Partner model (REVENDEUR type, new fields)
- Updates to Palette model (new status values, location tracking)
- Updates to PaletteMovement model (new actions, new FK references)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'phase1_hierarchy'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Create new ENUM types ###
    conn = op.get_bind()
    
    # Helper function to create ENUM if it doesn't exist
    def create_enum_if_not_exists(enum_name: str, enum_values: list):
        result = conn.execute(sa.text(
            "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = :name)"
        ), {"name": enum_name})
        exists = result.scalar()
        if not exists:
            enum = postgresql.ENUM(*enum_values, name=enum_name)
            enum.create(conn)
    
    # BonEnlevementStatus
    create_enum_if_not_exists('bon_enlevement_status', 
        ['CREATION', 'VALIDE', 'EN_CHARGEMENT', 'EN_ROUTE', 'EN_LIVRAISON', 'TERMINE', 'ANNULE'])
    
    # LivraisonStatus
    create_enum_if_not_exists('livraison_status',
        ['EN_ATTENTE', 'EN_COURS', 'LIVREE', 'PROBLEME', 'ANNULEE'])
    
    # BonReceptionRetourStatus
    create_enum_if_not_exists('bon_reception_retour_status',
        ['CREATION', 'EN_ROUTE', 'ARRIVE', 'EN_CONTROLE', 'VALIDE', 'REFUSE'])
    
    # DetailRetourType
    create_enum_if_not_exists('detail_retour_type',
        ['PALETTE_VIDE', 'BOUTEILLE_VIDE', 'CONSIGNE'])
    
    # DetailRetourEtat
    create_enum_if_not_exists('detail_retour_etat',
        ['BON', 'MOYEN', 'MAUVAIS', 'REFUSE'])
    
    
    # ### Create new hierarchy tables ###
    
    # Create groupes table
    op.create_table(
        'groupes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Unique identifier for the group'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Name of the group'),
        sa.Column('code', sa.String(length=50), nullable=False, comment='Unique code for the group'),
        sa.Column('address', sa.String(length=500), nullable=True, comment='Physical address of the group'),
        sa.Column('city', sa.String(length=100), nullable=True, comment='City where the group is located'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='Phone number of the group'),
        sa.Column('email', sa.String(length=255), nullable=True, comment='Email address of the group'),
        sa.Column('is_active', sa.Boolean(), nullable=False, comment='Whether the group is active'),
        sa.Column('notes', sa.String(length=1000), nullable=True, comment='Additional notes about the group'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_groupes_id'), 'groupes', ['id'], unique=False)
    op.create_index(op.f('ix_groupes_name'), 'groupes', ['name'], unique=False)
    op.create_index(op.f('ix_groupes_code'), 'groupes', ['code'], unique=False)
    
    # Create grand_distributeurs table
    op.create_table(
        'grand_distributeurs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Unique identifier for the grand distributor'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Name of the grand distributor'),
        sa.Column('code', sa.String(length=50), nullable=False, comment='Unique code for the grand distributor'),
        sa.Column('groupe_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Foreign key to the Groupe model'),
        sa.Column('address', sa.String(length=500), nullable=True, comment='Physical address of the grand distributor'),
        sa.Column('city', sa.String(length=100), nullable=True, comment='City where the grand distributor is located'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='Phone number of the grand distributor'),
        sa.Column('email', sa.String(length=255), nullable=True, comment='Email address of the grand distributor'),
        sa.Column('is_active', sa.Boolean(), nullable=False, comment='Whether the grand distributor is active'),
        sa.Column('notes', sa.String(length=1000), nullable=True, comment='Additional notes about the grand distributor'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['groupe_id'], ['groupes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_grand_distributeurs_id'), 'grand_distributeurs', ['id'], unique=False)
    op.create_index(op.f('ix_grand_distributeurs_name'), 'grand_distributeurs', ['name'], unique=False)
    op.create_index(op.f('ix_grand_distributeurs_code'), 'grand_distributeurs', ['code'], unique=False)
    op.create_index(op.f('ix_grand_distributeurs_groupe_id'), 'grand_distributeurs', ['groupe_id'], unique=False)
    
    # Create centres_remplisseurs table
    op.create_table(
        'centres_remplisseurs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Unique identifier for the filling center'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Name of the filling center'),
        sa.Column('code', sa.String(length=50), nullable=False, comment='Unique code for the filling center'),
        sa.Column('grand_distributeur_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Foreign key to the GrandDistributeur model'),
        sa.Column('address', sa.String(length=500), nullable=True, comment='Physical address of the filling center'),
        sa.Column('city', sa.String(length=100), nullable=True, comment='City where the filling center is located'),
        sa.Column('postal_code', sa.String(length=20), nullable=True, comment='Postal code of the filling center'),
        sa.Column('country', sa.String(length=100), nullable=True, comment='Country of the filling center'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='Phone number of the filling center'),
        sa.Column('email', sa.String(length=255), nullable=True, comment='Email address of the filling center'),
        sa.Column('contact_name', sa.String(length=255), nullable=True, comment='Name of the contact person at the filling center'),
        sa.Column('contact_phone', sa.String(length=20), nullable=True, comment='Phone number of the contact person at the filling center'),
        sa.Column('is_active', sa.Boolean(), nullable=False, comment='Whether the filling center is active'),
        sa.Column('latitude', sa.Float(), nullable=True, comment='GPS latitude of the filling center'),
        sa.Column('longitude', sa.Float(), nullable=True, comment='GPS longitude of the filling center'),
        sa.Column('notes', sa.String(length=1000), nullable=True, comment='Additional notes about the filling center'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['grand_distributeur_id'], ['grand_distributeurs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_centres_remplisseurs_id'), 'centres_remplisseurs', ['id'], unique=False)
    op.create_index(op.f('ix_centres_remplisseurs_name'), 'centres_remplisseurs', ['name'], unique=False)
    op.create_index(op.f('ix_centres_remplisseurs_code'), 'centres_remplisseurs', ['code'], unique=False)
    op.create_index(op.f('ix_centres_remplisseurs_grand_distributeur_id'), 'centres_remplisseurs', ['grand_distributeur_id'], unique=False)
    
    # Update Partner table to add REVENDEUR type and new fields
    # Note: This assumes PartnerType enum already exists, we're just adding a value
    op.execute("ALTER TYPE partner_type ADD VALUE IF NOT EXISTS 'REVENDEUR'")
    
    op.add_column('partners', sa.Column('code', sa.String(length=50), nullable=True, comment='Unique client code for the partner'))
    op.add_column('partners', sa.Column('parent_grossiste_id', postgresql.UUID(as_uuid=True), nullable=True, comment='For REVENDEUR type, ID of the parent grossiste'))
    op.add_column('partners', sa.Column('contact_name', sa.String(length=255), nullable=True, comment='Name of the primary contact person for the partner'))
    op.add_column('partners', sa.Column('contact_phone', sa.String(length=20), nullable=True, comment='Phone number of the primary contact person for the partner'))
    
    op.create_index(op.f('ix_partners_code'), 'partners', ['code'], unique=True)
    op.create_index(op.f('ix_partners_parent_grossiste_id'), 'partners', ['parent_grossiste_id'], unique=False)
    op.create_foreign_key('fk_partners_parent_grossiste_id', 'partners', 'partners', ['parent_grossiste_id'], ['id'], ondelete='SET NULL')
    
    # Create depots table (if not exists)
    op.create_table(
        'depots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Unique identifier for the depot'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Name of the depot'),
        sa.Column('code', sa.String(length=50), nullable=True, comment='Unique code for the depot'),
        sa.Column('partner_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Foreign key to the Partner model'),
        sa.Column('address', sa.String(length=500), nullable=True, comment='Physical address of the depot'),
        sa.Column('city', sa.String(length=100), nullable=True, comment='City where the depot is located'),
        sa.Column('postal_code', sa.String(length=20), nullable=True, comment='Postal code of the depot'),
        sa.Column('latitude', sa.Float(), nullable=True, comment='GPS latitude of the depot'),
        sa.Column('longitude', sa.Float(), nullable=True, comment='GPS longitude of the depot'),
        sa.Column('contact_name', sa.String(length=255), nullable=True, comment='Name of the contact person at the depot'),
        sa.Column('contact_phone', sa.String(length=20), nullable=True, comment='Phone number of the contact person at the depot'),
        sa.Column('capacity_b28', sa.Integer(), nullable=True, comment='Capacity for B28 palettes'),
        sa.Column('capacity_b12', sa.Integer(), nullable=True, comment='Capacity for B12 palettes'),
        sa.Column('capacity_b6', sa.Integer(), nullable=True, comment='Capacity for B6 palettes'),
        sa.Column('is_active', sa.Boolean(), nullable=False, comment='Whether the depot is active'),
        sa.Column('is_main_depot', sa.Boolean(), nullable=False, comment='Indicates if this is the main depot for the partner'),
        sa.Column('notes', sa.String(length=1000), nullable=True, comment='Additional notes about the depot'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['partner_id'], ['partners.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_depots_id'), 'depots', ['id'], unique=False)
    op.create_index(op.f('ix_depots_name'), 'depots', ['name'], unique=False)
    op.create_index(op.f('ix_depots_code'), 'depots', ['code'], unique=False)
    op.create_index(op.f('ix_depots_partner_id'), 'depots', ['partner_id'], unique=False)
    op.create_index('ix_depots_name_active', 'depots', ['name', 'is_active'], unique=False)
    op.create_index('ix_depots_partner', 'depots', ['partner_id', 'is_active'], unique=False)
    op.create_index('ix_depots_main', 'depots', ['partner_id', 'is_main_depot'], unique=False)
    op.create_index('ix_depots_location', 'depots', ['latitude', 'longitude'], unique=False)
    
    # ### Create workflow tables ###
    
    # Create bons_enlevement table
    op.create_table(
        'bons_enlevement',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Unique identifier for the Bon d Enlèvement'),
        sa.Column('numero_bon', sa.String(length=100), nullable=False, comment='Unique number of the Bon d Enlèvement'),
        sa.Column('reference', sa.String(length=100), nullable=True, comment='Internal reference for the Bon d Enlèvement'),
        sa.Column('centre_remplisseur_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Foreign key to the CentreRemplisseur model'),
        sa.Column('grossiste_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Foreign key to the Partner model (ordering grossiste)'),
        sa.Column('depot_principal_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Foreign key to the Depot model (final destination depot)'),
        sa.Column('vehicule_immatriculation', sa.String(length=50), nullable=True, comment='Vehicle registration number'),
        sa.Column('chauffeur_nom', sa.String(length=255), nullable=True, comment='Name of the driver'),
        sa.Column('chauffeur_societe', sa.String(length=255), nullable=True, comment='Company of the driver'),
        sa.Column('chauffeur_phone', sa.String(length=20), nullable=True, comment='Phone number of the driver'),
        sa.Column('date_creation', sa.DateTime(), nullable=False, comment='Date of creation of the Bon d Enlèvement'),
        sa.Column('date_validation', sa.DateTime(), nullable=True, comment='Date of validation by the filling center'),
        sa.Column('date_chargement', sa.DateTime(), nullable=True, comment='Start date of loading'),
        sa.Column('date_depart', sa.DateTime(), nullable=True, comment='Departure date from the filling center'),
        sa.Column('date_arrivee_finale', sa.DateTime(), nullable=True, comment='Final arrival date at the main depot'),
        sa.Column('status', postgresql.ENUM('CREATION', 'VALIDE', 'EN_CHARGEMENT', 'EN_ROUTE', 'EN_LIVRAISON', 'TERMINE', 'ANNULE', name='bon_enlevement_status', create_type=False), nullable=False, comment='Current status of the Bon d Enlèvement workflow'),
        sa.Column('observations', sa.String(length=1000), nullable=True, comment='Additional observations'),
        sa.Column('instructions_livraison', sa.String(length=1000), nullable=True, comment='Special delivery instructions'),
        sa.Column('validateur_centre_id', postgresql.UUID(as_uuid=True), nullable=True, comment='User who validated the Bon d Enlèvement at the filling center'),
        sa.Column('recepteur_final_id', postgresql.UUID(as_uuid=True), nullable=True, comment='User who received the final delivery at the main depot'),
        sa.Column('otp_code', sa.String(length=10), nullable=True, comment='One-time password for delivery validation'),
        sa.Column('otp_expiry', sa.DateTime(), nullable=True, comment='OTP expiration time'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['centre_remplisseur_id'], ['centres_remplisseurs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['grossiste_id'], ['partners.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['depot_principal_id'], ['depots.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['validateur_centre_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['recepteur_final_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_bon')
    )
    op.create_index(op.f('ix_bons_enlevement_id'), 'bons_enlevement', ['id'], unique=False)
    op.create_index(op.f('ix_bons_enlevement_numero_bon'), 'bons_enlevement', ['numero_bon'], unique=False)
    op.create_index(op.f('ix_bons_enlevement_status'), 'bons_enlevement', ['status'], unique=False)
    op.create_index(op.f('ix_bons_enlevement_date_creation'), 'bons_enlevement', ['date_creation'], unique=False)
    op.create_index(op.f('ix_bons_enlevement_date_depart'), 'bons_enlevement', ['date_depart'], unique=False)
    op.create_index(op.f('ix_bons_enlevement_centre_remplisseur_id'), 'bons_enlevement', ['centre_remplisseur_id'], unique=False)
    op.create_index(op.f('ix_bons_enlevement_grossiste_id'), 'bons_enlevement', ['grossiste_id'], unique=False)
    op.create_index('ix_bons_enlevement_numero_bon_status', 'bons_enlevement', ['numero_bon', 'status'], unique=False)
    op.create_index('ix_bons_enlevement_dates', 'bons_enlevement', ['date_depart', 'date_arrivee_finale'], unique=False)
    op.create_index('ix_bons_enlevement_grossiste_centre', 'bons_enlevement', ['grossiste_id', 'centre_remplisseur_id'], unique=False)
    
    # Create livraisons_details table
    op.create_table(
        'livraisons_details',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Unique livraison detail identifier'),
        sa.Column('bon_enlevement_id', postgresql.UUID(as_uuid=True), nullable=False, comment='FK to bons_enlevement'),
        sa.Column('ordre_livraison', sa.Integer(), nullable=False, comment='Order in tour (1, 2, 3...)'),
        sa.Column('depot_id', postgresql.UUID(as_uuid=True), nullable=True, comment='FK to depots'),
        sa.Column('revendeur_id', postgresql.UUID(as_uuid=True), nullable=True, comment='FK to partners (if revendeur)'),
        sa.Column('date_arrivee', sa.DateTime(), nullable=True, comment='Arrival date'),
        sa.Column('date_depart', sa.DateTime(), nullable=True, comment='Departure date'),
        sa.Column('status', postgresql.ENUM('EN_ATTENTE', 'EN_COURS', 'LIVREE', 'PROBLEME', 'ANNULEE', name='livraison_status', create_type=False), nullable=False, comment='Current status'),
        sa.Column('recepteur_nom', sa.String(length=255), nullable=True, comment='Receiver name'),
        sa.Column('recepteur_signature', sa.String(length=500), nullable=True, comment='Receiver signature (Base64 or path)'),
        sa.Column('observations', sa.String(length=1000), nullable=True, comment='Observations'),
        sa.Column('problemes', sa.String(length=1000), nullable=True, comment='Problems description'),
        sa.Column('latitude_arrivee', sa.Float(), nullable=True, comment='GPS latitude at arrival'),
        sa.Column('longitude_arrivee', sa.Float(), nullable=True, comment='GPS longitude at arrival'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['bon_enlevement_id'], ['bons_enlevement.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['depot_id'], ['depots.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['revendeur_id'], ['partners.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_livraisons_details_id'), 'livraisons_details', ['id'], unique=False)
    op.create_index(op.f('ix_livraisons_details_status'), 'livraisons_details', ['status'], unique=False)
    op.create_index('ix_livraisons_bon', 'livraisons_details', ['bon_enlevement_id', 'ordre_livraison'], unique=False)
    op.create_index('ix_livraisons_status', 'livraisons_details', ['status'], unique=False)
    op.create_index('ix_livraisons_depot', 'livraisons_details', ['depot_id'], unique=False)
    
    # Create association table livraison_palettes
    op.create_table(
        'livraison_palettes',
        sa.Column('livraison_detail_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('palette_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['livraison_detail_id'], ['livraisons_details.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['palette_id'], ['palettes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('livraison_detail_id', 'palette_id')
    )
    op.create_index('ix_livraison_palettes_livraison', 'livraison_palettes', ['livraison_detail_id'], unique=False)
    op.create_index('ix_livraison_palettes_palette', 'livraison_palettes', ['palette_id'], unique=False)
    
    # Create collectes_vides table
    op.create_table(
        'collectes_vides',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Unique collecte vide identifier'),
        sa.Column('bon_enlevement_id', postgresql.UUID(as_uuid=True), nullable=False, comment='FK to bons_enlevement'),
        sa.Column('livraison_detail_id', postgresql.UUID(as_uuid=True), nullable=True, comment='FK to livraisons_details (if multi-depot)'),
        sa.Column('depot_id', postgresql.UUID(as_uuid=True), nullable=True, comment='FK to depots (where collection occurred)'),
        sa.Column('type_bouteille', postgresql.ENUM('B6', 'B12', 'B28', name='palette_type', create_type=False), nullable=False, comment='Bottle type (B6, B12, B28)'),
        sa.Column('quantite_bouteilles_vides', sa.Integer(), nullable=False, comment='Number of empty bottles'),
        sa.Column('quantite_palettes_vides', sa.Integer(), nullable=False, comment='Number of empty palette structures'),
        sa.Column('date_collecte', sa.DateTime(), nullable=False, comment='Collection date'),
        sa.Column('collecteur_nom', sa.String(length=255), nullable=True, comment='Collector name (often driver)'),
        sa.Column('observations', sa.String(length=1000), nullable=True, comment='Observations'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['bon_enlevement_id'], ['bons_enlevement.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['livraison_detail_id'], ['livraisons_details.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['depot_id'], ['depots.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_collectes_vides_id'), 'collectes_vides', ['id'], unique=False)
    op.create_index('ix_collectes_bon', 'collectes_vides', ['bon_enlevement_id'], unique=False)
    op.create_index('ix_collectes_livraison', 'collectes_vides', ['livraison_detail_id'], unique=False)
    op.create_index('ix_collectes_depot', 'collectes_vides', ['depot_id'], unique=False)
    op.create_index('ix_collectes_date', 'collectes_vides', ['date_collecte'], unique=False)
    
    # Create bons_reception_retour table
    op.create_table(
        'bons_reception_retour',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Unique bon reception retour identifier'),
        sa.Column('numero_bl', sa.String(length=100), nullable=False, comment='BL number'),
        sa.Column('numero_reception', sa.String(length=100), nullable=False, comment='Reception number'),
        sa.Column('grossiste_id', postgresql.UUID(as_uuid=True), nullable=True, comment='FK to partners'),
        sa.Column('depot_depart_id', postgresql.UUID(as_uuid=True), nullable=True, comment='FK to depots'),
        sa.Column('centre_remplisseur_id', postgresql.UUID(as_uuid=True), nullable=True, comment='FK to centres_remplisseurs'),
        sa.Column('vehicule_immatriculation', sa.String(length=50), nullable=True, comment='Vehicle registration'),
        sa.Column('transporteur_nom', sa.String(length=255), nullable=True, comment='Transporter name'),
        sa.Column('transporteur_societe', sa.String(length=255), nullable=True, comment='Transporter company'),
        sa.Column('date_creation', sa.DateTime(), nullable=False, comment='Creation date'),
        sa.Column('date_depart', sa.DateTime(), nullable=True, comment='Departure date'),
        sa.Column('date_arrivee', sa.DateTime(), nullable=True, comment='Arrival date'),
        sa.Column('date_controle', sa.DateTime(), nullable=True, comment='Quality control date'),
        sa.Column('date_validation', sa.DateTime(), nullable=True, comment='Validation date'),
        sa.Column('status', postgresql.ENUM('CREATION', 'EN_ROUTE', 'ARRIVE', 'EN_CONTROLE', 'VALIDE', 'REFUSE', name='bon_reception_retour_status', create_type=False), nullable=False, comment='Current status'),
        sa.Column('controleur_id', postgresql.UUID(as_uuid=True), nullable=True, comment='FK to users (quality controller)'),
        sa.Column('magasinier_id', postgresql.UUID(as_uuid=True), nullable=True, comment='FK to users (warehouse keeper)'),
        sa.Column('observations', sa.String(length=1000), nullable=True, comment='Observations'),
        sa.Column('manquants', sa.String(length=1000), nullable=True, comment='Missing items description'),
        sa.Column('client_signature', sa.String(length=500), nullable=True, comment='Client signature'),
        sa.Column('magasinier_signature', sa.String(length=500), nullable=True, comment='Warehouse keeper signature'),
        sa.Column('controleur_signature', sa.String(length=500), nullable=True, comment='Quality controller signature'),
        sa.Column('palette_count', sa.Integer(), nullable=False, comment='Number of palettes'),
        sa.Column('palette_acceptees', sa.Integer(), nullable=False, comment='Number of accepted palettes'),
        sa.Column('palette_refusees', sa.Integer(), nullable=False, comment='Number of refused palettes'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['grossiste_id'], ['partners.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['depot_depart_id'], ['depots.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['centre_remplisseur_id'], ['centres_remplisseurs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['controleur_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['magasinier_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_bl'),
        sa.UniqueConstraint('numero_reception')
    )
    op.create_index(op.f('ix_bons_reception_retour_id'), 'bons_reception_retour', ['id'], unique=False)
    op.create_index(op.f('ix_bons_reception_retour_numero_bl'), 'bons_reception_retour', ['numero_bl'], unique=False)
    op.create_index(op.f('ix_bons_reception_retour_numero_reception'), 'bons_reception_retour', ['numero_reception'], unique=False)
    op.create_index(op.f('ix_bons_reception_retour_status'), 'bons_reception_retour', ['status'], unique=False)
    op.create_index(op.f('ix_bons_reception_retour_date_creation'), 'bons_reception_retour', ['date_creation'], unique=False)
    op.create_index(op.f('ix_bons_reception_retour_grossiste_id'), 'bons_reception_retour', ['grossiste_id'], unique=False)
    op.create_index(op.f('ix_bons_reception_retour_centre_remplisseur_id'), 'bons_reception_retour', ['centre_remplisseur_id'], unique=False)
    op.create_index(op.f('ix_bons_reception_retour_controleur_id'), 'bons_reception_retour', ['controleur_id'], unique=False)
    op.create_index(op.f('ix_bons_reception_retour_magasinier_id'), 'bons_reception_retour', ['magasinier_id'], unique=False)
    op.create_index('ix_bons_ret_numero_bl_status', 'bons_reception_retour', ['numero_bl', 'status'], unique=False)
    op.create_index('ix_bons_ret_grossiste', 'bons_reception_retour', ['grossiste_id', 'status'], unique=False)
    op.create_index('ix_bons_ret_centre', 'bons_reception_retour', ['centre_remplisseur_id', 'status'], unique=False)
    op.create_index('ix_bons_ret_dates', 'bons_reception_retour', ['date_creation', 'date_arrivee'], unique=False)
    
    # Create details_retour table
    op.create_table(
        'details_retour',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Unique detail retour identifier'),
        sa.Column('bon_reception_retour_id', postgresql.UUID(as_uuid=True), nullable=False, comment='FK to bons_reception_retour'),
        sa.Column('type_detail', postgresql.ENUM('PALETTE_VIDE', 'BOUTEILLE_VIDE', 'CONSIGNE', name='detail_retour_type', create_type=False), nullable=False, comment='Type of item'),
        sa.Column('type_bouteille', postgresql.ENUM('B6', 'B12', 'B28', name='palette_type', create_type=False), nullable=True, comment='Bottle type (B6, B12, B28)'),
        sa.Column('quantite_prevue', sa.Integer(), nullable=False, comment='Expected quantity'),
        sa.Column('quantite_recue', sa.Integer(), nullable=False, comment='Received quantity'),
        sa.Column('quantite_acceptee', sa.Integer(), nullable=False, comment='Accepted quantity'),
        sa.Column('quantite_refusee', sa.Integer(), nullable=False, comment='Refused quantity'),
        sa.Column('etat', postgresql.ENUM('BON', 'MOYEN', 'MAUVAIS', 'REFUSE', name='detail_retour_etat', create_type=False), nullable=True, comment='Condition state'),
        sa.Column('observations', sa.String(length=1000), nullable=True, comment='Observations'),
        sa.Column('motif_refus', sa.String(length=500), nullable=True, comment='Refusal reason'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['bon_reception_retour_id'], ['bons_reception_retour.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_details_retour_id'), 'details_retour', ['id'], unique=False)
    op.create_index('ix_details_retour_bon', 'details_retour', ['bon_reception_retour_id'], unique=False)
    op.create_index('ix_details_retour_type', 'details_retour', ['type_detail', 'type_bouteille'], unique=False)
    
    # ### Update Palette table ###
    
    # Add new columns to palettes table
    op.add_column('palettes', sa.Column('current_depot_id', postgresql.UUID(as_uuid=True), nullable=True, comment='ID du dépôt où se trouve actuellement la palette'))
    op.add_column('palettes', sa.Column('current_centre_remplisseur_id', postgresql.UUID(as_uuid=True), nullable=True, comment='ID du centre remplisseur où se trouve actuellement la palette'))
    op.add_column('palettes', sa.Column('is_full', sa.Boolean(), nullable=False, server_default='true', comment='True if palette is full, False if empty'))
    op.add_column('palettes', sa.Column('bon_enlevement_actuel_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Current bon d\'enlèvement if in delivery transit'))
    op.add_column('palettes', sa.Column('bon_retour_actuel_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Current bon de réception retour if in return transit'))
    
    # Create foreign keys for new palette columns
    op.create_foreign_key('fk_palettes_current_depot_id', 'palettes', 'depots', ['current_depot_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_palettes_current_centre_remplisseur_id', 'palettes', 'centres_remplisseurs', ['current_centre_remplisseur_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_palettes_bon_enlevement_actuel_id', 'palettes', 'bons_enlevement', ['bon_enlevement_actuel_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_palettes_bon_retour_actuel_id', 'palettes', 'bons_reception_retour', ['bon_retour_actuel_id'], ['id'], ondelete='SET NULL')
    
    # Create indexes for new palette columns
    op.create_index('ix_palettes_bon_enlevement', 'palettes', ['bon_enlevement_actuel_id'], unique=False)
    op.create_index('ix_palettes_bon_retour', 'palettes', ['bon_retour_actuel_id'], unique=False)
    op.create_index('ix_palettes_depot', 'palettes', ['current_depot_id'], unique=False)
    op.create_index('ix_palettes_centre', 'palettes', ['current_centre_remplisseur_id'], unique=False)
    op.create_index('ix_palettes_full_status', 'palettes', ['is_full', 'status'], unique=False)
    
    # Update PaletteStatus enum to add new values
    # Note: PostgreSQL doesn't support removing enum values, so we only add new ones
    op.execute("ALTER TYPE palette_status ADD VALUE IF NOT EXISTS 'AU_CENTRE'")
    op.execute("ALTER TYPE palette_status ADD VALUE IF NOT EXISTS 'EN_CHARGEMENT'")
    op.execute("ALTER TYPE palette_status ADD VALUE IF NOT EXISTS 'EN_ROUTE_LIVRAISON'")
    op.execute("ALTER TYPE palette_status ADD VALUE IF NOT EXISTS 'AU_DEPOT'")
    op.execute("ALTER TYPE palette_status ADD VALUE IF NOT EXISTS 'EN_ROUTE_RETOUR'")
    op.execute("ALTER TYPE palette_status ADD VALUE IF NOT EXISTS 'EN_CONTROLE'")
    op.execute("ALTER TYPE palette_status ADD VALUE IF NOT EXISTS 'VALIDEE'")
    
    # ### Update PaletteMovement table ###
    
    # Add new columns to palette_movements table
    op.add_column('palette_movements', sa.Column('bon_enlevement_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Related bon d\'enlèvement (optional)'))
    op.add_column('palette_movements', sa.Column('bon_reception_retour_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Related bon de réception retour (optional)'))
    op.add_column('palette_movements', sa.Column('livraison_detail_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Related livraison detail (optional)'))
    op.add_column('palette_movements', sa.Column('depot_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Related depot (optional)'))
    op.add_column('palette_movements', sa.Column('centre_remplisseur_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Related filling center (optional)'))
    
    # Create foreign keys for new palette_movements columns
    op.create_foreign_key('fk_palette_movements_bon_enlevement_id', 'palette_movements', 'bons_enlevement', ['bon_enlevement_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_palette_movements_bon_reception_retour_id', 'palette_movements', 'bons_reception_retour', ['bon_reception_retour_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_palette_movements_livraison_detail_id', 'palette_movements', 'livraisons_details', ['livraison_detail_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_palette_movements_depot_id', 'palette_movements', 'depots', ['depot_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_palette_movements_centre_remplisseur_id', 'palette_movements', 'centres_remplisseurs', ['centre_remplisseur_id'], ['id'], ondelete='SET NULL')
    
    # Create indexes for new palette_movements columns
    op.create_index('ix_movements_bon_enlevement', 'palette_movements', ['bon_enlevement_id', 'timestamp'], unique=False)
    op.create_index('ix_movements_bon_retour', 'palette_movements', ['bon_reception_retour_id', 'timestamp'], unique=False)
    op.create_index('ix_movements_livraison', 'palette_movements', ['livraison_detail_id', 'timestamp'], unique=False)
    op.create_index('ix_movements_depot', 'palette_movements', ['depot_id', 'timestamp'], unique=False)
    op.create_index('ix_movements_centre', 'palette_movements', ['centre_remplisseur_id', 'timestamp'], unique=False)
    
    # Update MovementAction enum to add new values
    op.execute("ALTER TYPE movement_action ADD VALUE IF NOT EXISTS 'ASSIGNATION_BON_ENLEVEMENT'")
    op.execute("ALTER TYPE movement_action ADD VALUE IF NOT EXISTS 'CHARGEMENT_CENTRE'")
    op.execute("ALTER TYPE movement_action ADD VALUE IF NOT EXISTS 'DEPART_CENTRE'")
    op.execute("ALTER TYPE movement_action ADD VALUE IF NOT EXISTS 'ARRIVEE_DEPOT'")
    op.execute("ALTER TYPE movement_action ADD VALUE IF NOT EXISTS 'LIVRAISON_DEPOT'")
    op.execute("ALTER TYPE movement_action ADD VALUE IF NOT EXISTS 'COLLECTE_VIDE'")
    op.execute("ALTER TYPE movement_action ADD VALUE IF NOT EXISTS 'ASSIGNATION_BON_RETOUR'")
    op.execute("ALTER TYPE movement_action ADD VALUE IF NOT EXISTS 'DEPART_DEPOT'")
    op.execute("ALTER TYPE movement_action ADD VALUE IF NOT EXISTS 'ARRIVEE_CENTRE'")
    op.execute("ALTER TYPE movement_action ADD VALUE IF NOT EXISTS 'CONTROLE_QUALITE'")
    op.execute("ALTER TYPE movement_action ADD VALUE IF NOT EXISTS 'VALIDATION_RETOUR'")


def downgrade() -> None:
    # ### Revert PaletteMovement table changes ###
    op.drop_index('ix_movements_centre', table_name='palette_movements')
    op.drop_index('ix_movements_depot', table_name='palette_movements')
    op.drop_index('ix_movements_livraison', table_name='palette_movements')
    op.drop_index('ix_movements_bon_retour', table_name='palette_movements')
    op.drop_index('ix_movements_bon_enlevement', table_name='palette_movements')
    
    op.drop_constraint('fk_palette_movements_centre_remplisseur_id', 'palette_movements', type_='foreignkey')
    op.drop_constraint('fk_palette_movements_depot_id', 'palette_movements', type_='foreignkey')
    op.drop_constraint('fk_palette_movements_livraison_detail_id', 'palette_movements', type_='foreignkey')
    op.drop_constraint('fk_palette_movements_bon_reception_retour_id', 'palette_movements', type_='foreignkey')
    op.drop_constraint('fk_palette_movements_bon_enlevement_id', 'palette_movements', type_='foreignkey')
    
    op.drop_column('palette_movements', 'centre_remplisseur_id')
    op.drop_column('palette_movements', 'depot_id')
    op.drop_column('palette_movements', 'livraison_detail_id')
    op.drop_column('palette_movements', 'bon_reception_retour_id')
    op.drop_column('palette_movements', 'bon_enlevement_id')
    
    # ### Revert Palette table changes ###
    op.drop_index('ix_palettes_full_status', table_name='palettes')
    op.drop_index('ix_palettes_centre', table_name='palettes')
    op.drop_index('ix_palettes_depot', table_name='palettes')
    op.drop_index('ix_palettes_bon_retour', table_name='palettes')
    op.drop_index('ix_palettes_bon_enlevement', table_name='palettes')
    
    op.drop_constraint('fk_palettes_bon_retour_actuel_id', 'palettes', type_='foreignkey')
    op.drop_constraint('fk_palettes_bon_enlevement_actuel_id', 'palettes', type_='foreignkey')
    op.drop_constraint('fk_palettes_current_centre_remplisseur_id', 'palettes', type_='foreignkey')
    op.drop_constraint('fk_palettes_current_depot_id', 'palettes', type_='foreignkey')
    
    op.drop_column('palettes', 'bon_retour_actuel_id')
    op.drop_column('palettes', 'bon_enlevement_actuel_id')
    op.drop_column('palettes', 'is_full')
    op.drop_column('palettes', 'current_centre_remplisseur_id')
    op.drop_column('palettes', 'current_depot_id')
    
    # ### Drop workflow tables ###
    op.drop_table('details_retour')
    op.drop_table('bons_reception_retour')
    op.drop_table('collectes_vides')
    op.drop_table('livraison_palettes')
    op.drop_table('livraisons_details')
    op.drop_table('bons_enlevement')
    op.drop_table('depots')
    
    # ### Revert Partner table changes ###
    op.drop_constraint('fk_partners_parent_grossiste_id', 'partners', type_='foreignkey')
    op.drop_index(op.f('ix_partners_parent_grossiste_id'), table_name='partners')
    op.drop_index(op.f('ix_partners_code'), table_name='partners')
    
    op.drop_column('partners', 'contact_phone')
    op.drop_column('partners', 'contact_name')
    op.drop_column('partners', 'parent_grossiste_id')
    op.drop_column('partners', 'code')
    
    # ### Drop hierarchy tables ###
    op.drop_table('centres_remplisseurs')
    op.drop_table('grand_distributeurs')
    op.drop_table('groupes')
    
    # ### Drop new ENUMs ###
    detail_retour_etat = postgresql.ENUM('BON', 'MOYEN', 'MAUVAIS', 'REFUSE', name='detail_retour_etat')
    detail_retour_etat.drop(op.get_bind(), checkfirst=True)
    
    detail_retour_type = postgresql.ENUM('PALETTE_VIDE', 'BOUTEILLE_VIDE', 'CONSIGNE', name='detail_retour_type')
    detail_retour_type.drop(op.get_bind(), checkfirst=True)
    
    bon_reception_retour_status = postgresql.ENUM('CREATION', 'EN_ROUTE', 'ARRIVE', 'EN_CONTROLE', 'VALIDE', 'REFUSE', name='bon_reception_retour_status')
    bon_reception_retour_status.drop(op.get_bind(), checkfirst=True)
    
    livraison_status = postgresql.ENUM('EN_ATTENTE', 'EN_COURS', 'LIVREE', 'PROBLEME', 'ANNULEE', name='livraison_status')
    livraison_status.drop(op.get_bind(), checkfirst=True)
    
    bon_enlevement_status = postgresql.ENUM('CREATION', 'VALIDE', 'EN_CHARGEMENT', 'EN_ROUTE', 'EN_LIVRAISON', 'TERMINE', 'ANNULE', name='bon_enlevement_status')
    bon_enlevement_status.drop(op.get_bind(), checkfirst=True)

