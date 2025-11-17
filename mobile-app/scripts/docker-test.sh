#!/bin/bash

# Script de test avec Docker pour GazTracker Mobile

set -e

echo "🐳 Configuration de l'environnement de test Docker..."

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker installé: $(docker --version)${NC}"

# Vérifier Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose n'est pas installé${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker Compose installé: $(docker-compose --version)${NC}"

# Trouver l'IP locale
echo -e "${YELLOW}🔍 Recherche de l'IP locale...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    IP=$(hostname -I | awk '{print $1}')
else
    IP="192.168.1.100"  # Par défaut
fi

echo -e "${GREEN}📍 IP locale: $IP${NC}"

# Démarrer les services
echo -e "${YELLOW}🚀 Démarrage des services Docker...${NC}"
docker-compose -f docker-compose.mobile.yml up -d

# Attendre que l'API soit prête
echo -e "${YELLOW}⏳ Attente que l'API soit prête...${NC}"
sleep 10

# Test de santé
echo -e "${YELLOW}🧪 Test de l'API...${NC}"
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API est prête!${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -e "${YELLOW}   Tentative $RETRY_COUNT/$MAX_RETRIES...${NC}"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ L'API n'est pas prête après $MAX_RETRIES tentatives${NC}"
    echo -e "${YELLOW}📋 Vérifiez les logs: docker-compose -f docker-compose.mobile.yml logs api${NC}"
    exit 1
fi

# Afficher les informations
echo ""
echo -e "${GREEN}✅ Environnement Docker prêt!${NC}"
echo ""
echo -e "${YELLOW}📋 Informations importantes:${NC}"
echo "   - API: http://localhost:8000"
echo "   - API (depuis téléphone): http://$IP:8000"
echo "   - Health check: http://localhost:8000/health"
echo ""
echo -e "${YELLOW}⚠️  Configuration requise:${NC}"
echo "   1. Mettre à jour src/config/apiConfig.ts:"
echo "      baseUrl: 'http://$IP:8000'"
echo ""
echo "   2. Vérifier que votre téléphone est sur le même WiFi"
echo ""
echo -e "${YELLOW}📱 Commandes utiles:${NC}"
echo "   - Voir les logs: docker-compose -f docker-compose.mobile.yml logs -f"
echo "   - Arrêter: docker-compose -f docker-compose.mobile.yml down"
echo "   - Redémarrer: docker-compose -f docker-compose.mobile.yml restart api"
echo ""

