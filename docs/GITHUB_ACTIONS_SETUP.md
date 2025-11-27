# Configuration GitHub Actions pour Lightsail

Guide complet pour configurer le déploiement automatique sur AWS Lightsail.

## 📋 Prérequis

- Un serveur Lightsail avec Ubuntu 20.04 ou supérieur
- Accès SSH au serveur
- Un compte GitHub avec accès au repository

## 🚀 Étape 1 : Configuration du Serveur Lightsail

### 1.1 Connexion au serveur

```bash
ssh ubuntu@VOTRE_IP_LIGHTSAIL
```

### 1.2 Exécution du script d'installation

```bash
# Télécharger le script depuis le repo
curl -O https://raw.githubusercontent.com/Bigschad/gaztracker/develop/scripts/setup-lightsail-server.sh

# Rendre le script exécutable
chmod +x setup-lightsail-server.sh

# Exécuter le script
./setup-lightsail-server.sh
```

### 1.3 Déconnexion et reconnexion

```bash
exit
ssh ubuntu@VOTRE_IP_LIGHTSAIL
```

### 1.4 Configuration des variables d'environnement

```bash
cd /opt/gaztracker
cp .env.template .env
nano .env
```

Modifiez les valeurs suivantes :
- `POSTGRES_PASSWORD` : Mot de passe PostgreSQL
- `SECRET_KEY` : Clé secrète application
- `JWT_SECRET_KEY` : Clé secrète JWT
- `ADMIN_PASSWORD` : Mot de passe admin
- `ALLOWED_ORIGINS` : Votre domaine ou IP

Pour générer des clés sécurisées :
```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
```

## 🔐 Étape 2 : Configuration des Secrets GitHub

### 2.1 Générer une paire de clés SSH (sur votre machine locale)

```bash
ssh-keygen -t ed25519 -C "github-actions-gaztracker" -f ~/.ssh/lightsail_deploy
```

### 2.2 Copier la clé publique sur le serveur

```bash
ssh-copy-id -i ~/.ssh/lightsail_deploy.pub ubuntu@VOTRE_IP_LIGHTSAIL
```

### 2.3 Tester la connexion

```bash
ssh -i ~/.ssh/lightsail_deploy ubuntu@VOTRE_IP_LIGHTSAIL
```

### 2.4 Ajouter les secrets dans GitHub

Allez sur : `https://github.com/Bigschad/gaztracker/settings/secrets/actions`

Ajoutez les secrets suivants :

#### `LIGHTSAIL_SSH_KEY`
```bash
cat ~/.ssh/lightsail_deploy
```
Copiez tout le contenu (y compris BEGIN et END)

#### `LIGHTSAIL_HOST`
```
VOTRE_IP_LIGHTSAIL
# Exemple: 3.123.45.67
```

#### `LIGHTSAIL_USER`
```
ubuntu
```

## 📦 Étape 3 : Structure des Environnements

### Production (branche `main`)
- Chemin: `/opt/gaztracker`
- Backend: Port 8000
- Frontend: Port 3000
- Base de données: `gaztracker_db`

### Recette (branche `develop`)
- Chemin: `/opt/gaztracker-recette`
- Backend: Port 8001
- Frontend: Port 3001
- Base de données: `gaztracker_db_recette`

## 🔄 Étape 4 : Premier Déploiement

### 4.1 Déploiement automatique

Le déploiement se fait automatiquement quand vous poussez sur `main` ou `develop` :

```bash
git push origin develop  # Déploie sur recette
git push origin main     # Déploie sur production
```

### 4.2 Déploiement manuel

Vous pouvez aussi déclencher un déploiement manuellement :

1. Allez sur : `https://github.com/Bigschad/gaztracker/actions`
2. Sélectionnez "Deploy to Lightsail"
3. Cliquez sur "Run workflow"
4. Choisissez la branche
5. Cliquez sur "Run workflow"

## 🔍 Étape 5 : Vérification

