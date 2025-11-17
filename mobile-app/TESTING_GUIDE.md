# 🧪 Guide de Test - GazTracker Mobile

## 📋 Prérequis

### 1. Installation des dépendances

```bash
cd mobile-app
npm install
```

### 2. Vérifier l'installation Expo

```bash
npx expo --version
# Doit afficher la version d'Expo
```

### 3. Installer Expo Go sur votre téléphone (optionnel)

- **Android** : [Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
- **iOS** : [App Store](https://apps.apple.com/app/expo-go/id982107779)

## ⚙️ Configuration Avant Test

### 1. Configurer l'URL de l'API Backend

Éditer `src/config/apiConfig.ts` :

```typescript
export const API_CONFIG = {
  baseUrl: __DEV__
    ? 'http://192.168.1.XXX:8000'  // ⚠️ Remplacer XXX par votre IP locale
    : 'https://api.gaztracker.com',
  // ...
};
```

**Comment trouver votre IP locale :**
- **Windows** : `ipconfig` dans PowerShell → Chercher "IPv4 Address"
- **Mac/Linux** : `ifconfig` ou `ip addr` → Chercher votre IP locale (généralement 192.168.x.x)

### 2. Démarrer le Backend API

Assurez-vous que votre API FastAPI est démarrée :

```bash
# Dans le dossier racine du projet
cd ..
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

⚠️ **Important** : Utiliser `--host 0.0.0.0` pour accepter les connexions depuis le réseau local.

### 3. Vérifier la connexion réseau

- Votre téléphone et votre ordinateur doivent être sur le **même réseau WiFi**
- Désactiver le pare-feu Windows/Mac si nécessaire pour le port 8000

## 🚀 Lancer l'Application

### Option 1 : Avec Expo Go (Recommandé pour débuter)

```bash
npm start
```

Puis :
- Scanner le QR code avec Expo Go (Android) ou l'appareil photo (iOS)
- L'application se chargera sur votre téléphone

### Option 2 : Sur Émulateur Android

```bash
# Démarrer l'émulateur Android depuis Android Studio
npm run android
```

⚠️ **Note** : Pour l'émulateur, utiliser `http://10.0.2.2:8000` dans `apiConfig.ts` au lieu de votre IP locale.

### Option 3 : Build de développement

```bash
# Android
npx expo run:android

# iOS (Mac uniquement)
npx expo run:ios
```

## 🧪 Tests par Fonctionnalité

### 1. Test d'Authentification

#### Test Login
1. Ouvrir l'application
2. Vérifier que l'écran de login s'affiche
3. Entrer un email et mot de passe valides
4. Cliquer sur "Se connecter"
5. ✅ **Résultat attendu** : Redirection vers le Dashboard

#### Test Login avec mauvais identifiants
1. Entrer un email/mot de passe incorrect
2. ✅ **Résultat attendu** : Message d'erreur affiché

#### Test Session persistante
1. Se connecter
2. Fermer complètement l'application
3. Rouvrir l'application
4. ✅ **Résultat attendu** : Reste connecté (pas besoin de se reconnecter)

#### Test Timeout de session
1. Se connecter
2. Attendre 15 minutes sans activité
3. Essayer d'utiliser l'application
4. ✅ **Résultat attendu** : Redirection vers login

### 2. Test du Scan RFID

⚠️ **Important** : Le scan NFC nécessite un **appareil physique** avec NFC activé. L'émulateur ne supporte pas le NFC.

#### Préparation
1. Activer NFC dans les paramètres Android
2. Avoir un tag RFID/NFC disponible

#### Test Scan RFID
1. Aller sur l'écran de chargement ou déchargement
2. Cliquer sur "Scanner un tag RFID"
3. Approcher le tag RFID de l'appareil
4. ✅ **Résultat attendu** : 
   - Le tag est détecté
   - Le numéro du tag s'affiche
   - La palette correspondante est chargée

#### Test Scan avec tag inconnu
1. Scanner un tag qui n'existe pas dans la base
2. ✅ **Résultat attendu** : Message d'erreur "Palette non trouvée"

#### Test NFC désactivé
1. Désactiver NFC dans les paramètres
2. Essayer de scanner
3. ✅ **Résultat attendu** : Message demandant d'activer NFC

### 3. Test du Chargement de Palettes

#### Scénario complet
1. Se connecter en tant que **Chauffeur**
2. Aller sur le Dashboard
3. Sélectionner une expédition
4. Cliquer sur "Chargement"
5. Scanner plusieurs palettes (minimum 2-3)
6. Vérifier que les palettes apparaissent dans la liste
7. Cliquer sur "Confirmer le chargement"
8. ✅ **Résultat attendu** : 
   - Confirmation de succès
   - Retour au Dashboard
   - Expédition mise à jour

#### Test Validation
1. Scanner une palette déjà chargée
2. ✅ **Résultat attendu** : Message "Palette déjà scannée"

1. Scanner une palette non assignée à l'expédition
2. ✅ **Résultat attendu** : Message d'erreur

### 4. Test du Déchargement

#### Scénario complet
1. Sélectionner une expédition en transit
2. Aller sur "Déchargement"
3. Scanner les palettes déchargées
4. Vérifier la barre de progression
5. Confirmer le déchargement
6. ✅ **Résultat attendu** : 
   - Redirection vers le Bon de Livraison
   - Palettes marquées comme livrées

### 5. Test de la Signature Électronique

1. Après déchargement, aller sur le Bon de Livraison
2. Cliquer sur "Signer"
3. Dessiner une signature sur le canvas
4. Cliquer sur "Confirmer"
5. ✅ **Résultat attendu** : 
   - Signature sauvegardée
   - Affichage "✓ Signé" sur le BL

### 6. Test de Génération PDF

1. Après signature, cliquer sur "Générer le PDF"
2. ✅ **Résultat attendu** : 
   - PDF généré
   - Option de partage disponible

### 7. Test Mode Offline

#### Test Stockage Offline
1. Se connecter
2. Charger quelques données (expéditions, palettes)
3. Activer le mode avion
4. ✅ **Résultat attendu** : 
   - Indicateur "Mode hors ligne" affiché
   - Les données restent accessibles

#### Test Sync Automatique
1. En mode offline, scanner des palettes
2. Les actions sont mises en queue
3. Désactiver le mode avion
4. ✅ **Résultat attendu** : 
   - Sync automatique démarre
   - Les données sont synchronisées avec le serveur

#### Test Queue de Sync
1. Scanner plusieurs palettes en offline
2. Vérifier dans la base SQLite que les items sont en queue
3. Se reconnecter
4. ✅ **Résultat attendu** : Tous les items sont synchronisés

### 8. Test des Notifications

1. Créer une nouvelle expédition assignée au chauffeur
2. ✅ **Résultat attendu** : Notification push reçue

## 🐛 Dépannage

### Problème : "Network request failed"

**Solutions :**
1. Vérifier que l'API backend est démarrée
2. Vérifier l'URL dans `apiConfig.ts`
3. Vérifier que le téléphone et l'ordinateur sont sur le même WiFi
4. Pour émulateur : utiliser `10.0.2.2:8000` au lieu de l'IP locale
5. Désactiver temporairement le pare-feu

### Problème : NFC ne fonctionne pas

**Solutions :**
1. Vérifier que NFC est activé dans les paramètres Android
2. Vérifier que l'appareil supporte NFC
3. Tester avec un autre tag RFID
4. Redémarrer l'application
5. Vérifier les permissions dans `app.json`

### Problème : "Cannot connect to Metro bundler"

**Solutions :**
1. Arrêter le serveur Expo (`Ctrl+C`)
2. Nettoyer le cache : `npx expo start -c`
3. Redémarrer : `npm start`

### Problème : Erreurs de build Android

**Solutions :**
```bash
cd android
./gradlew clean
cd ..
npx expo run:android
```

### Problème : Base de données SQLite ne fonctionne pas

**Solutions :**
1. Vérifier que `expo-sqlite` est installé : `npm list expo-sqlite`
2. Vérifier les logs dans la console
3. Réinstaller : `npm install expo-sqlite`

## 📊 Checklist de Test Complète

### Authentification
- [ ] Login avec identifiants valides
- [ ] Login avec identifiants invalides
- [ ] Persistance de session
- [ ] Logout
- [ ] Timeout de session

### Scan RFID
- [ ] Scan tag existant
- [ ] Scan tag inexistant
- [ ] NFC désactivé
- [ ] Timeout de scan

### Chargement
- [ ] Scanner plusieurs palettes
- [ ] Validation des palettes
- [ ] Confirmation de chargement
- [ ] Gestion des erreurs

### Déchargement
- [ ] Scanner palettes déchargées
- [ ] Barre de progression
- [ ] Confirmation de déchargement
- [ ] Validation des statuts

### Signature & PDF
- [ ] Signature électronique
- [ ] Génération PDF
- [ ] Partage PDF

### Mode Offline
- [ ] Stockage local
- [ ] Queue de sync
- [ ] Sync automatique
- [ ] Indicateur offline

### Navigation
- [ ] Navigation entre écrans
- [ ] Retour en arrière
- [ ] Paramètres de route

## 🔍 Tests de Performance

### Test de Charge
1. Charger 50+ expéditions
2. Vérifier le temps de chargement
3. Vérifier la fluidité du scroll

### Test de Mémoire
1. Utiliser l'application pendant 30+ minutes
2. Vérifier qu'il n'y a pas de fuites mémoire
3. Vérifier la consommation de batterie

## 📱 Tests sur Différents Appareils

### Android
- [ ] Android 10+
- [ ] Différentes tailles d'écran
- [ ] Appareils avec/sans NFC

### iOS (si applicable)
- [ ] iOS 13+
- [ ] iPhone et iPad

## 🎯 Tests d'Intégration

### Workflow Complet
1. [ ] Login
2. [ ] Voir les expéditions
3. [ ] Charger des palettes
4. [ ] Partir en livraison
5. [ ] Décharger les palettes
6. [ ] Signer le BL
7. [ ] Générer et partager le PDF

## 📝 Logs et Debug

### Activer les logs
Dans `src/config/apiConfig.ts`, ajouter :
```typescript
axiosClient.interceptors.request.use((config) => {
  console.log('API Request:', config.method, config.url);
  return config;
});
```

### Voir les logs
```bash
# Logs Expo
npm start

# Logs Android
adb logcat | grep ReactNativeJS

# Logs iOS
# Utiliser Xcode Console
```

## ✅ Critères de Validation

L'application est prête pour la production si :
- ✅ Tous les tests de base passent
- ✅ Pas d'erreurs critiques dans les logs
- ✅ Performance acceptable (< 2s pour les opérations principales)
- ✅ Mode offline fonctionne correctement
- ✅ Scan RFID fonctionne sur appareil physique
- ✅ Pas de fuites mémoire
- ✅ UX fluide et intuitive

---

**Bon test ! 🚀**

