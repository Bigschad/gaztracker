# 📱 APPLICATION MOBILE GAZTRACKER - README

Documentation complète pour développer l'app mobile chauffeur **sans accès à l'API**.

---

## 🎯 VOTRE MISSION

Développer une app mobile React Native pour que les chauffeurs puissent :
- Scanner des palettes avec RFID
- Gérer les livraisons
- Collecter les palettes vides
- Suivre leur trajet GPS

---

## 📚 VOS 3 FICHIERS ESSENTIELS

### 1. **MOBILE_START_HERE.md** ⭐
→ Commencez par ici (10 min)

### 2. **MOBILE_MOCK_DATA.js** 💾
→ Copiez ce fichier dans votre projet

### 3. **MOBILE_DEV_SPEC.md** 📖
→ Référence complète (consultez au besoin)

---

## 🚀 DÉMARRAGE EN 3 ÉTAPES

### Étape 1 : Lire (10 min)
```bash
Ouvrir MOBILE_START_HERE.md
```

### Étape 2 : Setup (5 min)
```bash
npx create-expo-app gaztracker-mobile
cd gaztracker-mobile
cp MOBILE_MOCK_DATA.js ./src/services/mockData.js
```

### Étape 3 : Coder
```javascript
import { MOCK_USER, MOCK_BONS } from './services/mockData';

// Vous êtes prêt ! 🎉
```

---

## 📦 TOUT CE QUI EST FOURNI

| Fichier | Contenu | Utilité |
|---------|---------|---------|
| **MOBILE_START_HERE.md** | Guide démarrage | ⭐ Point d'entrée |
| **MOBILE_DEV_SPEC.md** | Spécifications (50p) | 📖 Référence |
| **MOBILE_MOCK_DATA.js** | Données fictives | 💾 Mock data |
| **MOBILE_API_ENDPOINTS.md** | Liste endpoints | 📡 Référence rapide |
| **RECAP_MOBILE_DOC.md** | Vue d'ensemble | 📊 Résumé |
| **INDEX_MOBILE.md** | Navigation | 🗺️ Index |

---

## ✅ CE QUE VOUS POUVEZ FAIRE

### SANS API (MAINTENANT)
✅ Développer tous les écrans  
✅ Tester tous les workflows  
✅ Simuler scanner RFID  
✅ Démos fonctionnelles  
✅ 80% de l'app complète

### AVEC API (PLUS TARD)
- Changer 1 flag (`MOCK_MODE = false`)
- Implémenter requêtes HTTP
- Tester intégration

---

## 🎨 ÉCRANS À DÉVELOPPER

1. Login
2. Liste Bons
3. Chargement RFID
4. Tournée Livraison
5. Déchargement RFID
6. Collecte Vides
7. Signature
8. Gestion Tags RFID

**Wireframes détaillés** dans `MOBILE_DEV_SPEC.md`

---

## 💡 EXEMPLE RAPIDE

```javascript
// services/apiService.js
import * as MockData from './mockData';

const MOCK_MODE = true;

export async function login(email, password) {
  if (MOCK_MODE) {
    await MockData.delay(500);
    return MockData.MOCK_LOGIN_RESPONSE;
  }
  // TODO: vraie API
}

export async function getMesBons() {
  if (MOCK_MODE) {
    await MockData.delay(300);
    return { items: MockData.MOCK_BONS };
  }
  // TODO: vraie API
}

export async function scanRFID(tagId) {
  if (MOCK_MODE) {
    await MockData.delay(200);
    const palette = MockData.findPaletteByRFID(tagId);
    if (!palette) throw new Error('Tag non trouvé');
    return { success: true, palette };
  }
  // TODO: vraie API
}
```

---

## 🆘 BESOIN D'AIDE ?

**Question** → **Fichier à consulter**

Comment démarrer ? → `MOBILE_START_HERE.md`  
Voir les endpoints ? → `MOBILE_API_ENDPOINTS.md`  
Wireframes ? → `MOBILE_DEV_SPEC.md` section 7  
Mock data ? → `MOBILE_MOCK_DATA.js`  
Vue d'ensemble ? → `RECAP_MOBILE_DOC.md`

---

## 📈 TEMPS ESTIMÉ

- **Setup** : 1 jour
- **MVP** : 7 jours
- **Features** : 5 jours
- **Tests** : 2 jours

**Total** : ~15 jours pour app complète

---

## 🎉 C'EST TOUT !

Vous avez tout ce qu'il faut. Commencez maintenant :

**→ Ouvrir [MOBILE_START_HERE.md](MOBILE_START_HERE.md)**

---

**Questions ?** Tous les fichiers sont dans le dossier du projet.  
**Index complet ?** Voir [INDEX_MOBILE.md](INDEX_MOBILE.md)

**Happy Coding! 🚀**

