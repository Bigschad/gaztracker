#!/bin/bash
# =============================================================================
# Script de déploiement automatique sur EC2 avec Docker
# Version alternative utilisant Docker Compose
# =============================================================================

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
REPO_URL="https://github.com/Bigschad/gaztracker.git"
BRANCH="${DEPLOY_BRANCH:-develop}"
DEPLOY_DIR="${DEPLOY_DIR:-/opt/gaztracker}"

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_root() {
    if [ "$EUID" -ne 0 ]; then 
        log_error "Ce script doit être exécuté en tant que root ou avec sudo"
        exit 1
    fi
}

install_docker() {
    log_info "Installation de Docker et Docker Compose..."
    
    # Détecter la distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    else
        log_error "Impossible de détecter la distribution"
        exit 1
    fi
    
    log_info "Distribution détectée: $OS"
    
    # Installer selon la distribution
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        apt-get update -y
        apt-get install -y \
            git \
            curl \
            docker.io \
            docker-compose \
            nginx \
            certbot \
            python3-certbot-nginx
    elif [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ] || [ "$OS" = "fedora" ]; then
        # Amazon Linux 2023 / RHEL / CentOS / Fedora
        # Détecter si on utilise yum ou dnf
        if command -v dnf &> /dev/null; then
            PKG_MGR="dnf"
        else
            PKG_MGR="yum"
        fi
        
        log_info "Utilisation de $PKG_MGR comme gestionnaire de paquets"
        
        $PKG_MGR update -y
        
        # Installer git et nginx
        $PKG_MGR install -y git nginx
        
        # Gérer curl : remplacer curl-minimal par curl complet si nécessaire
        if rpm -q curl-minimal &> /dev/null; then
            log_info "curl-minimal détecté, remplacement par curl complet..."
            $PKG_MGR install -y curl --allowerasing || $PKG_MGR install -y curl
        else
            # Vérifier si curl est déjà installé
            if ! command -v curl &> /dev/null; then
                $PKG_MGR install -y curl
            else
                log_info "curl est déjà installé"
            fi
        fi
        
        # Installer Docker
        if ! command -v docker &> /dev/null; then
            log_info "Installation de Docker..."
            if [ "$OS" = "amzn" ]; then
                # Amazon Linux 2023
                $PKG_MGR install -y docker
            else
                # RHEL / CentOS / Fedora
                $PKG_MGR install -y docker
            fi
        else
            log_info "Docker est déjà installé"
        fi
        
        # Installer Docker Compose (plugin ou standalone)
        if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
            log_info "Installation de Docker Compose..."
            # Essayer d'abord le plugin Docker Compose V2
            if [ "$PKG_MGR" = "dnf" ]; then
                $PKG_MGR install -y docker-compose-plugin || {
                    # Fallback: installer standalone
                    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                    chmod +x /usr/local/bin/docker-compose
                }
            else
                # Fallback: installer standalone
                curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                chmod +x /usr/local/bin/docker-compose
            fi
        else
            log_info "Docker Compose est déjà installé"
        fi
        
        # Installer Certbot
        $PKG_MGR install -y certbot python3-certbot-nginx || pip3 install certbot-nginx || true
    else
        log_error "Distribution non supportée: $OS"
        exit 1
    fi
    
    # Démarrer Docker
    systemctl enable docker
    systemctl start docker || service docker start
    
    # Installer Docker Buildx si nécessaire
    if ! docker buildx version &> /dev/null 2>&1; then
        log_info "Installation de Docker Buildx..."
        BUILDX_VERSION="v0.17.0"
        BUILDX_URL="https://github.com/docker/buildx/releases/download/${BUILDX_VERSION}/buildx-${BUILDX_VERSION}.linux-amd64"
        
        # Installer pour root (car on exécute avec sudo)
        mkdir -p /root/.docker/cli-plugins
        curl -L "$BUILDX_URL" -o /root/.docker/cli-plugins/docker-buildx
        chmod +x /root/.docker/cli-plugins/docker-buildx
        
        # Si exécuté avec sudo, installer aussi pour l'utilisateur sudo
        if [ -n "$SUDO_USER" ]; then
            SUDO_HOME=$(eval echo ~$SUDO_USER)
            mkdir -p "$SUDO_HOME/.docker/cli-plugins"
            curl -L "$BUILDX_URL" -o "$SUDO_HOME/.docker/cli-plugins/docker-buildx"
            chmod +x "$SUDO_HOME/.docker/cli-plugins/docker-buildx"
            chown -R "$SUDO_USER:$SUDO_USER" "$SUDO_HOME/.docker"
        fi
        
        # Attendre un peu que Docker soit prêt
        sleep 2
        
        # Créer une instance buildx
        docker buildx create --use --name builder 2>/dev/null || true
        docker buildx inspect --bootstrap 2>/dev/null || true
    else
        log_info "Docker Buildx est déjà installé"
        # S'assurer qu'une instance buildx est créée
        docker buildx create --use --name builder 2>/dev/null || true
    fi
    
    # Ajouter l'utilisateur actuel au groupe docker (pour éviter sudo)
    if [ -n "$SUDO_USER" ]; then
        usermod -aG docker "$SUDO_USER"
        log_info "Utilisateur $SUDO_USER ajouté au groupe docker"
    elif [ -n "$USER" ] && [ "$USER" != "root" ]; then
        usermod -aG docker "$USER"
        log_info "Utilisateur $USER ajouté au groupe docker"
    fi
    
    log_success "Docker installé"
}

