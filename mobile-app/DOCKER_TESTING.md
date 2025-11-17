# 🐳 Guide de Test avec Docker - GazTracker Mobile

## 📋 Vue d'ensemble

Ce guide explique comment tester l'application mobile avec Docker. Il y a deux approches :

1. **Backend API dans Docker** (Recommandé) - L'API tourne dans Docker, l'app mobile sur votre machine
2. **Environnement complet dans Docker** - Tout dans Docker (plus complexe)

## 🚀 Option 1 : Backend API dans Docker (Recommandé)

### Avantages
- ✅ Simple à mettre en place
- ✅ API isolée et reproductible
- ✅ App mobile fonctionne normalement
- ✅ Test NFC possible sur appareil physique

### Configuration

#### 1. Démarrer le backend API dans Docker

```bash
# Depuis le dossier mobile-app/
docker-compose -f docker-compose.mobile.yml up -d api postgres redis
```

#### 2. Vérifier que l'API fonctionne

```bash
# Vérifier les logs
docker-compose -f docker-compose.mobile.yml logs -f api

# Tester l'API
curl http://localhost:8000/health
```

#### 3. Configurer l'app mobile

Éditer `src/config/apiConfig.ts` :

```typescript
export const API_CONFIG = {
  baseUrl: __DEV__
    ? 'http://VOTRE_IP_MACHINE:8000'  // IP de votre machine (pas localhost!)
    : 'https://api.gaztracker.com',
  // ...
};
```

**Important** : Utiliser l'IP de votre machine, pas `localhost` ou `127.0.0.1`, car l'app mobile sur votre téléphone doit accéder à l'API sur votre machine.

#### 4. Trouver l'IP de votre machine

**Windows :**
```powershell
ipconfig
# Chercher "IPv4 Address" sous votre adaptateur WiFi
```

**Mac/Linux :**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
# ou
hostname -I
```

#### 5. Lancer l'app mobile

```bash
# Dans mobile-app/
npm start
```

Puis connecter votre téléphone (même réseau WiFi) et scanner le QR code.

### Commandes Utiles

```bash
# Démarrer les services
docker-compose -f docker-compose.mobile.yml up -d

# Voir les logs
docker-compose -f docker-compose.mobile.yml logs -f api

# Arrêter les services
docker-compose -f docker-compose.mobile.yml down

# Redémarrer l'API
docker-compose -f docker-compose.mobile.yml restart api

# Voir le statut
docker-compose -f docker-compose.mobile.yml ps
```

## 🐳 Option 2 : Environnement Complet dans Docker

### Limitations
- ⚠️ Expo Dev Server peut tourner dans Docker
- ⚠️ Mais l'app mobile doit toujours être sur un appareil physique/émulateur
- ⚠️ NFC nécessite un appareil physique (pas possible dans Docker)

### Configuration

#### 1. Démarrer tous les services

```bash
# Backend + Expo Dev Server
docker-compose -f docker-compose.mobile.yml --profile dev up -d
```

#### 2. Accéder à Expo Dev Server

L'Expo Dev Server sera accessible sur :
- `http://VOTRE_IP_MACHINE:19000` (Expo)
- `http://VOTRE_IP_MACHINE:19001` (Metro bundler)

#### 3. Connecter l'app mobile

Utiliser Expo Go et se connecter à `exp://VOTRE_IP_MACHINE:19000`

## 🧪 Tests Automatisés avec Docker

### Script de Test API

Créer `scripts/test-api-docker.sh` :

```bash
#!/bin/bash

echo "🧪 Test de l'API dans Docker..."

# Attendre que l'API soit prête
echo "⏳ Attente de l'API..."
sleep 10

# Test health check
echo "📡 Test health check..."
curl -f http://localhost:8000/health || exit 1

# Test endpoint API
echo "📡 Test endpoint API..."
curl -f http://localhost:8000/api/v1/health || exit 1

echo "✅ Tous les tests API passent!"
```

### Lancer les tests

