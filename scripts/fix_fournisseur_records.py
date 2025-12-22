#!/usr/bin/env python3
"""
Script to fix any remaining FOURNISSEUR records in the database.

This script updates all partners with type='FOURNISSEUR' to type='DISTRIBUTEUR'.
It can be run multiple times safely.

Usage:
    python scripts/fix_fournisseur_records.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.database import db_manager
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_fournisseur_records():
    """Fix all FOURNISSEUR records in the database."""
    logger.info("Initializing database connection...")
    db_manager.init_db()
    
    if not db_manager.sync_engine:
        logger.error("Database not initialized")
        return False
    
    try:
        with db_manager.sync_engine.connect() as connection:
            # Check if DISTRIBUTEUR exists in enum
            logger.info("Checking if DISTRIBUTEUR enum value exists...")
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_enum 
                    WHERE enumlabel = 'DISTRIBUTEUR' 
                    AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'partner_type')
                )
            """))
            enum_exists = result.scalar()
            
            if not enum_exists:
                logger.warning("DISTRIBUTEUR enum value does not exist. Adding it...")
                try:
                    connection.execute(text("ALTER TYPE partner_type ADD VALUE 'DISTRIBUTEUR'"))
                    connection.commit()
                    logger.info("DISTRIBUTEUR enum value added successfully")
                except Exception as e:
                    logger.error(f"Failed to add DISTRIBUTEUR enum value: {e}")
                    return False
            
            # Count FOURNISSEUR records
            logger.info("Counting FOURNISSEUR records...")
            result = connection.execute(text("""
                SELECT COUNT(*) FROM partners WHERE type::text = 'FOURNISSEUR';
            """))
            count = result.scalar()
            
            if count == 0:
                logger.info("No FOURNISSEUR records found. Database is clean.")
                return True
            
            logger.info(f"Found {count} FOURNISSEUR record(s) to fix.")
            
            # Update FOURNISSEUR records to DISTRIBUTEUR
            logger.info("Updating FOURNISSEUR records to DISTRIBUTEUR...")
            result = connection.execute(text("""
                UPDATE partners 
                SET type = 'DISTRIBUTEUR'::partner_type 
                WHERE type::text = 'FOURNISSEUR';
            """))
            connection.commit()
            
            updated_count = result.rowcount
            logger.info(f"Successfully updated {updated_count} record(s).")
            
            # Verify no FOURNISSEUR records remain
            result = connection.execute(text("""
                SELECT COUNT(*) FROM partners WHERE type::text = 'FOURNISSEUR';
            """))
            remaining = result.scalar()
            
            if remaining > 0:
                logger.warning(f"WARNING: {remaining} FOURNISSEUR record(s) still remain after update.")
                return False
            else:
                logger.info("All FOURNISSEUR records have been successfully migrated to DISTRIBUTEUR.")
                return True
                
    except Exception as e:
        logger.error(f"Error fixing FOURNISSEUR records: {e}")
        return False
    finally:
        if db_manager.sync_engine:
            db_manager.sync_engine.dispose()


if __name__ == "__main__":
    success = fix_fournisseur_records()
    sys.exit(0 if success else 1)
