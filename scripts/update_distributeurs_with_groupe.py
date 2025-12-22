"""
Script to update existing DISTRIBUTEUR partners with groupe_id.

This script assigns all existing DISTRIBUTEUR partners to a specific groupe.
Run this script after adding the groupe_id column to the partners table.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.partner import Partner, PartnerType
from app.models.groupe import Groupe


def update_distributeurs_with_groupe(groupe_id: str = None):
    """
    Update all DISTRIBUTEUR partners to be linked to a groupe.
    
    Args:
        groupe_id: UUID of the groupe to assign. If None, uses the first active groupe.
    """
    db: Session = SessionLocal()
    
    try:
        # Get groupe
        if groupe_id:
            groupe = db.query(Groupe).filter(Groupe.id == groupe_id).first()
            if not groupe:
                print(f"❌ Groupe with ID {groupe_id} not found")
                return
        else:
            # Get first active groupe
            groupe = db.query(Groupe).filter(Groupe.is_active == True).first()
            if not groupe:
                print("❌ No active groupe found. Please create a groupe first.")
                return
        
        print(f"📦 Using groupe: {groupe.name} (ID: {groupe.id})")
        
        # Get all DISTRIBUTEUR partners (optionally filter by those without groupe_id)
        distributeurs_query = db.query(Partner).filter(
            Partner.type == PartnerType.DISTRIBUTEUR
        )
        
        # Option to update only those without groupe_id, or all
        update_all = True  # Set to False to update only those without groupe_id
        if not update_all:
            distributeurs_query = distributeurs_query.filter(Partner.groupe_id.is_(None))
        
        distributeurs = distributeurs_query.all()
        
        if not distributeurs:
            print("✅ No DISTRIBUTEUR partners found")
            return
        
        print(f"📋 Found {len(distributeurs)} DISTRIBUTEUR partner(s):")
        
        # Update each distributeur
        updated_count = 0
        skipped_count = 0
        for dist in distributeurs:
            if dist.groupe_id == groupe.id:
                print(f"  ⊘ {dist.name} -> Already assigned to {groupe.name} (skipped)")
                skipped_count += 1
            else:
                old_groupe = dist.groupe_id
                dist.groupe_id = groupe.id
                if old_groupe:
                    print(f"  ↻ {dist.name} -> Changed from groupe {old_groupe} to {groupe.name}")
                else:
                    print(f"  ✓ {dist.name} -> Assigned to {groupe.name}")
                updated_count += 1
        
        # Commit changes
        db.commit()
        print(f"\n✅ Successfully updated {updated_count} DISTRIBUTEUR partner(s) with groupe_id")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Update DISTRIBUTEUR partners with groupe_id")
    parser.add_argument(
        "--groupe-id",
        type=str,
        help="UUID of the groupe to assign. If not provided, uses the first active groupe."
    )
    
    args = parser.parse_args()
    
    print("🔄 Updating DISTRIBUTEUR partners with groupe_id...")
    update_distributeurs_with_groupe(args.groupe_id)
    print("✨ Done!")
