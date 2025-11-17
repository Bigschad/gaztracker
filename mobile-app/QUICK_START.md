# ⚡ Démarrage Rapide - GazTracker Mobile

## 🚀 En 5 Minutes

### 1. Installer les dépendances
```bash
cd mobile-app
npm install
```

### 2. Configurer l'API
Éditer `src/config/apiConfig.ts` :
```typescript
baseUrl: 'http://VOTRE_IP:8000'  // Remplacer VOTRE_IP
```

### 3. Démarrer le backend
```bash
# Dans le dossier parent
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Lancer l'app
```bash
npm start
```

### 5. Tester
- Scanner le QR code avec Expo Go
- Se connecter avec vos identifiants
- Tester le scan RFID (nécessite appareil physique)

## 📱 Test Rapide NFC

1. Activer NFC sur votre téléphone Android
2. Aller sur l'écran de chargement
3. Cliquer sur "Scanner un tag RFID"
4. Approcher un tag NFC/RFID
5. ✅ Le tag devrait être détecté !

## ⚠️ Problèmes Courants

**"Network request failed"**
→ Vérifier que le backend tourne et que l'IP est correcte

**NFC ne fonctionne pas**
→ Vérifier que NFC est activé dans les paramètres Android

**App ne se charge pas**
→ `npx expo start -c` (nettoyer le cache)

---

Pour plus de détails, voir `TESTING_GUIDE.md`

