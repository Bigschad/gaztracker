# 🚀 Déploiement Production (Branche dev)

## Vue d'ensemble

La branche `dev` est configurée pour le déploiement en production avec des fichiers `.env` séparés pour chaque service. La branche `develop` reste pour le développement local.

## Architecture des configurations

```
gaztracker/
├── docker-compose.yml           # Pour develop (local)
├── docker-compose.prod.yml      # Pour dev (production)
├── .env.app.example             # Config backend (à copier)
├── .env.db.example              # Config PostgreSQL (à copier)
├── .env.redis.example           # Config Redis (à copier)
├── .env.frontend.example        # Config frontend (à copier)
└── .env.docker                  # Config legacy (develop seulement)
```

## 📋 Prérequis Lightsail

### 1. Créer une instance Lightsail

- **OS**: Ubuntu 22.04 LTS ou plus récent
- **Plan**: Au minimum 2 GB RAM, 1 vCPU, 60 GB SSD
- **Ouvrir les ports**:
  - 22 (SSH)
  - 80 (HTTP)
  - 443 (HTTPS)
  - 8000 (Backend API)
  - 3000 (Frontend)

### 2. Connectez-vous à votre instance

```bash
ssh ubuntu@VOTRE_IP_LIGHTSAIL
```

### 3. Installation initiale

```bash
# Mise à jour du système
sudo apt-get update && sudo apt-get upgrade -y

# Installation de Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Installation de Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Installation de Git
sudo apt-get install -y git

# Déconnexion/reconnexion pour appliquer les permissions Docker
exit
```

Reconnectez-vous:
```bash
ssh ubuntu@VOTRE_IP_LIGHTSAIL
```

### 4. Cloner le dépôt

```bash
# Créer le répertoire de déploiement
sudo mkdir -p /opt/gaztracker
sudo chown -R $USER:$USER /opt/gaztracker

# Cloner le projet
cd /opt/gaztracker
git clone https://github.com/Bigschad/gaztracker.git .
git checkout dev
```

### 5. Configurer les variables d'environnement

```bash
cd /opt/gaztracker

# Copier les fichiers exemples
cp .env.app.example .env.app
cp .env.db.example .env.db
cp .env.redis.example .env.redis
cp .env.frontend.example .env.frontend

# Éditer chaque fichier avec vos valeurs
nano .env.app
nano .env.db
nano .env.redis
nano .env.frontend
```

#### Configuration `.env.db`

```env
POSTGRES_USER=gaztracker_user
POSTGRES_PASSWORD=VOTRE_MOT_DE_PASSE_SECURISE
POSTGRES_DB=gaztracker_db
POSTGRES_PORT=5432
```

#### Configuration `.env.redis`

```env
REDIS_PASSWORD=VOTRE_MOT_DE_PASSE_REDIS_SECURISE
REDIS_PORT=6379
```

#### Configuration `.env.app`

```env
# Database
DATABASE_URL=postgresql+asyncpg://gaztracker_user:VOTRE_MOT_DE_PASSE_SECURISE@postgres:5432/gaztracker_db

# Redis
REDIS_URL=redis://:VOTRE_MOT_DE_PASSE_REDIS_SECURISE@redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Application
SECRET_KEY=GENERER_AVEC_openssl_rand_-hex_32
ENVIRONMENT=production
DEBUG=False

# CORS
ALLOWED_ORIGINS=http://VOTRE_IP:3000,http://VOTRE_DOMAINE,https://VOTRE_DOMAINE
ALLOW_CREDENTIALS=True

# JWT
JWT_SECRET_KEY=GENERER_AVEC_openssl_rand_-hex_32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=30

# Admin User
ADMIN_EMAIL=admin@gaztracker.com
ADMIN_PASSWORD=VOTRE_MOT_DE_PASSE_ADMIN
ADMIN_FIRST_NAME=System
ADMIN_LAST_NAME=Administrator

# API
API_V1_PREFIX=/api/v1
API_PORT=8000

# File Upload
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=/app/uploads

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

#### Configuration `.env.frontend`

```env
VITE_API_URL=http://VOTRE_IP:8000
FRONTEND_PORT=3000
```

### 6. Générer les secrets

```bash
# Générer SECRET_KEY
openssl rand -hex 32

# Générer JWT_SECRET_KEY
openssl rand -hex 32

# Générer un mot de passe fort
openssl rand -base64 32
```

### 7. Créer les répertoires nécessaires

```bash
cd /opt/gaztracker
mkdir -p uploads/logos logs
sudo chown -R 1000:1000 uploads logs
```

### 8. Démarrer les services

```bash
cd /opt/gaztracker

# Build et démarrage
docker-compose -f docker-compose.prod.yml up -d --build

# Vérifier les logs
docker-compose -f docker-compose.prod.yml logs -f

