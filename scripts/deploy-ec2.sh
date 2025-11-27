#!/bin/bash
# =============================================================================
# Script de déploiement automatique sur EC2
# Déploie le backend FastAPI, le backoffice React et toutes les dépendances
# =============================================================================

set -e  # Arrêter en cas d'erreur

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/Bigschad/gaztracker.git"
BRANCH="${DEPLOY_BRANCH:-develop}"
DEPLOY_DIR="${DEPLOY_DIR:-/opt/gaztracker}"
APP_USER="${APP_USER:-gaztracker}"
SERVICE_NAME="gaztracker"

# Fonction pour afficher les messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que le script est exécuté en tant que root ou avec sudo
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        log_error "Ce script doit être exécuté en tant que root ou avec sudo"
        exit 1
    fi
}

# Variable globale pour la distribution
OS=""

# Installer les dépendances système
install_system_dependencies() {
    log_info "Installation des dépendances système..."
    
    # Détecter la distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    else
        log_error "Impossible de détecter la distribution"
        exit 1
    fi
    
    log_info "Distribution détectée: $OS"
    
    # Mettre à jour le système
    apt-get update -y || yum update -y
    
    # Installer les dépendances selon la distribution
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        apt-get install -y \
            git \
            curl \
            wget \
            build-essential \
            python3.12 \
            python3.12-venv \
            python3-pip \
            postgresql-client \
            nginx \
            supervisor \
            certbot \
            python3-certbot-nginx \
            docker.io \
            docker-compose \
            nodejs \
            npm
    elif [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
        # Amazon Linux 2 / RHEL / CentOS
        yum install -y \
            git \
            curl \
            wget \
            gcc \
            gcc-c++ \
            make \
            python3 \
            python3-pip \
            postgresql \
            nginx \
            supervisor \
            docker \
            nodejs \
            npm
        
        # Installer Docker Compose
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        
        # Installer Certbot
        yum install -y certbot python3-certbot-nginx || pip3 install certbot-nginx
    fi
    
    # Démarrer Docker
    systemctl enable docker
    systemctl start docker || service docker start
    
    log_success "Dépendances système installées"
}

# Créer l'utilisateur de l'application
create_app_user() {
    log_info "Création de l'utilisateur $APP_USER..."
    
    if ! id "$APP_USER" &>/dev/null; then
        useradd -r -m -s /bin/bash -d "$DEPLOY_DIR" "$APP_USER"
        usermod -aG docker "$APP_USER"
        log_success "Utilisateur $APP_USER créé"
    else
        log_warning "L'utilisateur $APP_USER existe déjà"
    fi
}

# Cloner ou mettre à jour le dépôt
clone_or_update_repo() {
    log_info "Téléchargement/mise à jour du code depuis GitHub..."
    
    if [ -d "$DEPLOY_DIR" ]; then
        log_info "Le répertoire existe, mise à jour..."
        cd "$DEPLOY_DIR"
        git fetch origin
        git checkout "$BRANCH"
        git pull origin "$BRANCH"
    else
        log_info "Clonage du dépôt..."
        mkdir -p "$DEPLOY_DIR"
        git clone -b "$BRANCH" "$REPO_URL" "$DEPLOY_DIR"
    fi
    
    # Changer le propriétaire
    chown -R "$APP_USER:$APP_USER" "$DEPLOY_DIR"
    
    log_success "Code téléchargé/mis à jour"
}

# Configurer l'environnement Python
setup_python_env() {
    log_info "Configuration de l'environnement Python..."
    
    cd "$DEPLOY_DIR"
    
    # Détecter la version de Python disponible
    if command -v python3.12 &> /dev/null; then
        PYTHON_CMD="python3.12"
    elif command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
    elif command -v python3.10 &> /dev/null; then
        PYTHON_CMD="python3.10"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        log_error "Python 3 n'est pas installé!"
        exit 1
    fi
    
    log_info "Utilisation de $PYTHON_CMD"
    
    sudo -u "$APP_USER" bash <<EOF
        # Créer l'environnement virtuel s'il n'existe pas
        if [ ! -d "venv" ]; then
            $PYTHON_CMD -m venv venv
        fi
        
        # Activer et mettre à jour pip
        source venv/bin/activate
        pip install --upgrade pip setuptools wheel
        
        # Installer les dépendances
        pip install -r requirements.txt
EOF
    
    log_success "Environnement Python configuré"
}

# Configurer l'environnement Node.js pour le backoffice
setup_node_env() {
    log_info "Configuration de l'environnement Node.js pour le backoffice..."
    
    cd "$DEPLOY_DIR/backoffice-web"
    sudo -u "$APP_USER" bash <<EOF
        # Installer les dépendances
        npm install
        
        # Build de production
        npm run build
EOF
    
    log_success "Environnement Node.js configuré"
}

# Configurer les variables d'environnement
setup_environment() {
    log_info "Configuration des variables d'environnement..."
    
    cd "$DEPLOY_DIR"
    
    # Créer le fichier .env s'il n'existe pas
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_warning "Fichier .env créé depuis .env.example"
            log_warning "⚠️  IMPORTANT: Éditez $DEPLOY_DIR/.env avec vos configurations!"
        else
            log_error "Fichier .env.example non trouvé!"
            exit 1
        fi
    else
        log_info "Fichier .env existe déjà"
    fi
    
    # S'assurer que le fichier .env appartient à l'utilisateur de l'app
    chown "$APP_USER:$APP_USER" .env
    chmod 600 .env
    
    log_success "Variables d'environnement configurées"
}

# Configurer PostgreSQL (si pas déjà fait)
setup_postgresql() {
    log_info "Configuration de PostgreSQL..."
    
    # Vérifier si PostgreSQL est installé
    if ! command -v psql &> /dev/null; then
        log_info "Installation de PostgreSQL..."
        if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
            apt-get install -y postgresql postgresql-contrib
        elif [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
            yum install -y postgresql-server postgresql-contrib
            postgresql-setup initdb || /usr/bin/postgresql-setup --initdb
        fi
        systemctl enable postgresql
        systemctl start postgresql || service postgresql start
    fi
    
    log_success "PostgreSQL configuré"
}

# Configurer Redis (si pas déjà fait)
setup_redis() {
    log_info "Configuration de Redis..."
    
    # Vérifier si Redis est installé
    if ! command -v redis-cli &> /dev/null; then
        log_info "Installation de Redis..."
        if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
            apt-get install -y redis-server
        elif [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
            yum install -y redis
        fi
        systemctl enable redis-server || systemctl enable redis
        systemctl start redis-server || systemctl start redis || service redis start
    fi
    
    log_success "Redis configuré"
}

# Exécuter les migrations de base de données
run_migrations() {
    log_info "Exécution des migrations de base de données..."
    
    cd "$DEPLOY_DIR"
    sudo -u "$APP_USER" bash <<EOF
        source venv/bin/activate
        
        # Vérifier si Alembic est disponible
        if command -v alembic &> /dev/null || [ -f "alembic.ini" ]; then
            alembic upgrade head
        else
            log_warning "Alembic non trouvé, création des tables directement..."
            python -c "from app.database import db_manager; import asyncio; asyncio.run(db_manager.init_db()); asyncio.run(db_manager.create_tables())" || true
        fi
EOF
    
    log_success "Migrations exécutées"
}

# Créer le service systemd pour le backend
create_backend_service() {
    log_info "Création du service systemd pour le backend..."
    
    cat > "/etc/systemd/system/${SERVICE_NAME}-backend.service" <<EOF
[Unit]
Description=GazTracker Backend API
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$DEPLOY_DIR
Environment="PATH=$DEPLOY_DIR/venv/bin"
ExecStart=$DEPLOY_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable "${SERVICE_NAME}-backend"
    
    log_success "Service backend créé"
}

# Créer le service systemd pour le frontend (nginx)
create_frontend_service() {
    log_info "Configuration de Nginx pour le frontend..."
    
    # Créer la configuration Nginx
    cat > "/etc/nginx/sites-available/${SERVICE_NAME}" <<EOF
# Backend API
server {
    listen 80;
    server_name _;
    
    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Backend Docs
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /openapi.json {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Frontend (Backoffice)
    location / {
        root $DEPLOY_DIR/backoffice-web/dist;
        try_files \$uri \$uri/ /index.html;
        index index.html;
    }
}
EOF
    
    # Activer le site
    ln -sf "/etc/nginx/sites-available/${SERVICE_NAME}" "/etc/nginx/sites-enabled/${SERVICE_NAME}"
    
    # Supprimer la configuration par défaut si elle existe
    rm -f /etc/nginx/sites-enabled/default
    
    # Tester la configuration Nginx
    nginx -t
    
    systemctl enable nginx
    systemctl restart nginx
    
    log_success "Nginx configuré"
}

# Démarrer les services
start_services() {
    log_info "Démarrage des services..."
    
    # Démarrer PostgreSQL et Redis s'ils ne sont pas déjà démarrés
    systemctl start postgresql || true
    systemctl start redis-server || true
    
    # Démarrer le backend
    systemctl start "${SERVICE_NAME}-backend"
    
    # Attendre que le backend soit prêt
    sleep 5
    
    # Vérifier le statut
    if systemctl is-active --quiet "${SERVICE_NAME}-backend"; then
        log_success "Services démarrés avec succès"
    else
        log_error "Erreur lors du démarrage des services"
        systemctl status "${SERVICE_NAME}-backend"
        exit 1
    fi
}

# Afficher les informations de déploiement
show_deployment_info() {
    log_success "=========================================="
    log_success "  Déploiement terminé avec succès!"
    log_success "=========================================="
    echo ""
    echo "📍 Répertoire de déploiement: $DEPLOY_DIR"
    echo "👤 Utilisateur: $APP_USER"
    echo "🌿 Branche: $BRANCH"
    echo ""
    echo "🔗 URLs:"
    echo "  - Backend API: http://$(curl -s ifconfig.me)/api/v1"
    echo "  - Backend Docs: http://$(curl -s ifconfig.me)/docs"
    echo "  - Frontend: http://$(curl -s ifconfig.me)/"
    echo ""
    echo "📋 Commandes utiles:"
    echo "  - Voir les logs backend: journalctl -u ${SERVICE_NAME}-backend -f"
    echo "  - Redémarrer backend: systemctl restart ${SERVICE_NAME}-backend"
    echo "  - Statut services: systemctl status ${SERVICE_NAME}-backend"
    echo "  - Voir les logs Nginx: tail -f /var/log/nginx/error.log"
    echo ""
    echo "⚠️  IMPORTANT:"
    echo "  1. Configurez le fichier .env: $DEPLOY_DIR/.env"
    echo "  2. Configurez le pare-feu EC2 pour ouvrir les ports 80 et 443"
    echo "  3. Pour HTTPS, exécutez: certbot --nginx -d votre-domaine.com"
    echo ""
}

# Fonction principale
main() {
    log_info "=========================================="
    log_info "  Déploiement GazTracker sur EC2"
    log_info "=========================================="
    echo ""
    
    check_root
    install_system_dependencies
    create_app_user
    clone_or_update_repo
    setup_python_env
    setup_node_env
    setup_environment
    setup_postgresql
    setup_redis
    run_migrations
    create_backend_service
    create_frontend_service
    start_services
    show_deployment_info
}

# Exécuter le script principal
main "$@"

