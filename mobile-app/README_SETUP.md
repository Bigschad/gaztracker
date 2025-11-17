# 🚀 Guide de Démarrage - GazTracker Mobile

## Installation

### 1. Prérequis
- Node.js 18+
- npm ou yarn
- Expo CLI: `npm install -g expo-cli`
- Android Studio (pour Android) ou Xcode (pour iOS)
- Un appareil Android avec NFC ou un émulateur

### 2. Installation des dépendances

```bash
cd mobile-app
npm install
```

### 3. Configuration

#### Configuration API
Modifier `src/config/apiConfig.ts` pour pointer vers votre API backend:
- Pour émulateur Android: `http://10.0.2.2:8000`
- Pour appareil physique: `http://VOTRE_IP_LOCALE:8000`
- Pour production: `https://api.gaztracker.com`

#### Configuration NFC
Le NFC est déjà configuré dans `app.json`. Vérifiez que les permissions sont correctes.

### 4. Lancer l'application

```bash
# Démarrer Expo
npm start

# Lancer sur Android
npm run android

# Lancer sur iOS (Mac uniquement)
npm run ios
```

## Structure du Projet

```
mobile-app/
├── src/
│   ├── api/              # Clients API (Axios)
│   ├── components/       # Composants réutilisables
│   ├── config/           # Configuration (API, constants)
│   ├── hooks/            # Hooks personnalisés
│   ├── navigation/       # Navigation (à créer)
│   ├── redux/            # Store Redux + Slices
│   ├── screens/          # Écrans de l'application
│   ├── services/         # Services (RFID, PDF, etc.)
│   ├── storage/          # SQLite + AsyncStorage (à créer)
│   ├── types/            # Types TypeScript
│   └── utils/            # Utilitaires (à créer)
├── App.tsx               # Point d'entrée
├── app.json              # Configuration Expo
└── package.json          # Dépendances
```

## Fonctionnalités Implémentées

✅ Structure de base du projet
✅ Configuration TypeScript
✅ Redux Toolkit + Redux Persist
✅ Authentification JWT avec refresh token
✅ API client avec interceptors
✅ Composant RFID Scanner
✅ Screens: Login, Dashboard, Loading
✅ Hooks: useAuth, useRFID, useOfflineSync

## À Implémenter

- [ ] Screen Déchargement
- [ ] Screen Création Tag RFID
- [ ] Service PDF pour bons de livraison
- [ ] Signature électronique
- [ ] SQLite pour stockage offline
- [ ] Système de sync offline complet
- [ ] Notifications push
- [ ] Géolocalisation
- [ ] Rapports et analytics

## Commandes Utiles

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Build Android
npm run build:android

# Build iOS
npm run build:ios
```

## Dépannage

### NFC ne fonctionne pas
- Vérifier que l'appareil supporte NFC
- Activer NFC dans les paramètres Android
- Vérifier les permissions dans `app.json`

### Erreur de connexion API
- Vérifier que l'API backend est démarrée
- Vérifier l'URL dans `apiConfig.ts`
- Pour émulateur: utiliser `10.0.2.2` au lieu de `localhost`

### Erreurs de build
- Nettoyer le cache: `expo start -c`
- Réinstaller les dépendances: `rm -rf node_modules && npm install`

## Prochaines Étapes

1. Tester l'authentification
2. Tester le scan RFID sur un appareil physique
3. Implémenter les screens manquants
4. Ajouter le système de sync offline
5. Générer les PDFs de bons de livraison

