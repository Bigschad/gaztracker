# 🚀 Déploiement en Recette (Staging) - GazTracker

Ce guide explique comment déployer GazTracker en environnement de recette avec Docker Compose.

## 📋 Prérequis

- Docker et Docker Compose installés
- Accès au dépôt du projet
- Variables d'environnement configurées

## 🔧 Configuration

### 1. Créer le fichier `.env.recette`

Créez un fichier `.env.recette` à la racine du projet avec les variables suivantes :

```env
# Application
APP_NAME=GazTracker
APP_ENVIRONMENT=staging
DEBUG=False

# Database PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=gaztracker_db_recette
POSTGRES_USER=gaztracker_user
POSTGRES_PASSWORD=VOTRE_MOT_DE_PASSE_SECURISE

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=VOTRE_MOT_DE_PASSE_REDIS

# JWT & Security
SECRET_KEY=$(openssl rand -hex 32)  # Générer une clé secrète de 32+ caractères
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080

# CORS - Ajoutez vos domaines de recette
ALLOWED_ORIGINS=http://localhost:3001,https://recette.gaztracker.com

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Frontend API URL
VITE_API_URL=http://localhost:8001

# PgAdmin (optionnel)
PGADMIN_EMAIL=admin@gaztracker.recette
PGADMIN_PASSWORD=VOTRE_MOT_DE_PASSE_PGADMIN
```

### 2. Générer une clé secrète JWT

```bash
# Linux/Mac
openssl rand -hex 32

# Windows PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

## 🚀 Déploiement

### Démarrer tous les services

```bash
docker-compose -f docker-compose.recette.yml up -d
```

### Démarrer avec PgAdmin (outils de gestion)

```bash
docker-compose -f docker-compose.recette.yml --profile tools up -d
```

### Vérifier l'état des services

```bash
docker-compose -f docker-compose.recette.yml ps
```

### Voir les logs

```bash
# Tous les services
docker-compose -f docker-compose.recette.yml logs -f

# Un service spécifique
docker-compose -f docker-compose.recette.yml logs -f app
docker-compose -f docker-compose.recette.yml logs -f postgres
```

## 🔄 Migrations de base de données

Les migrations Alembic s'exécutent automatiquement au démarrage via le script `docker-entrypoint.sh`.

Pour exécuter manuellement :

```bash
docker-compose -f docker-compose.recette.yml exec app alembic upgrade head
```

## 📊 Accès aux services

| Service | URL | Port |
|---------|-----|------|
| Backend API | http://localhost:8001 | 8001 |
| Frontend | http://localhost:3001 | 3001 |
| PostgreSQL | localhost:5433 | 5433 |
| Redis | localhost:6380 | 6380 |
| PgAdmin | http://localhost:5051 | 5051 |

## 🔒 Sécurité

### Mots de passe

⚠️ **IMPORTANT** : Changez tous les mots de passe par défaut dans `.env.recette` :
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `SECRET_KEY`
- `PGADMIN_PASSWORD`

### Connexion PostgreSQL

```bash
docker-compose -f docker-compose.recette.yml exec postgres psql -U gaztracker_user -d gaztracker_db_recette
```

### Connexion Redis

```bash
docker-compose -f docker-compose.recette.yml exec redis redis-cli -a VOTRE_MOT_DE_PASSE_REDIS
```

## 🛠️ Maintenance

### Arrêter les services

```bash
docker-compose -f docker-compose.recette.yml down
```

### Arrêter et supprimer les volumes (⚠️ supprime les données)

```bash
docker-compose -f docker-compose.recette.yml down -v
```

### Reconstruire les images

```bash
docker-compose -f docker-compose.recette.yml build --no-cache
```

### Redémarrer un service spécifique

```bash
docker-compose -f docker-compose.recette.yml restart app
```

## 📦 Sauvegardes

### Sauvegarde PostgreSQL

```bash
# Créer une sauvegarde
docker-compose -f docker-compose.recette.yml exec postgres pg_dump -U gaztracker_user gaztracker_db_recette > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurer une sauvegarde
docker-compose -f docker-compose.recette.yml exec -T postgres psql -U gaztracker_user gaztracker_db_recette < backup.sql
```

## 🐛 Dépannage

### Vérifier les logs d'erreur

```bash
docker-compose -f docker-compose.recette.yml logs --tail=100 app
```

### Vérifier la santé des services

```bash
# Backend
curl http://localhost:8001/health

# PostgreSQL
docker-compose -f docker-compose.recette.yml exec postgres pg_isready -U gaztracker_user

# Redis
docker-compose -f docker-compose.recette.yml exec redis redis-cli ping
```

### Problème de connexion à PostgreSQL

Si l'application ne peut pas se connecter à PostgreSQL :

1. Vérifiez que PostgreSQL est démarré :
   ```bash
   docker-compose -f docker-compose.recette.yml ps postgres
   ```

2. Vérifiez les variables d'environnement dans `.env.recette`

3. Vérifiez les logs PostgreSQL :
   ```bash
   docker-compose -f docker-compose.recette.yml logs postgres
   ```

### Réinitialiser l'environnement

```bash
# Arrêter et supprimer tout
docker-compose -f docker-compose.recette.yml down -v

# Redémarrer
docker-compose -f docker-compose.recette.yml up -d
```

## 📝 Différences avec l'environnement de développement

| Aspect | Développement | Recette |
|--------|---------------|---------|
| Ports | 8000, 3000, 5432, 6379 | 8001, 3001, 5433, 6380 |
| Volumes de code | Montés (hot-reload) | Intégrés dans l'image |
| Debug | Activé | Désactivé |
| Logging | Text | JSON |
| Ressources | Illimitées | Limitées |
| PgAdmin | Toujours actif | Optionnel (profile) |

## 🔄 Mise à jour

Pour mettre à jour l'application :

```bash
# 1. Récupérer les dernières modifications
git pull

# 2. Reconstruire les images
docker-compose -f docker-compose.recette.yml build

# 3. Redémarrer les services
docker-compose -f docker-compose.recette.yml up -d

# 4. Vérifier les migrations
docker-compose -f docker-compose.recette.yml exec app alembic upgrade head
```

## 📞 Support

En cas de problème :
1. Vérifiez les logs : `docker-compose -f docker-compose.recette.yml logs`
2. Vérifiez la configuration dans `.env.recette`
3. Vérifiez que tous les services sont "healthy" : `docker-compose -f docker-compose.recette.yml ps`

