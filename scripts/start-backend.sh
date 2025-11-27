#!/bin/bash
# Script de démarrage du backend FastAPI avec --host 0.0.0.0
# Ce script garantit que le serveur est accessible depuis le réseau local

echo "========================================"
echo "  Démarrage du backend GazTracker"
echo "========================================"
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -f "venv/bin/activate" ]; then
    echo "[ERREUR] Environnement virtuel non trouvé!"
    echo "Veuillez créer un environnement virtuel avec: python -m venv venv"
    exit 1
fi

# Activer l'environnement virtuel
echo "[1/3] Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier si uvicorn est installé
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "[ERREUR] uvicorn n'est pas installé!"
    echo "Installation en cours..."
    pip install uvicorn[standard]
fi

echo "[2/3] Vérification de la configuration..."
echo "Host: 0.0.0.0 (accessible depuis le réseau local)"
echo "Port: 8000"
echo ""

echo "[3/3] Démarrage du serveur..."
echo ""
echo "========================================"
echo "  Serveur accessible sur:"
echo "  - Local: http://localhost:8000"
echo "  - Réseau: http://$(hostname -I | awk '{print $1}'):8000"
echo "  - Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo "========================================"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

# Démarrer uvicorn avec --host 0.0.0.0
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

