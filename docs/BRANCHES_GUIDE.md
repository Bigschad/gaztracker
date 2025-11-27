# 🌿 Guide des branches GazTracker

## 📊 Vue d'ensemble

GazTracker utilise **2 branches principales** avec des configurations différentes :

```
main (stable)
  │
  ├── develop (développement local) ← Vous êtes ici actuellement
  │   ├── docker-compose.yml
  │   └── .env.docker
  │
  └── dev (production Lightsail)
      ├── docker-compose.prod.yml
      └── .env.app, .env.db, .env.redis, .env.frontend
```

## 🔀 Comparaison des branches

| Aspect | `develop` | `dev` |
|--------|-----------|-------|
| **Usage** | Développement local | Production Lightsail |
| **Docker Compose** | `docker-compose.yml` | `docker-compose.prod.yml` |
| **Variables d'environnement** | `.env.docker` (1 fichier) | `.env.app`, `.env.db`, `.env.redis`, `.env.frontend` (4 fichiers) |
| **Commande démarrage** | `docker-compose up -d` | `docker-compose -f docker-compose.prod.yml up -d` |
| **Debug** | ✅ Activé | ❌ Désactivé |
| **Hot reload** | ✅ Oui (volumes montés) | ❌ Non |
| **GitHub Actions** | ❌ Pas de déploiement | ✅ Déploiement automatique |
| **CORS** | `localhost:3000` | IP publique Lightsail |
| **Logs** | Console + fichiers | Fichiers uniquement |
| **Base de données** | Volume local | Volume persistant serveur |

## 🚀 Commandes rapides

### Sur la branche `develop` (développement local)

```bash
# Basculer sur develop
git checkout develop

# Démarrer l'application
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Reconstruire après des changements
docker-compose up -d --build

# Arrêter
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

### Sur la branche `dev` (production)

```bash
# Basculer sur dev
git checkout dev

# Sur le serveur Lightsail
docker-compose -f docker-compose.prod.yml up -d --build

# Voir les logs
docker-compose -f docker-compose.prod.yml logs -f

# Redémarrer un service
docker-compose -f docker-compose.prod.yml restart app

# Arrêter
docker-compose -f docker-compose.prod.yml down
```

## 📝 Workflow de développement

### 1. Développement local (branche `develop`)

```bash
# 1. S'assurer d'être sur develop
git checkout develop

# 2. Démarrer l'environnement local
docker-compose up -d

# 3. Développer et tester
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs

# 4. Commiter les changements
git add .
git commit -m "feat: nouvelle fonctionnalité"

# 5. Pousser sur develop
git push origin develop
```

### 2. Déploiement en production (branche `dev`)

#### Option A : Merge de develop vers dev

```bash
# 1. S'assurer que develop est à jour
git checkout develop
git pull origin develop

# 2. Basculer sur dev
git checkout dev

# 3. Merger develop dans dev
git merge develop

# 4. Pousser sur dev
git push origin dev
```

→ **GitHub Actions déploie automatiquement sur Lightsail**

#### Option B : Développement direct sur dev (urgent)

```bash
# 1. Basculer sur dev
git checkout dev

# 2. Faire les modifications nécessaires

# 3. Commiter et pousser
git add .
git commit -m "hotfix: correction urgente"
git push origin dev
```

→ **GitHub Actions déploie automatiquement**

#### Option C : Déploiement manuel sur Lightsail

```bash
# Sur le serveur Lightsail
ssh ubuntu@VOTRE_IP

cd /opt/gaztracker
git pull origin dev
docker-compose -f docker-compose.prod.yml up -d --build
```

## 🔧 Configuration des environnements

### Configuration `develop` (local)

Fichier `.env.docker` :

```env
# Database
DATABASE_URL=postgresql+asyncpg://gaztracker_user:gaztracker_pass_dev@postgres:5432/gaztracker_db

# Redis
REDIS_URL=redis://redis:6379/0

