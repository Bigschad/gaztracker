# 🐳 Démarrage Rapide avec Docker

## ⚡ En 3 Étapes

### 1. Démarrer le Backend dans Docker

Depuis le dossier **racine** du projet (`gaztracker/`) :

```bash
# Démarrer l'API, PostgreSQL et Redis
docker-compose up -d app postgres redis
```

### 2. Vérifier que l'API fonctionne

```bash
# Tester l'API
curl http://localhost:8000/health

# Voir les logs
docker-compose logs -f app
```

### 3. Configurer et lancer l'app mobile

```bash
# Aller dans le dossier mobile-app
cd mobile-app

# Trouver votre IP locale
# Windows: ipconfig
# Mac/Linux: ifconfig | grep "inet "

# Éditer src/config/apiConfig.ts
# Remplacer par votre IP: baseUrl: 'http://VOTRE_IP:8000'

# Lancer l'app
npm start
```

## 📱 Tester sur votre téléphone

1. **Vérifier que votre téléphone est sur le même WiFi** que votre ordinateur
2. **Scanner le QR code** avec Expo Go
3. **Tester l'authentification** et les fonctionnalités

## 🔧 Commandes Utiles

```bash
# Voir les logs de l'API
docker-compose logs -f app

# Redémarrer l'API
docker-compose restart app

# Arrêter tout
docker-compose down

# Voir le statut
docker-compose ps
```

## ⚠️ Important

- L'API doit être accessible depuis votre téléphone
- Utiliser l'**IP de votre machine**, pas `localhost`
- Le téléphone et l'ordinateur doivent être sur le **même réseau WiFi**

## 🐛 Dépannage

**"Network request failed"**
→ Vérifier que l'API tourne : `docker-compose ps`
→ Vérifier l'IP dans `apiConfig.ts`
→ Tester depuis le téléphone : `http://VOTRE_IP:8000/health`

**API ne démarre pas**
→ Vérifier les logs : `docker-compose logs app`
→ Vérifier que PostgreSQL et Redis sont démarrés

---

Pour plus de détails, voir `DOCKER_TESTING.md`