```bash
# Démarrer l'environnement de test
docker-compose -f docker-compose.test.yml up -d

# Attendre que tout soit prêt
sleep 15

# Les tests s'exécutent automatiquement via le service api-test
docker-compose -f docker-compose.test.yml logs api-test

# Arrêter
docker-compose -f docker-compose.test.yml down -v
```

## 🔧 Configuration Avancée

### Variables d'Environnement

Créer `.env.docker` :

```env
# API
API_URL=http://VOTRE_IP:8000
API_PREFIX=/api/v1

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=gaztracker_db
POSTGRES_USER=gaztracker_user
POSTGRES_PASSWORD=gaztracker_password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

### Réseau Docker

Le réseau `mobile-network` permet aux conteneurs de communiquer :

```bash
# Vérifier le réseau
docker network inspect mobile-network

# Tester la connexion depuis un conteneur
docker exec -it gaztracker-api-mobile curl http://postgres:5432
```

## 📱 Test avec Appareil Physique

### Configuration Réseau

1. **Votre machine** : IP locale (ex: `192.168.1.100`)
2. **Docker API** : Accessible sur `192.168.1.100:8000`
3. **Téléphone** : Même réseau WiFi, se connecte à `192.168.1.100:8000`

### Vérification

```bash
# Depuis votre téléphone (même WiFi)
# Ouvrir un navigateur et aller sur :
http://VOTRE_IP:8000/health

# Doit retourner : {"status": "healthy", ...}
```

## 🐛 Dépannage

### Problème : "Cannot connect to API"

**Solutions :**
1. Vérifier que Docker tourne : `docker ps`
2. Vérifier que l'API est accessible : `curl http://localhost:8000/health`
3. Vérifier l'IP dans `apiConfig.ts` (pas localhost!)
4. Vérifier le pare-feu (port 8000 doit être ouvert)
5. Vérifier que le téléphone et la machine sont sur le même WiFi

### Problème : "Connection refused"

**Solutions :**
```bash
# Vérifier les logs
docker-compose -f docker-compose.mobile.yml logs api

# Redémarrer l'API
docker-compose -f docker-compose.mobile.yml restart api

# Vérifier les ports
docker-compose -f docker-compose.mobile.yml ps
```

### Problème : Base de données non accessible

**Solutions :**
```bash
# Vérifier que PostgreSQL tourne
docker-compose -f docker-compose.mobile.yml ps postgres

# Voir les logs
docker-compose -f docker-compose.mobile.yml logs postgres

# Redémarrer
docker-compose -f docker-compose.mobile.yml restart postgres
```

## 📊 Monitoring

### Voir les logs en temps réel

```bash
# Tous les services
docker-compose -f docker-compose.mobile.yml logs -f

# Seulement l'API
docker-compose -f docker-compose.mobile.yml logs -f api

# Seulement la base de données
docker-compose -f docker-compose.mobile.yml logs -f postgres
```

### Statistiques des conteneurs

```bash
# Utilisation des ressources
docker stats

# Informations détaillées
docker-compose -f docker-compose.mobile.yml ps
```

## 🎯 Workflow de Test Recommandé

1. **Démarrer le backend dans Docker**
   ```bash
   docker-compose -f docker-compose.mobile.yml up -d
   ```

2. **Vérifier que l'API fonctionne**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Configurer l'app mobile**
   - Mettre à jour `apiConfig.ts` avec votre IP
   - Lancer `npm start`

4. **Tester sur appareil physique**
   - Scanner le QR code avec Expo Go
   - Tester l'authentification
   - Tester le scan RFID

5. **Nettoyer après les tests**
   ```bash
   docker-compose -f docker-compose.mobile.yml down
   ```

## ✅ Checklist Docker

- [ ] Docker installé et fonctionnel
- [ ] Docker Compose installé
- [ ] Backend API démarre dans Docker
- [ ] API accessible sur `http://localhost:8000`
- [ ] API accessible depuis le téléphone (même WiFi)
- [ ] Base de données initialisée
- [ ] App mobile configurée avec la bonne IP
- [ ] Tests de connexion réussis

---

**Note importante** : Docker est excellent pour le backend API, mais l'app mobile React Native doit toujours tourner sur un appareil physique ou un émulateur pour tester le NFC et les fonctionnalités natives.

