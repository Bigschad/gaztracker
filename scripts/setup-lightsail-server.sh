#!/bin/bash

# Script d'installation initiale sur serveur Lightsail
# À exécuter une seule fois lors de la première configuration

set -e

echo "🚀 Configuration du serveur Lightsail pour GazTracker"
echo "=================================================="

# Mise à jour du système
echo "📦 Mise à jour du système..."
sudo apt-get update
sudo apt-get upgrade -y

# Installation de Docker
echo "🐳 Installation de Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installé"
else
    echo "✅ Docker déjà installé"
fi

# Installation de Docker Compose
echo "🐳 Installation de Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installé"
else
    echo "✅ Docker Compose déjà installé"
fi

# Installation de dépendances système
echo "📦 Installation des dépendances système..."
sudo apt-get install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    net-tools \
    ufw

# Configuration du firewall
echo "🔥 Configuration du firewall..."
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 8000/tcp    # API Backend
sudo ufw allow 3000/tcp    # Frontend
sudo ufw allow 8001/tcp    # API Recette
sudo ufw allow 3001/tcp    # Frontend Recette
sudo ufw --force enable

# Créer les répertoires
echo "📁 Création des répertoires..."
sudo mkdir -p /opt/gaztracker
sudo mkdir -p /opt/gaztracker-recette
sudo chown -R $USER:$USER /opt/gaztracker
sudo chown -R $USER:$USER /opt/gaztracker-recette

# Configuration de la rotation des logs Docker
echo "📝 Configuration de la rotation des logs..."
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

sudo systemctl restart docker

# Augmenter les limites système
echo "⚙️  Configuration des limites système..."
sudo tee -a /etc/sysctl.conf > /dev/null <<EOF
# GazTracker optimizations
fs.file-max = 65536
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 2048
vm.swappiness = 10
EOF

sudo sysctl -p

# Créer un fichier de configuration pour les variables d'environnement
echo "📝 Création du template .env..."
cat > /opt/gaztracker/.env.template <<EOF
# Database
DATABASE_URL=postgresql+asyncpg://gaztracker_user:CHANGE_ME@postgres:5432/gaztracker_db
POSTGRES_USER=gaztracker_user
POSTGRES_PASSWORD=CHANGE_ME
POSTGRES_DB=gaztracker_db

# Redis
REDIS_URL=redis://redis:6379/0

# Application
SECRET_KEY=CHANGE_ME_GENERATE_SECURE_KEY
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=http://YOUR_DOMAIN,http://YOUR_IP:3000

# JWT
JWT_SECRET_KEY=CHANGE_ME_ANOTHER_SECURE_KEY
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=30

# Admin user
ADMIN_EMAIL=admin@gaztracker.com
ADMIN_PASSWORD=CHANGE_ME_ADMIN_PASSWORD
EOF

echo ""
echo "✅ Configuration du serveur terminée!"
echo ""
echo "📋 PROCHAINES ÉTAPES:"
echo "1. Déconnectez-vous et reconnectez-vous pour activer Docker"
echo "2. Configurez les secrets GitHub Actions:"
echo "   - LIGHTSAIL_SSH_KEY: Clé SSH privée"
echo "   - LIGHTSAIL_HOST: IP ou domaine du serveur"
echo "   - LIGHTSAIL_USER: Nom d'utilisateur SSH (généralement ubuntu)"
echo ""
echo "3. Copiez et configurez le fichier .env:"
echo "   cd /opt/gaztracker"
echo "   cp .env.template .env"
echo "   nano .env  # Modifier les valeurs CHANGE_ME"
echo ""
echo "4. Générez des clés sécurisées:"
echo "   python3 -c 'import secrets; print(secrets.token_urlsafe(32))'"
echo ""
echo "5. Le premier déploiement se fera automatiquement via GitHub Actions"
echo ""

