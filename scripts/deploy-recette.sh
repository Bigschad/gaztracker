#!/bin/bash
# =============================================================================
# Script de déploiement pour l'environnement de recette
# =============================================================================

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonctions de logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    log_error "Docker n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier que Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier que le fichier .env.recette existe
if [ ! -f ".env.recette" ]; then
    log_warning "Le fichier .env.recette n'existe pas."
    log_info "Création d'un fichier .env.recette depuis le template..."
    
    if [ -f ".env.example" ]; then
        cp .env.example .env.recette
        log_warning "⚠️  IMPORTANT: Modifiez le fichier .env.recette avec vos configurations avant de continuer!"
        log_warning "   Notamment: POSTGRES_PASSWORD, REDIS_PASSWORD, SECRET_KEY"
        exit 1
    else
        log_error "Aucun fichier .env.example trouvé. Créez manuellement .env.recette"
        exit 1
    fi
fi

# Fonction pour démarrer les services
start_services() {
    log_info "Démarrage des services de recette..."
    
    if [ "$1" == "--with-tools" ]; then
        log_info "Démarrage avec PgAdmin (outils de gestion)..."
        docker-compose -f docker-compose.recette.yml --profile tools up -d
    else
        docker-compose -f docker-compose.recette.yml up -d
    fi
    
    log_info "Attente du démarrage des services..."
    sleep 5
    
    log_info "État des services:"
    docker-compose -f docker-compose.recette.yml ps
}

# Fonction pour arrêter les services
stop_services() {
    log_info "Arrêt des services de recette..."
    docker-compose -f docker-compose.recette.yml down
}

# Fonction pour voir les logs
show_logs() {
    if [ -n "$1" ]; then
        docker-compose -f docker-compose.recette.yml logs -f "$1"
    else
        docker-compose -f docker-compose.recette.yml logs -f
    fi
}

# Fonction pour reconstruire les images
rebuild() {
    log_info "Reconstruction des images..."
    docker-compose -f docker-compose.recette.yml build --no-cache
    
    if [ "$1" == "--restart" ]; then
        log_info "Redémarrage des services..."
        docker-compose -f docker-compose.recette.yml up -d
    fi
}

# Fonction pour exécuter les migrations
run_migrations() {
    log_info "Exécution des migrations de base de données..."
    docker-compose -f docker-compose.recette.yml exec app alembic upgrade head
}

# Fonction pour vérifier la santé des services
health_check() {
    log_info "Vérification de la santé des services..."
    
    echo ""
    log_info "Backend API:"
    if curl -s http://localhost:8001/health > /dev/null; then
        echo -e "${GREEN}✓${NC} Backend API est accessible"
    else
        echo -e "${RED}✗${NC} Backend API n'est pas accessible"
    fi
    
    echo ""
    log_info "PostgreSQL:"
    if docker-compose -f docker-compose.recette.yml exec -T postgres pg_isready -U gaztracker_user > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} PostgreSQL est prêt"
    else
        echo -e "${RED}✗${NC} PostgreSQL n'est pas prêt"
    fi
    
    echo ""
    log_info "Redis:"
    if docker-compose -f docker-compose.recette.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Redis est prêt"
    else
        echo -e "${RED}✗${NC} Redis n'est pas prêt"
    fi
}

# Fonction pour afficher l'aide
show_help() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commandes disponibles:"
    echo "  start [--with-tools]    Démarrer les services (--with-tools pour inclure PgAdmin)"
    echo "  stop                    Arrêter les services"
    echo "  restart                 Redémarrer les services"
    echo "  logs [service]          Afficher les logs (optionnel: nom du service)"
    echo "  rebuild [--restart]     Reconstruire les images (--restart pour redémarrer après)"
    echo "  migrate                 Exécuter les migrations de base de données"
    echo "  health                  Vérifier la santé des services"
    echo "  status                  Afficher l'état des services"
    echo "  help                    Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0 start                Démarrer les services"
    echo "  $0 start --with-tools   Démarrer avec PgAdmin"
    echo "  $0 logs app             Voir les logs du backend"
    echo "  $0 rebuild --restart    Reconstruire et redémarrer"
}

# Gestion des commandes
case "${1:-help}" in
    start)
        start_services "$2"
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_services "$2"
        ;;
    logs)
        show_logs "$2"
        ;;
    rebuild)
        rebuild "$2"
        ;;
    migrate)
        run_migrations
        ;;
    health)
        health_check
        ;;
    status)
        docker-compose -f docker-compose.recette.yml ps
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Commande inconnue: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

