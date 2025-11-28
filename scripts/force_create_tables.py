#!/usr/bin/env python3
"""
Script pour forcer la création des tables manquantes directement via SQLAlchemy.
Ceci contourne Alembic pour s'assurer que les tables existent physiquement.
"""
import sys
import asyncio
from pathlib import Path
from sqlalchemy import text, inspect

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import db_manager, Base
# Import all models to ensure they are registered
from app.models import *

async def force_create_tables():
    print("🔄 Vérification et création des tables manquantes...")
    
    await db_manager.init_db()
    
    async with db_manager.engine.begin() as conn:
        # Récupérer les tables existantes
        def get_tables(connection):
            inspector = inspect(connection)
            return inspector.get_table_names()
            
        existing_tables = await conn.run_sync(get_tables)
        print(f"📊 Tables existantes ({len(existing_tables)}): {', '.join(existing_tables)}")
        
        # Identifier les tables manquantes (basé sur les métadonnées SQLAlchemy)
        expected_tables = Base.metadata.tables.keys()
        missing_tables = [t for t in expected_tables if t not in existing_tables]
        
        if not missing_tables:
            print("✅ Toutes les tables semblent exister.")
        else:
            print(f"⚠️  Tables manquantes ({len(missing_tables)}): {', '.join(missing_tables)}")
            print("🔨 Création des tables manquantes...")
            
            # Créer toutes les tables (SQLAlchemy ne crée que celles qui manquent)
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tables créées avec succès.")
            
            # Vérification après création
            existing_tables_after = await conn.run_sync(get_tables)
            print(f"📊 Tables après création ({len(existing_tables_after)}): {', '.join(existing_tables_after)}")

if __name__ == "__main__":
    try:
        asyncio.run(force_create_tables())
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