# Vérifier le statut
docker-compose -f docker-compose.prod.yml ps
```

### 9. Accéder à l'application

- **Frontend**: http://VOTRE_IP:3000
- **Backend API**: http://VOTRE_IP:8000/docs
- **Connexion**: admin@gaztracker.com / VOTRE_MOT_DE_PASSE_ADMIN

## 🔄 GitHub Actions - Déploiement Automatique

### Configuration des secrets GitHub

Allez sur: https://github.com/Bigschad/gaztracker/settings/secrets/actions

Ajoutez ces secrets:

1. **LIGHTSAIL_SSH_KEY**
   ```bash
   # Sur votre PC local
   ssh-keygen -t ed25519 -C "github-actions-gaztracker" -f ~/.ssh/lightsail_deploy
   # (Pas de passphrase)
   
   # Afficher la clé PRIVÉE (pour GitHub)
   cat ~/.ssh/lightsail_deploy
   
   # Afficher la clé PUBLIQUE (pour Lightsail)
   cat ~/.ssh/lightsail_deploy.pub
   ```
   
   Sur le serveur Lightsail:
   ```bash
   echo "COLLER_CLE_PUBLIQUE_ICI" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

2. **LIGHTSAIL_HOST**
   ```
   VOTRE_IP_LIGHTSAIL
   ```

3. **LIGHTSAIL_USER**
   ```
   ubuntu
   ```

### Test de connexion SSH

Sur votre PC:
```bash
ssh -i ~/.ssh/lightsail_deploy ubuntu@VOTRE_IP
```

### Déploiement automatique

```bash
# Depuis votre PC
git add .
git commit -m "Configuration production"
git push origin dev
```

Le workflow GitHub Actions se déclenche automatiquement et déploie sur Lightsail.

## 🔍 Commandes utiles

### Vérifier les logs

```bash
# Tous les services
docker-compose -f docker-compose.prod.yml logs -f

# Service spécifique
docker-compose -f docker-compose.prod.yml logs -f app
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Redémarrer un service

```bash
docker-compose -f docker-compose.prod.yml restart app
docker-compose -f docker-compose.prod.yml restart frontend
```

### Mettre à jour manuellement

```bash
cd /opt/gaztracker
git pull origin dev
docker-compose -f docker-compose.prod.yml up -d --build
```

### Sauvegarder la base de données

```bash
docker exec gaztracker_postgres pg_dump -U gaztracker_user gaztracker_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restaurer la base de données

```bash
cat backup_YYYYMMDD_HHMMSS.sql | docker exec -i gaztracker_postgres psql -U gaztracker_user -d gaztracker_db
```

## 🛡️ Sécurité

### Configurer le pare-feu UFW

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 3000/tcp
sudo ufw enable
sudo ufw status
```

### Configurer Nginx (optionnel)

```bash
sudo apt-get install -y nginx

sudo nano /etc/nginx/sites-available/gaztracker
```

Configuration Nginx:
```nginx
server {
    listen 80;
    server_name VOTRE_DOMAINE;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Activer:
```bash
sudo ln -s /etc/nginx/sites-available/gaztracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Configurer SSL avec Certbot (optionnel)

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d VOTRE_DOMAINE
```

## 🔙 Retour au développement local

Sur votre PC:
```bash
git checkout develop
docker-compose down
docker-compose up -d --build
```

## 📊 Monitoring

### Vérifier l'utilisation des ressources

```bash
docker stats
```

### Vérifier l'espace disque

```bash
df -h
docker system df
```

### Nettoyer Docker

```bash
docker system prune -a --volumes
```

## 🆘 Dépannage

### Erreur de connexion à la base de données

```bash
# Vérifier les logs PostgreSQL
docker-compose -f docker-compose.prod.yml logs postgres

# Redémarrer PostgreSQL
docker-compose -f docker-compose.prod.yml restart postgres
```

### Erreur CORS

Vérifiez `ALLOWED_ORIGINS` dans `.env.app`

### Port déjà utilisé

```bash
# Vérifier quel processus utilise le port
sudo lsof -i :8000
sudo lsof -i :3000

# Arrêter tous les containers
docker-compose -f docker-compose.prod.yml down
```

## 📝 Notes importantes

1. **Ne jamais commiter les fichiers `.env.*`** (sauf `.example`)
2. **Sauvegarder régulièrement** la base de données
3. **Tester en local** avant de pousser sur `dev`
4. **Monitorer les logs** après chaque déploiement
5. **Garder Docker à jour**: `sudo apt-get update && sudo apt-get upgrade docker-ce`

## 📞 Support

En cas de problème, vérifiez:
1. Les logs: `docker-compose -f docker-compose.prod.yml logs -f`
2. Les variables d'environnement: `cat .env.app`
3. L'état des containers: `docker-compose -f docker-compose.prod.yml ps`
4. Les workflows GitHub Actions: https://github.com/Bigschad/gaztracker/actions

