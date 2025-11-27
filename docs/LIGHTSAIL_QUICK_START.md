# 🚀 Guide Rapide Lightsail + GitHub Actions

Guide visuel pour déployer GazTracker sur AWS Lightsail avec déploiement automatique.

## 📋 Vue d'Ensemble

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Développeur   │         │  GitHub Actions  │         │    Lightsail    │
│   (Votre PC)    │         │   (Automatique)  │         │    (Serveur)    │
└────────┬────────┘         └────────┬─────────┘         └────────┬────────┘
         │                           │                            │
         │ git push origin develop   │                            │
         ├──────────────────────────>│                            │
         │                           │ SSH + Deploy               │
         │                           ├───────────────────────────>│
         │                           │                            │
         │                           │ Health Check               │
         │                           │<───────────────────────────┤
         │ Notification              │                            │
         │<──────────────────────────┤                            │
         │                           │                            │
```

## ⚡ Configuration en 3 Étapes

### 🔧 ÉTAPE 1 : Préparer le Serveur (15 min)

#### A. Se connecter au serveur

```bash
# Remplacez par votre IP Lightsail
ssh ubuntu@3.123.45.67
```

#### B. Exécuter le script d'installation

```bash
# Télécharger le script
wget https://raw.githubusercontent.com/Bigschad/gaztracker/develop/scripts/setup-lightsail-server.sh

# Exécuter
chmod +x setup-lightsail-server.sh
./setup-lightsail-server.sh
```

Le script va installer :
- ✅ Docker & Docker Compose
- ✅ Dépendances système
- ✅ Configuration du firewall
- ✅ Répertoires de déploiement
- ✅ Template de configuration

#### C. Configurer les variables d'environnement

```bash
# Déconnexion puis reconnexion (pour Docker)
exit
ssh ubuntu@3.123.45.67

# Configuration
cd /opt/gaztracker
cp .env.template .env
nano .env
```

**Variables à modifier** (remplacez `CHANGE_ME`) :

```env
# Générez des clés sécurisées avec:
# python3 -c 'import secrets; print(secrets.token_urlsafe(32))'

POSTGRES_PASSWORD=VotreMdpSecurePostgres123!
SECRET_KEY=votre-cle-secrete-generee-ici
JWT_SECRET_KEY=autre-cle-secrete-pour-jwt
ADMIN_PASSWORD=MotDePasseAdminSecure123!
ALLOWED_ORIGINS=http://3.123.45.67:3000,http://votre-domaine.com
```

Sauvegardez : `Ctrl+X` → `Y` → `Enter`

---

### 🔐 ÉTAPE 2 : Configurer les Secrets GitHub (10 min)

#### A. Générer une paire de clés SSH (sur VOTRE PC Windows)

```powershell
# Dans PowerShell
ssh-keygen -t ed25519 -C "github-actions-gaztracker" -f $HOME\.ssh\lightsail_deploy
```

Appuyez sur `Enter` 2 fois (pas de passphrase pour GitHub Actions)

#### B. Copier la clé publique sur le serveur

```powershell
# Afficher la clé publique
cat $HOME\.ssh\lightsail_deploy.pub

# Copiez le contenu affiché
```

Puis sur le serveur Lightsail :
```bash
# Sur le serveur
nano ~/.ssh/authorized_keys
# Collez la clé publique à la fin du fichier
# Sauvegardez: Ctrl+X → Y → Enter
```

#### C. Tester la connexion

```powershell
# Sur votre PC
ssh -i $HOME\.ssh\lightsail_deploy ubuntu@3.123.45.67
```

Si ça fonctionne ✅, continuez !

#### D. Ajouter les secrets dans GitHub

1. **Allez sur** : https://github.com/Bigschad/gaztracker/settings/secrets/actions

2. **Cliquez sur** : `New repository secret`

3. **Ajoutez ces 3 secrets** :

**Secret #1 : `LIGHTSAIL_SSH_KEY`**
```powershell
# Sur votre PC, affichez la clé PRIVÉE
cat $HOME\.ssh\lightsail_deploy

# Copiez TOUT le contenu (y compris BEGIN et END)
# Exemple:
# -----BEGIN OPENSSH PRIVATE KEY-----
# b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtz
# ... toutes les lignes ...
# -----END OPENSSH PRIVATE KEY-----
```

**Secret #2 : `LIGHTSAIL_HOST`**
```
3.123.45.67
```
(Remplacez par votre vraie IP Lightsail)

**Secret #3 : `LIGHTSAIL_USER`**
```
ubuntu
```

---

### 🚀 ÉTAPE 3 : Déployer (5 min)

#### A. Déploiement automatique

Le déploiement se fait **automatiquement** quand vous poussez :

```bash
# Déployer sur RECETTE (develop)
git push origin develop

