# 🔧 Correction Docker - Package PDF

## Problème résolu

Le package `@react-native-pdf/pdf-lib` n'existe pas dans npm. Il a été remplacé par `expo-print` qui est la solution recommandée pour Expo.

## Changements effectués

1. ✅ `package.json` : Remplacé `@react-native-pdf/pdf-lib` par `expo-print`
2. ✅ `pdfService.ts` : Mis à jour pour utiliser `expo-print`
3. ✅ `docker-compose.mobile.yml` : Retiré la version obsolète

## Relancer le build

```bash
# Reconstruire l'image Docker
docker-compose -f docker-compose.mobile.yml build expo-dev

# Ou si vous utilisez le docker-compose principal
cd ..
docker-compose build
```

## Alternative : Tester sans Docker (Recommandé)

Pour tester l'app mobile, il est plus simple de :

1. **Démarrer le backend dans Docker** (depuis le dossier racine) :
   ```bash
   docker-compose up -d app postgres redis
   ```

2. **Lancer l'app mobile localement** (depuis mobile-app/) :
   ```bash
   npm install  # Installer les dépendances (incluant expo-print)
   npm start
   ```

Cette approche est plus simple car :
- ✅ Pas besoin de build Docker pour l'app mobile
- ✅ Hot reload fonctionne mieux
- ✅ Test NFC possible sur appareil physique
- ✅ Débogage plus facile

## Vérification

Après `npm install`, vérifier que `expo-print` est installé :

```bash
npm list expo-print
```

---

**Note** : Docker est excellent pour le backend API, mais pour l'app mobile React Native, il est généralement plus pratique de la lancer localement.

