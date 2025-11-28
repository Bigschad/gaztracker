#!/bin/bash
# Script à exécuter sur le serveur pour corriger la migration problématique

set -e

echo "🔧 Correction de la migration add_missing_tables..."

MIGRATION_FILE=$(find alembic/versions -name "*add_missing_tables*.py" | head -1)

if [ -z "$MIGRATION_FILE" ]; then
    echo "❌ Migration add_missing_tables introuvable"
    exit 1
fi

echo "📝 Migration trouvée: $MIGRATION_FILE"

# Créer une sauvegarde
cp "$MIGRATION_FILE" "${MIGRATION_FILE}.backup"

# Ajouter les imports nécessaires
if ! grep -q "from sqlalchemy.dialects import postgresql" "$MIGRATION_FILE"; then
    sed -i '/^import sqlalchemy as sa/a from sqlalchemy.dialects import postgresql' "$MIGRATION_FILE"
fi

# Ajouter la fonction helper et les vérifications dans upgrade()
# Cette partie nécessite une modification Python plus complexe
# On va utiliser Python pour faire la modification

python3 << 'PYTHON_SCRIPT'
import re
from pathlib import Path

migration_file = Path("$MIGRATION_FILE")
content = migration_file.read_text(encoding='utf-8')

# Ajouter la fonction helper après def upgrade()
upgrade_pattern = r'(def upgrade\(\) -> None:\s*\n)'
helper_function = '''def upgrade() -> None:
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

# Remplacer la fonction upgrade
if re.search(upgrade_pattern, content):
    content = re.sub(
        upgrade_pattern,
        helper_function,
        content,
        count=1
    )
    migration_file.write_text(content, encoding='utf-8')
    print("✅ Migration corrigée")
else:
    print("⚠️  Impossible de trouver la fonction upgrade()")
    exit(1)
PYTHON_SCRIPT

echo "✅ Migration corrigée avec succès!"
echo "💡 Vous pouvez maintenant exécuter: alembic upgrade heads"