### 5.1 Vérifier les services

```bash
ssh ubuntu@VOTRE_IP_LIGHTSAIL
cd /opt/gaztracker
sudo docker-compose ps
```

### 5.2 Vérifier les logs

```bash
# Tous les services
sudo docker-compose logs --tail=50

# Un service spécifique
sudo docker-compose logs backend --tail=50
sudo docker-compose logs frontend --tail=50
```

### 5.3 Tester l'API

```bash
# Health check
curl http://VOTRE_IP:8000/health

# API info
curl http://VOTRE_IP:8000/api/v1/
```

### 5.4 Accéder au frontend

```
http://VOTRE_IP:3000
```

## 🛠️ Commandes Utiles

### Redémarrer les services

```bash
cd /opt/gaztracker
sudo docker-compose restart
```

### Reconstruire les images

```bash
cd /opt/gaztracker
sudo docker-compose build --no-cache
sudo docker-compose up -d
```

### Voir l'utilisation des ressources

```bash
# Utilisation Docker
sudo docker stats

# Utilisation système
htop
df -h
```

### Nettoyage

```bash
# Nettoyer les images inutilisées
sudo docker system prune -af

# Nettoyer les volumes
sudo docker volume prune -f
```

## 🔥 Configuration du Firewall

Les ports suivants sont ouverts :

| Port | Service | Environnement |
|------|---------|---------------|
| 22   | SSH     | Tous |
| 80   | HTTP    | Tous |
| 443  | HTTPS   | Tous |
| 8000 | API     | Production |
| 3000 | Frontend| Production |
| 8001 | API     | Recette |
| 3001 | Frontend| Recette |

Vérifier le firewall :
```bash
sudo ufw status
```

## 🚨 Résolution des Problèmes

### Le déploiement échoue

1. Vérifiez les logs GitHub Actions
2. Vérifiez la connexion SSH :
   ```bash
   ssh -i ~/.ssh/lightsail_deploy ubuntu@VOTRE_IP_LIGHTSAIL
   ```
3. Vérifiez les secrets GitHub

### Les containers ne démarrent pas

```bash
cd /opt/gaztracker
sudo docker-compose logs
```

### Erreur de base de données

```bash
# Recréer la base
sudo docker-compose down -v
sudo docker-compose up -d
```

### Espace disque insuffisant

```bash
# Vérifier l'espace
df -h

# Nettoyer Docker
sudo docker system prune -af
sudo docker volume prune -f
```

## 📊 Monitoring

### Logs en temps réel

```bash
sudo docker-compose logs -f
```

### Statistiques Docker

```bash
sudo docker stats
```

### Health check automatique

Le workflow GitHub Actions vérifie automatiquement :
- La santé de l'API après déploiement
- Le statut des containers
- Les erreurs dans les logs

## 🔄 Mise à Jour du Workflow

Pour modifier le workflow :

1. Éditez `.github/workflows/deploy.yml`
2. Committez et pushez
3. Le nouveau workflow sera utilisé au prochain déploiement

## 📝 Notes Importantes

- **Backups** : Les bases de données ne sont PAS sauvegardées automatiquement. Configurez des backups réguliers.
- **Secrets** : Ne committez JAMAIS de secrets dans le code
- **Monitoring** : Configurez un monitoring externe (UptimeRobot, etc.)
- **SSL/HTTPS** : Configurez un reverse proxy avec Nginx et Let's Encrypt pour la production

## 🎯 Prochaines Étapes

1. [ ] Configurer HTTPS avec Let's Encrypt
2. [ ] Configurer les backups automatiques
3. [ ] Configurer un monitoring externe
4. [ ] Configurer les alertes email
5. [ ] Configurer un CDN pour les assets statiques

## 📞 Support

En cas de problème, vérifiez :
1. Les logs GitHub Actions
2. Les logs Docker sur le serveur
3. Les variables d'environnement
4. La configuration firewall

