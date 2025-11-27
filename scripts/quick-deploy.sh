#!/bin/bash
# =============================================================================
# Script de déploiement rapide - Version simplifiée
# Pour un déploiement rapide sur EC2
# =============================================================================

set -e

REPO_URL="https://github.com/Bigschad/gaztracker.git"
BRANCH="${DEPLOY_BRANCH:-develop}"
DEPLOY_DIR="${DEPLOY_DIR:-/opt/gaztracker}"

echo "🚀 Déploiement rapide de GazTracker sur EC2"
echo ""

# Vérifier root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Ce script doit être exécuté avec sudo"
    exit 1
fi

# Installer les dépendances de base
echo "📦 Installation des dépendances..."
apt-get update -y
apt-get install -y git python3 python3-pip python3-venv nodejs npm nginx postgresql redis-server docker.io docker-compose

# Cloner le repo
echo "📥 Téléchargement du code..."
if [ -d "$DEPLOY_DIR" ]; then
    cd "$DEPLOY_DIR"
    git pull origin "$BRANCH"
else
    git clone -b "$BRANCH" "$REPO_URL" "$DEPLOY_DIR"
fi

# Setup Python
echo "🐍 Configuration Python..."
cd "$DEPLOY_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Setup Node.js
echo "📦 Configuration Node.js..."
cd "$DEPLOY_DIR/backoffice-web"
npm install
npm run build

# Créer .env si nécessaire
cd "$DEPLOY_DIR"
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "⚠️  Fichier .env créé - Configurez-le maintenant!"
fi

# Créer service systemd
echo "⚙️  Configuration du service..."
cat > /etc/systemd/system/gaztracker-backend.service <<EOF
[Unit]
Description=GazTracker Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$DEPLOY_DIR
Environment="PATH=$DEPLOY_DIR/venv/bin"
ExecStart=$DEPLOY_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable gaztracker-backend
systemctl start gaztracker-backend

# Configurer Nginx
echo "🌐 Configuration Nginx..."
cat > /etc/nginx/sites-available/gaztracker <<EOF
server {
    listen 80;
    server_name _;
    
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    location / {
        root $DEPLOY_DIR/backoffice-web/dist;
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

ln -sf /etc/nginx/sites-available/gaztracker /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo ""
echo "✅ Déploiement terminé!"
echo "📍 Répertoire: $DEPLOY_DIR"
echo "🔗 URL: http://$(curl -s ifconfig.me)"
echo ""
echo "⚠️  N'oubliez pas de configurer:"
echo "   1. Le fichier .env: $DEPLOY_DIR/.env"
echo "   2. Les migrations: cd $DEPLOY_DIR && source venv/bin/activate && alembic upgrade head"
echo "   3. Le pare-feu EC2 (ports 80, 443)"

