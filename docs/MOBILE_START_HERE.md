# 📱 DÉVELOPPEUR MOBILE - COMMENCER ICI

Bienvenue ! Ce guide vous permet de démarrer le développement de l'application mobile **GazTracker Chauffeur** même sans accès à l'API backend.

---

## 🎯 VOTRE MISSION

Développer une application mobile pour les **chauffeurs** qui permet de :

1. ✅ Gérer les tags RFID
2. ✅ Consulter les bons d'enlèvement assignés
3. ✅ Charger les palettes par flash RFID
4. ✅ Livrer aux dépôts avec confirmation RFID
5. ✅ Collecter palettes vides par flash RFID
6. ✅ Suivre le trajet GPS

---

## 📚 VOS 3 FICHIERS ESSENTIELS

### 1️⃣ **MOBILE_DEV_SPEC.md** (COMPLET - 50 pages)

✅ Spécifications détaillées  
✅ Tous les endpoints API  
✅ Exemples requêtes/réponses  
✅ Wireframes des écrans  
✅ Workflow complet  
✅ Architecture recommandée  

**→ Commencez par ici pour tout comprendre**

### 2️⃣ **MOBILE_MOCK_DATA.js** (MOCK DATA)

✅ Données fictives prêtes à l'emploi  
✅ 10 tags RFID  
✅ 8 palettes  
✅ 2 bons d'enlèvement  
✅ Helper functions  

**→ Copiez ce fichier dans votre projet React Native**

### 3️⃣ **MOBILE_API_ENDPOINTS.md** (RÉFÉRENCE RAPIDE)

✅ Liste compacte des endpoints  
✅ Statuts et transitions  
✅ Priorités développement  

**→ Gardez-le ouvert pour référence rapide**

---

## 🚀 DÉMARRAGE EN 5 ÉTAPES

### Étape 1 : Lire la spec (10 min)

```bash
Ouvrir MOBILE_DEV_SPEC.md
→ Lire sections 1 à 7
→ Regarder les wireframes (écrans 1-7)
```

### Étape 2 : Créer le projet (2 min)

```bash
npx create-expo-app gaztracker-mobile
cd gaztracker-mobile
```

### Étape 3 : Copier le mock data (1 min)

```bash
# Copier MOBILE_MOCK_DATA.js dans src/services/
cp MOBILE_MOCK_DATA.js ./src/services/mockData.js
```

### Étape 4 : Créer le service API (15 min)

```javascript
// src/services/apiService.js
import * as MockData from './mockData';

const MOCK_MODE = true; // false quand API dispo

export class ApiService {
  async login(email, password) {
    if (MOCK_MODE) {
      await MockData.delay(500);
      if (email === "chauffeur1@transport.ci" && password === "Chauf@123") {
        return MockData.MOCK_LOGIN_RESPONSE;
      }
      throw new Error("Identifiants incorrects");
    }
    // TODO: Vraie requête API
  }
  
  async getMesBons() {
    if (MOCK_MODE) {
      await MockData.delay(300);
      return { items: MockData.MOCK_BONS };
    }
    // TODO: Vraie requête API
  }
  
  async scanRFID(tagId) {
    if (MOCK_MODE) {
      await MockData.delay(200);
      const palette = MockData.findPaletteByRFID(tagId);
      if (!palette) {
        throw new Error(`Tag ${tagId} non trouvé`);
      }
      return {
        success: true,
        palette: palette,
        scan_timestamp: new Date().toISOString()
      };
    }
    // TODO: Vraie requête API
  }
  
  // Ajouter d'autres méthodes selon besoin
}

export default new ApiService();
```

### Étape 5 : Développer les écrans (vous êtes prêt !)

```
Ordre recommandé :
1. Écran Login
2. Écran Liste Bons
3. Écran Chargement RFID
4. Écran Livraison
5. Écran Collecte Vides
6. Écran Signature
```

---

## 🎨 ÉCRANS À DÉVELOPPER

Voir wireframes détaillés dans `MOBILE_DEV_SPEC.md` section "WIREFRAMES ÉCRANS"

### Priorité 1 (MVP)
1. 🔐 **Login** - Authentification chauffeur
2. 📋 **Liste Bons** - Mes enlèvements assignés
3. 📦 **Chargement** - Scanner palettes pleines

### Priorité 2
4. 🗺️ **Tournée** - Itinéraire et navigation
5. 📍 **Livraison** - Décharger au dépôt
6. ✍️ **Signature** - Validation récepteur

### Priorité 3
7. 🔄 **Collecte Vides** - Scanner palettes vides
8. 🏷️ **Gestion Tags** - CRUD tags RFID
9. 📊 **Statistiques** - Résumé journée

---

## 🧪 TESTER SANS API

### Scénario de test 1 : Chargement

```javascript
// Dans votre composant
import api from './services/apiService';

// 1. Récupérer bon VALIDE
const bons = await api.getMesBons();
const bon = bons.items.find(b => b.status === 'VALIDE');

// 2. Démarrer chargement
await api.startChargement(bon.id);

// 3. Scanner 5 palettes
const tags = ['RFID0001', 'RFID0002', 'RFID0003', 'RFID0004', 'RFID0005'];
for (const tag of tags) {
  const result = await api.scanRFID(tag);
  console.log(`✅ ${result.palette.serial_number} chargée`);
}

// 4. Partir
await api.depart(bon.id);
```