# Application
SECRET_KEY=dev-secret-key
ENVIRONMENT=development
DEBUG=True

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Admin
ADMIN_EMAIL=admin@gaztracker.com
ADMIN_PASSWORD=admin123
```

### Configuration `dev` (production)

**4 fichiers séparés** :

#### `.env.app` (Backend)
```env
DATABASE_URL=postgresql+asyncpg://USER:PASS@postgres:5432/gaztracker_db
SECRET_KEY=GENERER_AVEC_openssl_rand_hex_32
JWT_SECRET_KEY=GENERER_AVEC_openssl_rand_hex_32
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=http://VOTRE_IP:3000
ADMIN_PASSWORD=MOT_DE_PASSE_SECURISE
```

#### `.env.db` (PostgreSQL)
```env
POSTGRES_USER=gaztracker_user
POSTGRES_PASSWORD=MOT_DE_PASSE_SECURISE
POSTGRES_DB=gaztracker_db
```

#### `.env.redis` (Redis)
```env
REDIS_PASSWORD=MOT_DE_PASSE_REDIS
REDIS_PORT=6379
```

#### `.env.frontend` (React)
```env
VITE_API_URL=http://VOTRE_IP:8000
FRONTEND_PORT=3000
```

## 🔐 Sécurité

### Fichiers à ne JAMAIS commiter

Le `.gitignore` exclut automatiquement :

```gitignore
# Fichiers .env de production
.env.app
.env.db
.env.redis
.env.frontend

# Fichier .env de développement
.env.docker
```

### Générer des secrets sécurisés

```bash
# Secret général (32 caractères hexa = 64 caractères)
openssl rand -hex 32

# Mot de passe fort (base64)
openssl rand -base64 32

# UUID
python -c "import uuid; print(uuid.uuid4())"
```

## 📖 Documentation

### Pour le développement local (`develop`)
- Utilisez `docker-compose.yml`
- Variables dans `.env.docker`
- Hot reload activé

### Pour la production (`dev`)
- **Guides complets** :
  - [`README_DEV_BRANCH.md`](../README_DEV_BRANCH.md) - Guide rapide
  - [`docs/DEPLOYMENT_DEV.md`](DEPLOYMENT_DEV.md) - Guide détaillé
- Utilisez `docker-compose.prod.yml`
- Variables séparées (`.env.app`, `.env.db`, etc.)

## 🔄 Synchronisation des branches

### Merger develop dans dev (mise en production)

```bash
git checkout dev
git merge develop
git push origin dev
```

### Récupérer un hotfix de dev dans develop

```bash
git checkout develop
git cherry-pick <commit-hash-from-dev>
git push origin develop
```

### Voir les différences entre les branches

```bash
git diff develop..dev
```

## 🆘 Dépannage

### Problème : Mauvaises variables d'environnement

```bash
# Sur develop
docker-compose down
# Vérifier .env.docker
docker-compose up -d

# Sur dev (Lightsail)
cd /opt/gaztracker
# Vérifier .env.app, .env.db, .env.redis, .env.frontend
docker-compose -f docker-compose.prod.yml restart
```

### Problème : Conflit lors du merge

```bash
# Annuler le merge
git merge --abort

# Ou résoudre manuellement
git status
# Éditer les fichiers en conflit
git add .
git commit
```

### Problème : J'ai commité un .env par erreur

```bash
# Supprimer du dernier commit (avant push)
git rm --cached .env.app
git commit --amend

# Supprimer de l'historique complet (dangereux!)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env.app' \
  --prune-empty --tag-name-filter cat -- --all
```

## 📊 État actuel

```bash
# Voir sur quelle branche vous êtes
git branch

# Voir les branches distantes
git branch -r

# Voir toutes les branches
git branch -a
```

**Branches actuelles** :
- ✅ `develop` - Développement local (Docker Compose classique)
- ✅ `dev` - Production Lightsail (Docker Compose prod + GitHub Actions)
- 📋 `main` - À venir (production stable)

## 🎯 Résumé

| Tâche | Commande |
|-------|----------|
| Développer localement | `git checkout develop` + `docker-compose up -d` |
| Déployer en production | `git checkout dev` + `git merge develop` + `git push origin dev` |
| Voir les logs locaux | `docker-compose logs -f` |
| Voir les logs production | SSH + `docker-compose -f docker-compose.prod.yml logs -f` |
| Basculer de branche | `git checkout develop` ou `git checkout dev` |

---

**💡 Conseil** : Gardez ce fichier sous la main comme référence rapide !

