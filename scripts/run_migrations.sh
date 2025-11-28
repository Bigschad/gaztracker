#!/bin/bash
# Script pour exécuter les migrations Alembic manuellement

set -e

echo "🔄 Exécution des migrations Alembic..."

# Vérifier que la base de données est accessible
echo "⏳ Vérification de la connexion à la base de données..."
python -c "
from app.database import db_manager
db_manager.init_db()
print('✅ Connexion à la base de données OK')
"

# Exécuter les migrations
echo "📦 Application des migrations..."
alembic upgrade heads

echo "✅ Migrations terminées!"
echo ""
echo "📊 État actuel:"
alembic current

