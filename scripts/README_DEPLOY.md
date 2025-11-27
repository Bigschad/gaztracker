# 🚀 Guide de Déploiement sur EC2

Ce guide explique comment déployer automatiquement GazTracker sur un serveur EC2.

## 📋 Prérequis

- Instance EC2 Ubuntu 20.04+ ou Amazon Linux 2
- Accès SSH à l'instance
- Accès root ou sudo
- Ports ouverts dans le Security Group EC2 :
  - Port 22 (SSH)
  - Port 80 (HTTP)
  - Port 443 (HTTPS - optionnel)
  - Port 8000 (Backend API - optionnel, si accès direct)

## 🎯 Méthode 1 : Déploiement avec Services Systemd (Recommandé)

### Étapes

1. **Se connecter à l'instance EC2**
```bash
ssh -i votre-cle.pem ubuntu@votre-ip-ec2
```

2. **Télécharger le script de déploiement**
```bash
# Option 1: Cloner le repo et exécuter le script
git clone https://github.com/Bigschad/gaztracker.git
cd gaztracker/scripts
chmod +x deploy-ec2.sh

# Option 2: Télécharger directement le script
curl -O https://raw.githubusercontent.com/Bigschad/gaztracker/develop/scripts/deploy-ec2.sh
chmod +x deploy-ec2.sh
```

3. **Exécuter le script de déploiement**
```bash
sudo ./deploy-ec2.sh
```

Le script va :
- ✅ Installer toutes les dépendances système
- ✅ Cloner/mettre à jour le code depuis GitHub
- ✅ Configurer Python et Node.js
- ✅ Installer les dépendances backend et frontend
- ✅ Configurer PostgreSQL et Redis
- ✅ Exécuter les migrations de base de données
- ✅ Créer les services systemd
- ✅ Configurer Nginx
- ✅ Démarrer tous les services

4. **Configurer les variables d'environnement**
```bash
sudo nano /opt/gaztracker/.env
```

Éditez les variables importantes :
- `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `SECRET_KEY` (générer avec `openssl rand -hex 32`)
- `REDIS_HOST`, `REDIS_PORT`
- `APP_ENVIRONMENT=production`

5. **Redémarrer les services**
```bash
sudo systemctl restart gaztracker-backend
sudo systemctl restart nginx
```

## 🐳 Méthode 2 : Déploiement avec Docker (Alternative)

### Étapes

1. **Télécharger et exécuter le script Docker**
```bash
curl -O https://raw.githubusercontent.com/Bigschad/gaztracker/develop/scripts/deploy-ec2-docker.sh
chmod +x deploy-ec2-docker.sh
sudo ./deploy-ec2-docker.sh
```

2. **Configurer les variables d'environnement**
```bash
sudo nano /opt/gaztracker/.env.docker
```

3. **Redémarrer les conteneurs**
```bash
cd /opt/gaztracker
sudo docker-compose restart
```

## ⚙️ Configuration Post-Déploiement

### 1. Configurer HTTPS avec Let's Encrypt

```bash
sudo certbot --nginx -d votre-domaine.com
```

### 2. Configurer le pare-feu EC2

Dans la console AWS EC2 :
1. Sélectionnez votre instance
2. Security Groups → Edit inbound rules
3. Ajoutez :
   - Port 80 (HTTP) depuis 0.0.0.0/0
   - Port 443 (HTTPS) depuis 0.0.0.0/0

### 3. Vérifier les services

```bash
# Statut du backend
sudo systemctl status gaztracker-backend

# Logs du backend
sudo journalctl -u gaztracker-backend -f

# Statut de Nginx
sudo systemctl status nginx

# Logs Nginx
sudo tail -f /var/log/nginx/error.log
```

## 🔄 Mise à jour

Pour mettre à jour l'application :

```bash
cd /opt/gaztracker
sudo -u gaztracker git pull origin develop
sudo systemctl restart gaztracker-backend
```

## 📊 Commandes Utiles

### Services Systemd

```bash
# Démarrer
sudo systemctl start gaztracker-backend

# Arrêter
sudo systemctl stop gaztracker-backend

# Redémarrer
sudo systemctl restart gaztracker-backend

# Statut
sudo systemctl status gaztracker-backend

# Logs
sudo journalctl -u gaztracker-backend -f
```

### Docker Compose

```bash
cd /opt/gaztracker

# Démarrer
sudo docker-compose up -d

# Arrêter
sudo docker-compose down

# Logs
sudo docker-compose logs -f

# Redémarrer
sudo docker-compose restart
```

### Base de données

```bash
# Migrations
cd /opt/gaztracker
sudo -u gaztracker bash -c "source venv/bin/activate && alembic upgrade head"

# Accès PostgreSQL
sudo -u postgres psql -d gaztracker_db
```

## 🐛 Dépannage

### Le backend ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u gaztracker-backend -n 50

# Vérifier la configuration
sudo -u gaztracker /opt/gaztracker/venv/bin/python -c "from app.main import app"
```

### Nginx ne fonctionne pas

```bash
# Tester la configuration
sudo nginx -t

# Vérifier les logs
sudo tail -f /var/log/nginx/error.log
```

### Problèmes de permissions

```bash
# Corriger les permissions
sudo chown -R gaztracker:gaztracker /opt/gaztracker
```

## 📝 Variables d'Environnement Importantes

Assurez-vous de configurer ces variables dans `/opt/gaztracker/.env` :

```env
# Application
APP_ENVIRONMENT=production
DEBUG=False

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=gaztracker_db
POSTGRES_USER=gaztracker_user
POSTGRES_PASSWORD=votre_mot_de_passe_securise

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
SECRET_KEY=votre_cle_secrete_32_caracteres_minimum
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080
```

## 🔒 Sécurité

1. **Ne jamais commiter le fichier .env**
2. **Utiliser des mots de passe forts**
3. **Configurer HTTPS en production**
4. **Limiter l'accès SSH aux IPs autorisées**
5. **Configurer un pare-feu (UFW) sur l'instance**

```bash
# Exemple de configuration UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 📞 Support

En cas de problème, vérifiez :
1. Les logs des services
2. La configuration des variables d'environnement
3. Les permissions des fichiers
4. La connectivité réseau (ports ouverts)

