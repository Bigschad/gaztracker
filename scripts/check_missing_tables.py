#!/usr/bin/env python3
"""
Script pour vérifier quelles tables manquent dans la base de données
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import inspect, text
from app.database import db_manager
from app.models import (
    User, Palette, RFIDTag, Expedition, PaletteMovement,
    Notification, AuditLog, Partner, Contact,
    Groupe, GrandDistributeur, CentreRemplisseur, Depot,
    BonEnlevement, LivraisonDetail, CollecteVide,
    BonReceptionRetour, DetailRetour
)

def check_tables():
    """Vérifie quelles tables existent dans la base de données"""
    print("=" * 60)
    print("🔍 VÉRIFICATION DES TABLES DANS LA BASE DE DONNÉES")
    print("=" * 60)
    
    # Initialize database
    db_manager.init_db()
    db = next(db_manager.get_db())
    
    try:
        # Get inspector
        inspector = inspect(db_manager.engine)
        existing_tables = set(inspector.get_table_names())
        
        # Expected tables from models
        expected_tables = {
            'users', 'palettes', 'rfid_tags', 'expeditions',
            'palette_movements', 'notifications', 'audit_logs',
            'partners', 'contacts',
            'groupes', 'grand_distributeurs', 'centres_remplisseurs', 'depots',
            'bons_enlevement', 'livraisons_details', 'collectes_vides',
            'bons_reception_retour', 'details_retour',
            'livraison_palettes',  # Association table
            'system_config'  # System config table
        }
        
        print(f"\n📊 Tables attendues: {len(expected_tables)}")
        print(f"📊 Tables existantes: {len(existing_tables)}")
        
        # Find missing tables
        missing_tables = expected_tables - existing_tables
        extra_tables = existing_tables - expected_tables
        
        if missing_tables:
            print(f"\n❌ TABLES MANQUANTES ({len(missing_tables)}):")
            for table in sorted(missing_tables):
                print(f"   • {table}")
        else:
            print("\n✅ Toutes les tables attendues sont présentes!")
        
        if extra_tables:
            print(f"\n⚠️  TABLES SUPPLÉMENTAIRES ({len(extra_tables)}):")
            for table in sorted(extra_tables):
                print(f"   • {table}")
        
        # Check alembic_version table
        try:
            result = db.execute(text("SELECT version_num FROM alembic_version"))
            current_revision = result.scalar()
            print(f"\n📌 Révision Alembic actuelle: {current_revision}")
        except Exception as e:
            print(f"\n⚠️  Impossible de lire la révision Alembic: {e}")
        
        return len(missing_tables) == 0
        
    finally:
        db.close()

if __name__ == "__main__":
    try:
        success = check_tables()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