# Déployer sur PRODUCTION (main)
git push origin main
```

#### B. Déploiement manuel

1. Allez sur : https://github.com/Bigschad/gaztracker/actions
2. Cliquez sur "Deploy to Lightsail"
3. Cliquez sur "Run workflow"
4. Sélectionnez la branche (`develop` ou `main`)
5. Cliquez sur "Run workflow"

#### C. Suivre le déploiement

Sur la page Actions, vous verrez :
- ✅ Checkout code
- ✅ Configure SSH
- ✅ Upload to server
- ✅ Deploy on server
- ✅ Health check
- ✅ Cleanup

Durée totale : ~5-10 minutes

---

## 🎯 Résultat Final

### URLs d'accès

**Environnement RECETTE** (branche `develop`)
```
Frontend: http://VOTRE_IP:3001
Backend:  http://VOTRE_IP:8001
API Docs: http://VOTRE_IP:8001/docs
```

**Environnement PRODUCTION** (branche `main`)
```
Frontend: http://VOTRE_IP:3000
Backend:  http://VOTRE_IP:8000
API Docs: http://VOTRE_IP:8000/docs
```

### Connexion par défaut
```
Email:    admin@gaztracker.com
Password: Le mot de passe que vous avez défini dans .env
```

---

## 🔍 Vérification

### Sur le serveur

```bash
ssh ubuntu@VOTRE_IP_LIGHTSAIL

# Vérifier les containers
cd /opt/gaztracker
sudo docker-compose ps

# Voir les logs
sudo docker-compose logs --tail=50

# Voir les ressources
sudo docker stats
```

### Depuis votre PC

```powershell
# Test de l'API
Invoke-WebRequest -Uri "http://VOTRE_IP:8000/health"

# Ou avec curl
curl http://VOTRE_IP:8000/health
```

---

## 🛠️ Commandes Utiles

### Redémarrer les services

```bash
ssh ubuntu@VOTRE_IP_LIGHTSAIL
cd /opt/gaztracker
sudo docker-compose restart
```

### Voir les logs en temps réel

```bash
sudo docker-compose logs -f
```

### Reconstruire après modification de code

```bash
# Le workflow GitHub Actions le fait automatiquement
# Mais vous pouvez aussi le faire manuellement:
cd /opt/gaztracker
sudo docker-compose down
sudo docker-compose build --no-cache
sudo docker-compose up -d
```

---

## 📊 Monitoring

### Workflows GitHub Actions

Visualisez tous vos déploiements :
```
https://github.com/Bigschad/gaztracker/actions
```

Chaque déploiement affiche :
- Temps d'exécution
- Logs détaillés
- Statut de réussite/échec
- Health check final

### Notifications

GitHub vous notifie automatiquement par email si :
- ✅ Le déploiement réussit
- ❌ Le déploiement échoue

---

## 🚨 Résolution des Problèmes

### Le workflow échoue à "Configure SSH"

➡️ Vérifiez que `LIGHTSAIL_SSH_KEY` est correctement configuré dans les secrets GitHub

### Le workflow échoue à "Deploy on server"

➡️ Vérifiez que le serveur est accessible et que Docker est installé

### Les containers ne démarrent pas

```bash
# Sur le serveur
cd /opt/gaztracker
sudo docker-compose logs

# Vérifier le .env
cat .env

# Reconstruire
sudo docker-compose down -v
sudo docker-compose up -d
```

### "Permission denied" sur le serveur

```bash
# Donner les permissions
sudo chown -R $USER:$USER /opt/gaztracker
sudo chmod -R 755 /opt/gaztracker
```

---

## 🔐 Sécurité

### Recommandations

- ✅ Utilisez des mots de passe forts (32+ caractères)
- ✅ Activez le firewall (déjà fait par le script)
- ✅ Configurez HTTPS avec Let's Encrypt
- ✅ Limitez l'accès SSH par IP si possible
- ✅ Activez les backups automatiques Lightsail
- ✅ Utilisez des secrets GitHub (jamais dans le code)

### Configuration HTTPS (Optionnel)

```bash
# Installer Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtenir un certificat
sudo certbot --nginx -d votre-domaine.com
```

---

## 📝 Checklist Complète

- [ ] Serveur Lightsail créé et accessible via SSH
- [ ] Script `setup-lightsail-server.sh` exécuté
- [ ] Fichier `.env` configuré sur le serveur
- [ ] Paire de clés SSH générée
- [ ] Clé publique ajoutée au serveur
- [ ] 3 secrets configurés dans GitHub
- [ ] Test de connexion SSH réussi
- [ ] Premier déploiement lancé
- [ ] Health check réussi
- [ ] Application accessible via navigateur

---

## 🎉 C'est Tout !

Une fois configuré, chaque `git push` déclenchera automatiquement :
1. Build des images Docker
2. Transfert vers le serveur
3. Déploiement
4. Health check
5. Notification

**Temps de déploiement** : ~5-10 minutes

**Fréquence** : À chaque push sur `main` ou `develop`

---

## 📞 Support

Documentation complète : `docs/GITHUB_ACTIONS_SETUP.md`

Pour toute question, vérifiez :
1. Les logs GitHub Actions
2. Les logs Docker sur le serveur
3. Le fichier `.env` sur le serveur

