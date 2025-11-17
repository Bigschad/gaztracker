#!/bin/bash

# Script pour démarrer le backend dans Docker pour les tests mobile

set -e

echo "🐳 Démarrage du backend dans Docker pour les tests mobile..."

# Aller dans le dossier parent
cd "$(dirname "$0")/../.."

# Vérifier que docker-compose.yml existe
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml non trouvé dans le dossier parent"
    exit 1
fi

# Démarrer les services
echo "🚀 Démarrage des services..."
docker-compose up -d app postgres redis

# Attendre que les services soient prêts
echo "⏳ Attente que les services soient prêts..."
sleep 10

# Vérifier que l'API répond
echo "🧪 Vérification de l'API..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API est prête!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Tentative $RETRY_COUNT/$MAX_RETRIES..."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ L'API n'est pas prête"
    echo "📋 Vérifiez les logs: docker-compose logs app"
    exit 1
fi

# Trouver l'IP locale
if [[ "$OSTYPE" == "darwin"* ]]; then
    IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    IP=$(hostname -I | awk '{print $1}')
else
    IP="192.168.1.100"
fi

echo ""
echo "✅ Backend démarré avec succès!"
echo ""
echo "📋 Informations:"
echo "   - API: http://localhost:8000"
echo "   - API (depuis téléphone): http://$IP:8000"
echo ""
echo "⚠️  Configuration requise dans mobile-app/src/config/apiConfig.ts:"
echo "   baseUrl: 'http://$IP:8000'"
echo ""
echo "📱 Pour lancer l'app mobile:"
echo "   cd mobile-app && npm start"
echo ""

