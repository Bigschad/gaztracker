"""
Script to update existing DISTRIBUTEUR partners with groupe_id from active user's groupe.

This script:
1. Finds all DISTRIBUTEUR partners without a groupe_id
2. Gets the groupe_id from ADMIN users' company_name
3. Updates distributeurs to link them to the groupe
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import db_manager
from app.models.partner import Partner, PartnerType
from app.models.user import User, UserRole
from app.models.groupe import Groupe

# Initialize database
db_manager.init_db()

# Create session factory
def SessionLocal():
    """Create a new database session"""
    return db_manager.sync_session_maker()

def update_distributeurs_with_groupe():
    """Update DISTRIBUTEUR partners with groupe_id from ADMIN users."""
    
    db: Session = SessionLocal()
    
    try:
        # Get all ADMIN users and their groupe_id (stored in company_name)
        admin_users = db.query(User).filter(
            User.role == UserRole.ADMIN,
            User.company_name.isnot(None),
            User.company_name != ''
        ).all()
        
        if not admin_users:
            print("Aucun utilisateur ADMIN avec un groupe actif trouvé.")
            return
        
        # Get groupe_id from ADMIN users' company_name
        # Try to find a valid groupe_id
        groupe_id = None
        groupe = None
        
        print(f"\nRecherche du groupe actif parmi {len(admin_users)} utilisateur(s) ADMIN...")
        for admin_user in admin_users:
            potential_groupe_id = admin_user.company_name
            print(f"  - Utilisateur {admin_user.email}: company_name = {potential_groupe_id}")
            if potential_groupe_id:
                # Try to find the groupe (handle both UUID string and UUID object)
                try:
                    potential_groupe = db.query(Groupe).filter(Groupe.id == potential_groupe_id).first()
                    if potential_groupe:
                        groupe_id = potential_groupe_id
                        groupe = potential_groupe
                        print(f"  ✓ Groupe trouvé: {groupe.name} ({groupe.code})")
                        break
                    else:
                        print(f"    ⚠️  Aucun groupe trouvé avec l'ID {potential_groupe_id}")
                except Exception as e:
                    print(f"    ⚠️  Erreur lors de la recherche du groupe: {e}")
        
        if not groupe_id or not groupe:
            print("\nERREUR: Aucun groupe valide trouvé dans les utilisateurs ADMIN.")
            print("Vérifiez que:")
            print("  1. Les utilisateurs ADMIN ont un company_name défini")
            print("  2. Le company_name correspond à un groupe_id valide dans la table groupes")
            return
        
        print(f"Groupe trouvé: {groupe.name} ({groupe.code})")
        
        # Find all DISTRIBUTEUR partners without a groupe_id
        distributeurs = db.query(Partner).filter(
            Partner.type == PartnerType.DISTRIBUTEUR,
            (Partner.groupe_id.is_(None) | (Partner.groupe_id == ''))
        ).all()
        
        if not distributeurs:
            print("Aucun distributeur sans groupe_id trouvé.")
            return
        
        print(f"\nTrouvé {len(distributeurs)} distributeur(s) sans groupe_id:")
        for dist in distributeurs:
            print(f"  - {dist.name} (ID: {dist.id})")
        
        # Update all distributeurs with the groupe_id
        updated_count = 0
        for dist in distributeurs:
            dist.groupe_id = groupe_id
            updated_count += 1
            print(f"  ✓ Mis à jour: {dist.name} -> Groupe: {groupe.name}")
        
        db.commit()
        print(f"\n✓ {updated_count} distributeur(s) mis à jour avec succès avec le groupe {groupe.name}.")
        
    except Exception as e:
        db.rollback()
        print(f"ERREUR lors de la mise à jour: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Mise à jour des distributeurs avec le groupe actif")
    print("=" * 60)
    update_distributeurs_with_groupe()
    print("=" * 60)
