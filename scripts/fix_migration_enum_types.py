#!/usr/bin/env python3
"""
Script pour corriger la migration add_missing_tables qui essaie de créer
des types ENUM qui existent déjà.

Ce script doit être exécuté sur le serveur pour modifier la migration
problématique avant de l'appliquer.
"""
import os
import re
from pathlib import Path

def fix_migration_file(migration_file: Path):
    """Corrige la migration pour vérifier l'existence des types ENUM."""
    print(f"📝 Correction de la migration: {migration_file.name}")
    
    content = migration_file.read_text(encoding='utf-8')
    
    # Pattern pour trouver les créations de types ENUM
    # Exemple: sa.Column('type_bouteille', postgresql.ENUM('B6', 'B12', 'B28', name='palette_type', create_type=False), ...)
    # On veut changer create_type=False en create_type=False et ajouter checkfirst
    
    # Mais le vrai problème est dans les op.create_table qui créent des ENUM
    # Il faut ajouter une fonction helper au début de upgrade()
    
    # Chercher la fonction upgrade()
    upgrade_match = re.search(r'def upgrade\(\) -> None:\s*\n\s*""".*?"""\s*\n', content, re.DOTALL)
    if not upgrade_match:
        upgrade_match = re.search(r'def upgrade\(\) -> None:\s*\n', content)
    
    if upgrade_match:
        # Ajouter la fonction helper après la signature de upgrade()
        helper_function = '''
    # Helper function to create ENUM if it doesn't exist
    conn = op.get_bind()
    def create_enum_if_not_exists(enum_name: str, enum_values: list):
        result = conn.execute(sa.text(
            "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = :name)"
        ), {"name": enum_name})
        exists = result.scalar()
        if not exists:
            enum = postgresql.ENUM(*enum_values, name=enum_name)
            enum.create(conn)
    
'''
        
        # Insérer la fonction helper après la signature
        insert_pos = upgrade_match.end()
        content = content[:insert_pos] + helper_function + content[insert_pos:]
        
        # Remplacer toutes les créations de types ENUM par des appels à create_enum_if_not_exists
        # Pattern: postgresql.ENUM('B6', 'B12', 'B28', name='palette_type', create_type=False)
        # On ne peut pas facilement remplacer automatiquement, donc on ajoute juste les vérifications
        
        # Ajouter les imports nécessaires si pas présents
        if 'from sqlalchemy.dialects import postgresql' not in content:
            # Chercher les imports
            import_match = re.search(r'(from alembic import op\nimport sqlalchemy as sa)', content)
            if import_match:
                content = content[:import_match.end()] + '\nfrom sqlalchemy.dialects import postgresql' + content[import_match.end():]
        
        # Ajouter les vérifications pour les types ENUM communs
        enum_checks = '''
    # Ensure ENUM types exist before creating tables
    create_enum_if_not_exists('palette_type', ['B6', 'B12', 'B28'])
    create_enum_if_not_exists('bon_enlevement_status', 
        ['CREATION', 'VALIDE', 'EN_CHARGEMENT', 'EN_ROUTE', 'EN_LIVRAISON', 'TERMINE', 'ANNULE'])
    create_enum_if_not_exists('livraison_status',
        ['EN_ATTENTE', 'EN_COURS', 'LIVREE', 'PROBLEME', 'ANNULEE'])
    create_enum_if_not_exists('bon_reception_retour_status',
        ['CREATION', 'EN_ROUTE', 'ARRIVE', 'EN_CONTROLE', 'VALIDE', 'REFUSE'])
    create_enum_if_not_exists('detail_retour_type',
        ['PALETTE_VIDE', 'BOUTEILLE_VIDE', 'CONSIGNE'])
    create_enum_if_not_exists('detail_retour_etat',
        ['BON', 'MOYEN', 'MAUVAIS', 'REFUSE'])
    
'''
        
        # Trouver où insérer les vérifications (après la fonction helper, avant les op.create_table)
        create_table_match = re.search(r'op\.create_table\(', content)
        if create_table_match:
            insert_pos = create_table_match.start()
            content = content[:insert_pos] + enum_checks + content[insert_pos:]
        
        # Sauvegarder
        migration_file.write_text(content, encoding='utf-8')
        print(f"✅ Migration corrigée: {migration_file.name}")
        return True
    else:
        print(f"⚠️  Impossible de trouver la fonction upgrade() dans {migration_file.name}")
        return False

def main():
    """Trouve et corrige la migration problématique."""
    alembic_versions = Path('alembic/versions')
    
    if not alembic_versions.exists():
        print("❌ Dossier alembic/versions introuvable")
        return
    
    # Chercher la migration add_missing_tables
    migration_files = list(alembic_versions.glob('*add_missing_tables*.py'))
    
    if not migration_files:
        print("⚠️  Aucune migration add_missing_tables trouvée")
        print("💡 Le script peut être exécuté manuellement sur le serveur")
        return
    
    for migration_file in migration_files:
        fix_migration_file(migration_file)

if __name__ == "__main__":
    main()