### Scénario de test 2 : Livraison

```javascript
// 1. Récupérer bon EN_ROUTE
const bons = await api.getMesBons();
const bon = bons.items.find(b => b.status === 'EN_ROUTE');

// 2. Démarrer première livraison
const livraison = bon.livraisons[0];
await api.startLivraison(bon.id, livraison.id);

// 3. Décharger palettes
const tags = ['RFID0001', 'RFID0002', 'RFID0003'];
for (const tag of tags) {
  await api.unloadPalette(bon.id, livraison.id, tag);
}

// 4. Terminer avec signature
await api.completeLivraison(bon.id, livraison.id, {
  recepteur_nom: "Moussa Diallo",
  signature_base64: "data:image/png;base64,..."
});
```

---

## 📊 WORKFLOW COMPLET

```
1. LOGIN
   ↓
2. VOIR MES BONS (status: VALIDE)
   ↓
3. DÉMARRER CHARGEMENT
   ↓
4. SCANNER 5 PALETTES (RFID flash)
   ↓
5. PARTIR (status: EN_ROUTE)
   ↓
6. VOIR TOURNÉE (3 stops)
   ↓
7. ARRIVER AU STOP 1
   ↓
8. DÉCHARGER PALETTES (RFID flash)
   ↓
9. COLLECTER VIDES (RFID flash)
   ↓
10. SIGNER ET TERMINER
    ↓
11. PASSER AU STOP SUIVANT
    ↓
12. TERMINER LA TOURNÉE
```

---

## 💡 CONSEILS

### ✅ À FAIRE

- **Utilisez MOCK_MODE = true** pendant développement
- **Testez TOUS les scénarios** avec mock data
- **Simulez le scanner RFID** avec input manuel
- **Ajoutez des delays** (300-500ms) pour réalisme
- **Gérez les erreurs** (tag non trouvé, palette indisponible)
- **Mode offline** : AsyncStorage pour persistance

### ❌ À ÉVITER

- Ne vous bloquez PAS en attendant l'API
- N'inventez PAS vos propres structures de données
- Ne sautez PAS la simulation du scanner RFID
- Ne négligez PAS la gestion d'erreurs

---

## 🔄 QUAND L'API SERA DISPONIBLE

1. **Changer** `MOCK_MODE = false` dans apiService.js
2. **Ajouter** l'URL de base : `const API_URL = "https://api.gaztracker.ci"`
3. **Implémenter** les vraies requêtes HTTP avec axios
4. **Tester** endpoint par endpoint
5. **Comparer** réponses réelles vs mock data

---

## 📖 DOCUMENTATION COMPLÈTE

| Document | Contenu | Utilité |
|----------|---------|---------|
| **MOBILE_DEV_SPEC.md** | Spécifications complètes | ⭐ Principal |
| **MOBILE_MOCK_DATA.js** | Données fictives | ⭐ Essentiel |
| **MOBILE_API_ENDPOINTS.md** | Référence rapide | ⭐ Pratique |

---

## 🆘 BESOIN D'AIDE ?

### Questions fréquentes

**Q: Comment simuler le scanner RFID ?**  
R: Utilisez un simple TextInput pour saisir "RFID0001" manuellement. Ajoutez un bouton "Scanner" qui appelle `api.scanRFID(inputValue)`.

**Q: Les mock data suffisent vraiment ?**  
R: Oui ! Vous pouvez développer 80% de l'app avec le mock data fourni. Seule l'intégration API finale nécessitera l'API réelle.

**Q: Comment gérer les états complexes ?**  
R: Utilisez Context API ou Redux. Le mock data simule déjà les transitions d'états.

**Q: Et pour les tests ?**  
R: Le mock data est parfait pour les tests unitaires et d'intégration.

---

## 🎯 CHECKLIST RAPIDE

Avant de commencer à coder, vérifiez que vous avez :

- [ ] Lu `MOBILE_DEV_SPEC.md` sections 1-7
- [ ] Copié `MOBILE_MOCK_DATA.js` dans votre projet
- [ ] Créé `apiService.js` avec MOCK_MODE
- [ ] Testé le login avec mock data
- [ ] Compris le workflow (voir schéma ci-dessus)
- [ ] Choisi votre premier écran à développer

---

## 🚀 PRÊT ? C'EST PARTI !

**Votre premier objectif** : Afficher la liste des bons d'enlèvement

```javascript
// screens/MesBonsScreen.js
import { useEffect, useState } from 'react';
import api from '../services/apiService';

export default function MesBonsScreen() {
  const [bons, setBons] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBons();
  }, []);

  async function loadBons() {
    try {
      const data = await api.getMesBons();
      setBons(data.items);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <Text>Chargement...</Text>;

  return (
    <FlatList
      data={bons}
      renderItem={({ item }) => (
        <View>
          <Text>📋 {item.numero_bon}</Text>
          <Text>Status: {item.status}</Text>
          <Text>Destination: {item.depot_principal.name}</Text>
        </View>
      )}
    />
  );
}
```

---

## 🎉 BONNE CHANCE !

Vous avez tout ce qu'il faut pour démarrer. Le mock data est complet, la spec est claire, les wireframes sont fournis.

**Questions ?** Consultez `MOBILE_DEV_SPEC.md`  
**Référence rapide ?** Consultez `MOBILE_API_ENDPOINTS.md`

---

**Happy Coding! 🚀📱**

