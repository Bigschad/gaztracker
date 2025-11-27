# 📌 Branche DEV - Configuration Production

## 🎯 Objectif

Cette branche (`dev`) est configurée spécifiquement pour le **déploiement en production** sur Lightsail avec des fichiers `.env` séparés pour chaque service.

## 🔀 Différences avec develop

| Aspect | `develop` (local) | `dev` (production) |
|--------|-------------------|-------------------|
| **Compose** | `docker-compose.yml` | `docker-compose.prod.yml` |
| **Config** | `.env.docker` | `.env.app`, `.env.db`, `.env.redis`, `.env.frontend` |
| **GitHub Actions** | ❌ | ✅ Auto-déploiement |
| **Debug** | ✅ Activé | ❌ Désactivé |
| **HTTPS** | ❌ | ✅ Recommandé |

## 🚀 Quick Start

### Sur Lightsail

```bash
# 1. Cloner
cd /opt/gaztracker
git clone https://github.com/Bigschad/gaztracker.git .
git checkout dev

# 2. Configurer
cp .env.app.example .env.app
cp .env.db.example .env.db
cp .env.redis.example .env.redis
cp .env.frontend.example .env.frontend

# Éditer avec vos valeurs
nano .env.app
nano .env.db
nano .env.redis
nano .env.frontend

# 3. Démarrer
docker-compose -f docker-compose.prod.yml up -d --build

# 4. Vérifier
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

### Déploiement automatique

```bash
# Sur votre PC
git checkout dev
git add .
git commit -m "Update production"
git push origin dev
```

→ GitHub Actions déploie automatiquement sur Lightsail

## 📁 Structure des fichiers .env

### `.env.app` (Backend)
```env
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/db
SECRET_KEY=...
JWT_SECRET_KEY=...
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=http://YOUR_IP:3000
```

### `.env.db` (PostgreSQL)
```env
POSTGRES_USER=gaztracker_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=gaztracker_db
```

### `.env.redis` (Redis)
```env
REDIS_PASSWORD=secure_redis_pass
REDIS_PORT=6379
```

### `.env.frontend` (React)
```env
VITE_API_URL=http://YOUR_IP:8000
FRONTEND_PORT=3000
```

## 🔐 Secrets GitHub à configurer

Allez sur: https://github.com/Bigschad/gaztracker/settings/secrets/actions

1. **LIGHTSAIL_SSH_KEY** → Clé privée SSH
2. **LIGHTSAIL_HOST** → IP de votre serveur
3. **LIGHTSAIL_USER** → `ubuntu`

## 📖 Documentation complète

Consultez: [`docs/DEPLOYMENT_DEV.md`](docs/DEPLOYMENT_DEV.md)

## ⚠️ Important

1. **NE JAMAIS** commiter les fichiers `.env.*` (sauf `.example`)
2. Les fichiers `.env.*` sont dans `.gitignore`
3. Pour revenir en développement local:
   ```bash
   git checkout develop
   docker-compose up -d --build
   ```

## 🔄 Workflow

```
Local (develop) → Tests → Commit
                           ↓
                    Push to dev
                           ↓
                  GitHub Actions
                           ↓
              Déploiement Lightsail
```

## 🆘 Aide rapide

### Voir les logs
```bash
docker-compose -f docker-compose.prod.yml logs -f app
```

### Redémarrer
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Mettre à jour
```bash
git pull origin dev
docker-compose -f docker-compose.prod.yml up -d --build
```

### Sauvegarder la DB
```bash
docker exec gaztracker_postgres pg_dump -U gaztracker_user gaztracker_db > backup.sql
```

---

**📞 Questions?** Consultez [`docs/DEPLOYMENT_DEV.md`](docs/DEPLOYMENT_DEV.md) pour plus de détails.

