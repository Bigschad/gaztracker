#!/bin/bash
# Script pour corriger les problèmes de révisions Alembic sur le serveur

set -e

echo "🔧 Correction des révisions Alembic..."

cd /opt/gaztracker || exit 1

# Vérifier l'état actuel
echo "📊 État actuel des migrations:"
docker-compose exec -T app alembic current || echo "   Aucune migration appliquée"

# Lister toutes les migrations disponibles
echo ""
echo "📋 Migrations disponibles:"
docker-compose exec -T app alembic history || true

# Vérifier s'il y a des migrations problématiques
echo ""
echo "🔍 Recherche de migrations problématiques..."

# Supprimer la migration add_missing_tables si elle existe
if find alembic/versions -name "*add_missing_tables*.py" 2>/dev/null | grep -q .; then
    echo "⚠️  Migration add_missing_tables trouvée, suppression..."
    rm -f alembic/versions/*add_missing_tables*.py
    echo "✅ Migration supprimée"
fi

# Vérifier que la migration add_logo_to_groupe existe
if [ ! -f "alembic/versions/2025_11_27_add_logo_to_groupe.py" ]; then
    echo "⚠️  Migration add_logo_to_groupe non trouvée!"
    echo "💡 Vérifiez que toutes les migrations sont présentes"
fi

# Essayer de marquer la révision actuelle si nécessaire
echo ""
echo "🔄 Vérification de la chaîne de révisions..."
if docker-compose exec -T app alembic check 2>&1 | grep -q "KeyError\|down_revision"; then
    echo "⚠️  Problème détecté dans la chaîne de révisions"
    echo "💡 Tentative de correction..."
    
    # Obtenir la dernière révision valide
    LAST_VALID=$(docker-compose exec -T app alembic history | grep -E "^\s+[a-f0-9]+" | tail -1 | awk '{print $1}' || echo "")
    
    if [ -n "$LAST_VALID" ]; then
        echo "📌 Marquage de la révision: $LAST_VALID"
        docker-compose exec -T app alembic stamp "$LAST_VALID" || true
    fi
fi

echo ""
echo "✅ Vérification terminée"
echo "💡 Pour appliquer les migrations: docker-compose exec app alembic upgrade heads"

