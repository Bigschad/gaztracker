# 📱 GazTracker Mobile App

Application Android pour le scan RFID des palettes de bouteilles de gaz.

## 🎯 Fonctionnalités

1. **Création de tags RFID** - Scanner et enregistrer de nouveaux tags RFID
2. **Ajout de palettes aux expéditions** - Scanner les tags pour ajouter des palettes à une expédition
3. **Confirmation de déchargement** - Scanner les tags pour confirmer le déchargement chez un grossiste

## 🛠️ Technologies Recommandées

### Option 1: React Native (Recommandé) ⭐
- **Avantages**: 
  - **Cohérence avec votre stack** : Vous avez déjà un frontend React (backoffice-web)
  - **Bibliothèque NFC mature** : `react-native-nfc-manager` est très bien maintenue et documentée
  - **Courbe d'apprentissage réduite** : Si l'équipe maîtrise React/TypeScript
  - **Écosystème riche** : Nombreuses bibliothèques disponibles
  - **Cross-platform** : Android + iOS si besoin
- **Bibliothèque NFC**: `react-native-nfc-manager` (https://github.com/revtel/react-native-nfc-manager)
  - Support complet NFC/RFID
  - Documentation excellente
  - Communauté active

### Option 2: Flutter
- **Avantages**: 
  - Développement rapide
  - Excellent support NFC avec `nfc_manager`
  - UI moderne et performante
  - Cross-platform (Android + iOS si besoin)
- **Bibliothèque NFC**: `nfc_manager` (https://pub.dev/packages/nfc_manager)

### Option 3: Kotlin Natif
- **Avantages**: 
  - Performance maximale
  - Accès complet aux APIs Android
  - Support NFC natif Android

## 📋 Prérequis

### Pour Flutter
- Flutter SDK (3.0+)
- Android Studio
- Android SDK (API 21+)
- Un appareil Android avec NFC ou un émulateur

### Pour React Native
- Node.js (18+)
- React Native CLI
- Android Studio
- Android SDK

### Pour Kotlin
- Android Studio
- Kotlin plugin
- Android SDK (API 21+)

## 🚀 Démarrage Rapide (React Native)

```bash
# 1. Installer React Native CLI
npm install -g react-native-cli

# 2. Créer le projet React Native
cd mobile-app
npx react-native init GazTrackerMobile --template react-native-template-typescript

# 3. Installer les dépendances
cd GazTrackerMobile
npm install react-native-nfc-manager
npm install axios  # Pour les appels API
npm install @react-native-async-storage/async-storage  # Pour stocker le token JWT
npm install react-navigation  # Pour la navigation (optionnel)

# 4. Lier les dépendances natives (si nécessaire)
cd android && ./gradlew clean && cd ..

# 5. Configurer les permissions NFC dans android/app/src/main/AndroidManifest.xml
# Voir la section Configuration ci-dessous

# 6. Lancer l'application
npm run android
# ou
npx react-native run-android
```

### Alternative: Flutter

```bash
# 1. Installer Flutter
# Voir: https://flutter.dev/docs/get-started/install

# 2. Créer le projet Flutter
cd mobile-app
flutter create gaztracker_mobile

# 3. Ajouter les dépendances
cd gaztracker_mobile
flutter pub add nfc_manager
flutter pub add http
flutter pub add shared_preferences
flutter pub add provider  # Pour la gestion d'état

# 4. Configurer les permissions NFC dans android/app/src/main/AndroidManifest.xml
# Voir la section Configuration ci-dessous

# 5. Lancer l'application
flutter run
```

## ⚙️ Configuration

### Configuration NFC (Android)

Dans `android/app/src/main/AndroidManifest.xml`:

```xml
<manifest>
    <!-- Permission NFC -->
    <uses-permission android:name="android.permission.NFC" />
    
    <!-- Feature NFC (optionnel, pour filtrer sur Play Store) -->
    <uses-feature
        android:name="android.hardware.nfc"
        android:required="false" />
    
    <application>
        <!-- ... -->
    </application>
</manifest>
```

### Configuration API

#### Pour React Native
Créer un fichier `src/config/apiConfig.ts`:

```typescript
export const API_CONFIG = {
  // TODO: Remplacer par l'URL de votre API en production
  baseUrl: __DEV__ 
    ? 'http://10.0.2.2:8000'  // Pour émulateur Android
    : 'https://api.gaztracker.com',  // Production
  apiPrefix: '/api/v1',
};

export const getApiUrl = () => `${API_CONFIG.baseUrl}${API_CONFIG.apiPrefix}`;
```

#### Pour Flutter
Créer un fichier `lib/config/api_config.dart`:

```dart
class ApiConfig {
  // TODO: Remplacer par l'URL de votre API en production
  static const String baseUrl = 'http://10.0.2.2:8000'; // Pour émulateur Android
  // static const String baseUrl = 'http://192.168.1.XXX:8000'; // Pour appareil physique
  static const String apiPrefix = '/api/v1';
  
  static String get apiUrl => '$baseUrl$apiPrefix';
}
```

## 📱 Structure de l'Application

### React Native
```
mobile-app/GazTrackerMobile/
├── src/
│   ├── App.tsx
│   ├── config/
│   │   └── apiConfig.ts
│   ├── models/
│   │   ├── rfidTag.ts
│   │   ├── palette.ts
│   │   └── expedition.ts
│   ├── services/
│   │   ├── apiService.ts
│   │   ├── authService.ts
│   │   └── nfcService.ts
│   ├── screens/
│   │   ├── LoginScreen.tsx
│   │   ├── CreateTagScreen.tsx
│   │   ├── AddPaletteToExpeditionScreen.tsx
│   │   └── ConfirmUnloadingScreen.tsx
│   ├── components/
│   │   └── NFCScanner.tsx
│   └── utils/
│       └── constants.ts
├── android/
├── ios/
└── package.json
```

### Flutter
```
mobile-app/gaztracker_mobile/
├── lib/
│   ├── main.dart
│   ├── config/
│   │   └── api_config.dart
│   ├── models/
│   │   ├── rfid_tag.dart
│   │   ├── palette.dart
│   │   └── expedition.dart
│   ├── services/
│   │   ├── api_service.dart
│   │   ├── auth_service.dart
│   │   └── nfc_service.dart
│   ├── screens/
│   │   ├── login_screen.dart
│   │   ├── create_tag_screen.dart
│   │   ├── add_palette_to_expedition_screen.dart
│   │   └── confirm_unloading_screen.dart
│   ├── widgets/
│   │   └── nfc_scanner_widget.dart
│   └── utils/
│       └── constants.dart
├── android/
├── ios/
└── pubspec.yaml
```

## 🔌 Endpoints API Utilisés

### Authentification
- `POST /api/v1/auth/login` - Connexion
- `POST /api/v1/auth/refresh` - Rafraîchir le token

### Tags RFID
- `POST /api/v1/rfid-tags` - Créer un tag RFID
- `GET /api/v1/rfid-tags/number/{tag_number}` - Récupérer un tag par numéro

### Palettes
- `GET /api/v1/palettes/rfid/{rfid_tag_number}` - Récupérer une palette par RFID
- `POST /api/v1/palettes/scan` - Scanner une palette

### Expéditions
- `GET /api/v1/expeditions` - Liste des expéditions
- `GET /api/v1/expeditions/{id}` - Détails d'une expédition
- `POST /api/v1/expeditions/{id}/palettes` - Ajouter des palettes à une expédition

## 📝 Workflow d'Utilisation

### 1. Création de Tag RFID
1. L'utilisateur ouvre l'écran "Créer Tag RFID"
2. L'application active le scanner NFC
3. L'utilisateur scanne le tag RFID
4. L'application envoie le tag_number à l'API pour création
5. Confirmation de création

### 2. Ajout de Palette à une Expédition
1. L'utilisateur sélectionne une expédition
2. L'application active le scanner NFC
3. L'utilisateur scanne le tag de la palette
4. L'application vérifie que la palette existe
5. L'application ajoute la palette à l'expédition via l'API
6. Confirmation d'ajout

### 3. Confirmation de Déchargement
1. L'utilisateur sélectionne une expédition (ou scanne directement)
2. L'application active le scanner NFC
3. L'utilisateur scanne le tag de la palette
4. L'application vérifie que la palette appartient à l'expédition
5. L'application enregistre le scan (et met à jour le statut si nécessaire)
6. Confirmation de déchargement

## 🔐 Authentification

L'application utilise JWT pour l'authentification:

### React Native
- Token d'accès stocké dans `AsyncStorage`
- Refresh token pour renouveler l'accès
- Intercepteur Axios pour ajouter le token aux requêtes

### Flutter
- Token d'accès stocké dans `SharedPreferences`
- Refresh token pour renouveler l'accès
- Intercepteur HTTP pour ajouter le token aux requêtes

## 🧪 Tests

### Tester avec un émulateur Android
- L'émulateur Android ne supporte pas le NFC réel
- Utiliser un appareil physique pour tester le scan NFC
- Pour les tests d'API, utiliser l'émulateur avec l'URL `http://10.0.2.2:8000`

### Tester avec un appareil physique
- Activer le mode développeur
- Activer le débogage USB
- Connecter l'appareil et lancer :
  - React Native: `npm run android` ou `npx react-native run-android`
  - Flutter: `flutter run`

## 📦 Build de Production

### React Native
```bash
# Générer un APK
cd android
./gradlew assembleRelease

# Générer un App Bundle (pour Play Store)
./gradlew bundleRelease
```

### Flutter
```bash
# Générer un APK
flutter build apk --release

# Générer un App Bundle (pour Play Store)
flutter build appbundle --release
```

## 🐛 Dépannage

### NFC ne fonctionne pas
- Vérifier que l'appareil supporte NFC
- Vérifier que NFC est activé dans les paramètres Android
- Vérifier les permissions dans AndroidManifest.xml

### Erreur de connexion API
- Vérifier que l'API backend est démarrée
- Vérifier l'URL dans la configuration API
- Pour émulateur: utiliser `10.0.2.2` au lieu de `localhost`
- Pour appareil physique: utiliser l'IP locale du serveur (ex: `192.168.1.XXX:8000`)

## 📚 Ressources

### React Native
- [react-native-nfc-manager Documentation](https://github.com/revtel/react-native-nfc-manager)
- [React Native Documentation](https://reactnative.dev/)
- [React Native NFC Tutorial](https://github.com/revtel/react-native-nfc-manager#readme)

### Flutter
- [nfc_manager Documentation](https://pub.dev/packages/nfc_manager)
- [Flutter Documentation](https://flutter.dev/)

### Général
- [Documentation API GazTracker](../README.md)
- [Android NFC Guide](https://developer.android.com/guide/topics/connectivity/nfc)

## 👥 Équipe

- **Mobile Developer**: À définir
- **Backend API**: FastAPI (dans `/app`)

---

## 💡 Pourquoi React Native est recommandé pour ce projet ?

1. **Cohérence technologique** : Vous avez déjà un frontend React (backoffice-web), donc l'équipe maîtrise React/TypeScript
2. **Bibliothèque NFC mature** : `react-native-nfc-manager` est très bien maintenue, documentée et testée
3. **Réutilisation du code** : Possibilité de partager des types TypeScript entre le web et le mobile
4. **Courbe d'apprentissage** : Plus rapide si l'équipe connaît déjà React

**Note**: Ce README est un guide de démarrage. Les deux technologies (React Native et Flutter) sont viables, mais React Native est recommandé pour ce projet spécifique.