clone_or_update_repo() {
    log_info "Téléchargement/mise à jour du code..."
    
    if [ -d "$DEPLOY_DIR" ]; then
        cd "$DEPLOY_DIR"
        git fetch origin
        git checkout "$BRANCH"
        git pull origin "$BRANCH"
    else
        mkdir -p "$DEPLOY_DIR"
        git clone -b "$BRANCH" "$REPO_URL" "$DEPLOY_DIR"
    fi
    
    log_success "Code téléchargé/mis à jour"
}

setup_environment() {
    log_info "Configuration des variables d'environnement..."
    
    cd "$DEPLOY_DIR"
    
    if [ ! -f ".env.docker" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env.docker
            log_warning "⚠️  Éditez $DEPLOY_DIR/.env.docker avec vos configurations!"
        fi
    fi
    
    log_success "Variables d'environnement configurées"
}

configure_nginx() {
    log_info "Configuration de Nginx..."
    
    # Détecter la distribution pour le chemin Nginx
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    fi
    
    # Chemin selon la distribution
    if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ] || [ "$OS" = "fedora" ]; then
        # Amazon Linux / RHEL / CentOS
        NGINX_CONF="/etc/nginx/conf.d/gaztracker.conf"
    else
        # Ubuntu / Debian
        NGINX_CONF="/etc/nginx/sites-available/gaztracker"
    fi
    
    cat > "$NGINX_CONF" <<'EOF'
server {
    listen 80;
    server_name _;
    
    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
    
    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF
    
    # Activer le site selon la distribution
    if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ] || [ "$OS" = "fedora" ]; then
        # Amazon Linux / RHEL / CentOS - pas besoin de lien symbolique
        # Supprimer la config par défaut si elle existe
        rm -f /etc/nginx/conf.d/default.conf
    else
        # Ubuntu / Debian
        ln -sf /etc/nginx/sites-available/gaztracker /etc/nginx/sites-enabled/
        rm -f /etc/nginx/sites-enabled/default
    fi
    
    # Tester et redémarrer Nginx
    nginx -t
    systemctl enable nginx
    systemctl restart nginx || service nginx restart
    
    log_success "Nginx configuré"
}

deploy_with_docker() {
    log_info "Déploiement avec Docker Compose..."
    
    cd "$DEPLOY_DIR"
    
    # Détecter la commande Docker Compose disponible
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
        log_info "Utilisation de Docker Compose V2 (plugin)"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
        log_info "Utilisation de Docker Compose V1 (standalone)"
    else
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    # Arrêter les conteneurs existants
    $DOCKER_COMPOSE_CMD down || true
    
    # Construire et démarrer
    $DOCKER_COMPOSE_CMD up -d --build
    
    # Attendre que les services soient prêts
    log_info "Attente du démarrage des services..."
    sleep 10
    
    # Vérifier le statut
    $DOCKER_COMPOSE_CMD ps
    
    log_success "Déploiement Docker terminé"
}

create_docker_service() {
    log_info "Création du service systemd pour Docker Compose..."
    
    # Détecter la commande Docker Compose disponible
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
        EXEC_START="/usr/bin/docker compose up -d"
        EXEC_STOP="/usr/bin/docker compose down"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
        DOCKER_COMPOSE_PATH=$(which docker-compose)
        EXEC_START="$DOCKER_COMPOSE_PATH up -d"
        EXEC_STOP="$DOCKER_COMPOSE_PATH down"
    else
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    cat > "/etc/systemd/system/gaztracker-docker.service" <<EOF
[Unit]
Description=GazTracker Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$DEPLOY_DIR
ExecStart=$EXEC_START
ExecStop=$EXEC_STOP
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable gaztracker-docker
    
    log_success "Service Docker créé"
}

main() {
    log_info "=========================================="
    log_info "  Déploiement GazTracker (Docker) sur EC2"
    log_info "=========================================="
    echo ""
    
    check_root
    install_docker
    clone_or_update_repo
    setup_environment
    configure_nginx
    create_docker_service
    deploy_with_docker
    
    log_success "=========================================="
    log_success "  Déploiement terminé!"
    log_success "=========================================="
    echo ""
    echo "📍 Répertoire: $DEPLOY_DIR"
    echo "🔗 URLs:"
    echo "  - API: http://$(curl -s ifconfig.me)/api/v1"
    echo "  - Docs: http://$(curl -s ifconfig.me)/docs"
    echo "  - Frontend: http://$(curl -s ifconfig.me)/"
    echo ""
    echo "📋 Commandes:"
    echo "  - Logs: cd $DEPLOY_DIR && docker-compose logs -f (ou docker compose logs -f)"
    echo "  - Redémarrer: cd $DEPLOY_DIR && docker-compose restart (ou docker compose restart)"
    echo "  - Arrêter: cd $DEPLOY_DIR && docker-compose down (ou docker compose down)"
    echo ""
    echo "⚠️  Note: Si vous utilisez Docker Compose V2, remplacez 'docker-compose' par 'docker compose'"
    echo ""
}

main "$@"

