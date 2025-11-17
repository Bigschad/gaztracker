#!/bin/bash

# Script de configuration et test pour GazTracker Mobile

echo "🚀 Configuration de l'environnement de test..."

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé"
    exit 1
fi

echo "✅ Node.js installé: $(node --version)"

# Vérifier npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm n'est pas installé"
    exit 1
fi

echo "✅ npm installé: $(npm --version)"

# Installer les dépendances
echo "📦 Installation des dépendances..."
npm install

# Vérifier Expo
if ! command -v expo &> /dev/null; then
    echo "📦 Installation d'Expo CLI..."
    npm install -g expo-cli
fi

echo "✅ Expo CLI installé"

# Trouver l'IP locale
echo "🔍 Recherche de l'IP locale..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Mac
    IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    IP=$(hostname -I | awk '{print $1}')
else
    # Windows (Git Bash)
    IP=$(ipconfig | grep "IPv4" | awk '{print $14}' | head -n 1)
fi

echo "📍 IP locale trouvée: $IP"
echo ""
echo "⚠️  IMPORTANT: Mettez à jour src/config/apiConfig.ts avec cette IP:"
echo "   baseUrl: 'http://$IP:8000'"
echo ""
echo "✅ Configuration terminée!"
echo ""
echo "📱 Pour démarrer l'application:"
echo "   npm start"
echo ""
echo "🔧 Pour tester sur Android:"
echo "   npm run android"
echo ""

