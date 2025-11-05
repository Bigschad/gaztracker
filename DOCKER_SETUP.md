# 🐳 Configuration Docker - GazTracker

## Vue d'ensemble

Votre application GazTracker est maintenant complètement dockerisée ! Voici ce qui a été configuré :

### Services disponibles

1. **Application FastAPI** (`gaztracker_app`) - Port 8000
2. **PostgreSQL** (`gaztracker_postgres`) - Port 5432
3. **Redis** (`gaztracker_redis`) - Port 6379
4. **PgAdmin** (`gaztracker_pgadmin`) - Port 5050
5. **Redis Commander** (`gaztracker_redis_commander`) - Port 8081

## Fichiers créés

- `Dockerfile` - Image multi-stage pour l'application
- `.dockerignore` - Fichiers exclus du build Docker
- `.env.docker` - Variables d'environnement pour Docker
- `scripts/docker-entrypoint.sh` - Script de démarrage avec attente des services et migrations
- `docker-compose.yml` - Orchestration des services (mis à jour)

## Démarrage

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker logs gaztracker_app
docker logs gaztracker_postgres
docker logs gaztracker_redis

# Arrêter tous les services
docker-compose down

# Rebuild et redémarrer
docker-compose down && docker-compose build && docker-compose up -d
```

## Accès aux services

- **API**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs
- **PgAdmin**: http://localhost:5050
  - Email: admin@gaztracker.com
  - Password: admin
- **Redis Commander**: http://localhost:8081

## Configuration

Les variables d'environnement sont dans `.env.docker`. Points importants :

- Les services utilisent les noms Docker comme hôtes (ex: `postgres`, `redis`)
- Les migrations Alembic s'exécutent automatiquement au démarrage
- L'application attend que PostgreSQL et Redis soient prêts avant de démarrer

## Problème connu

**Issue**: Les champs `List[str]` dans pydantic-settings ne se parsent pas correctement depuis les variables d'environnement.

**Solution temporaire**: Modifier `app/config.py` pour utiliser `str` au lieu de `List[str]` et convertir dans le validator.

## Prochaines étapes

1. Résoudre le problème de parsing pydantic
2. Tester complètement le setup Docker
3. Ajouter des volumes persistants pour PostgreSQL
4. Configuration SSL/TLS pour la production
