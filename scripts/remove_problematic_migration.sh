#!/bin/bash
# Script simple pour supprimer la migration problématique add_missing_tables
# La migration phase1_hierarchy devrait déjà avoir créé toutes les tables

set -e

echo "🔧 Suppression de la migration problématique add_missing_tables..."

MIGRATION_FILE=$(find alembic/versions -name "*add_missing_tables*.py" | head -1)

if [ -z "$MIGRATION_FILE" ]; then
    echo "✅ Aucune migration add_missing_tables trouvée - rien à faire"
    exit 0
fi

echo "📝 Migration trouvée: $MIGRATION_FILE"
echo "🗑️  Suppression de la migration problématique..."

# Supprimer la migration
rm "$MIGRATION_FILE"
echo "✅ Migration supprimée"

# Vérifier l'état actuel des migrations
echo ""
echo "📊 État actuel des migrations:"
alembic current

echo ""
echo "💡 La migration phase1_hierarchy devrait avoir créé toutes les tables."
echo "   Vous pouvez maintenant exécuter: alembic upgrade heads"

