# 📡 API ENDPOINTS - APPLICATION MOBILE

Référence rapide des endpoints nécessaires pour l'application mobile chauffeur.

---

## 🔐 AUTHENTIFICATION

```
POST   /api/v1/auth/login
```
Body: `{ "email", "password" }`  
Return: `{ "access_token", "user" }`

---

## 🏷️ TAGS RFID

```
GET    /api/v1/rfid-tags?status=ACTIVE&limit=50
POST   /api/v1/rfid-tags/scan
POST   /api/v1/rfid-tags
POST   /api/v1/rfid-tags/{id}/assign-palette
```

---

## 📦 PALETTES

```
GET    /api/v1/palettes?skip=0&limit=50
GET    /api/v1/palettes?status=AU_CENTRE&is_full=true
GET    /api/v1/palettes/by-rfid/{tag_id}
GET    /api/v1/palettes/{id}
```

---

## 🚛 BONS D'ENLÈVEMENT

### Consulter

```
GET    /api/v1/bons-enlevement/my-assignments
GET    /api/v1/bons-enlevement/{id}
GET    /api/v1/bons-enlevement/{id}/palettes
GET    /api/v1/bons-enlevement/{id}/itineraire
```

### Workflow Chargement

```
POST   /api/v1/bons-enlevement/{id}/start-chargement
POST   /api/v1/bons-enlevement/{id}/add-palette-by-rfid
POST   /api/v1/bons-enlevement/{id}/remove-palette
POST   /api/v1/bons-enlevement/{id}/depart
```

### Workflow Livraisons

```
POST   /api/v1/bons-enlevement/{id}/livraisons/{liv_id}/start
POST   /api/v1/bons-enlevement/{id}/livraisons/{liv_id}/unload-palette
POST   /api/v1/bons-enlevement/{id}/livraisons/{liv_id}/complete
```

### Workflow Collecte

```
POST   /api/v1/bons-enlevement/{id}/livraisons/{liv_id}/start-collecte
POST   /api/v1/bons-enlevement/{id}/livraisons/{liv_id}/collect-empty
GET    /api/v1/bons-enlevement/{id}/collectes
```

### GPS Tracking

```
POST   /api/v1/bons-enlevement/{id}/update-position
```

### Terminer

```
POST   /api/v1/bons-enlevement/{id}/terminer
```

---

## 📊 STATUTS

### Bon d'Enlèvement
- `CREATION` → `VALIDE` → `EN_CHARGEMENT` → `EN_ROUTE` → `EN_LIVRAISON` → `TERMINE`

### Palette
- `AU_CENTRE` → `EN_CHARGEMENT` → `EN_ROUTE_LIVRAISON` → `AU_DEPOT`

### Livraison
- `EN_ATTENTE` → `EN_COURS` → `LIVREE`

---

## 🔑 HEADERS

Toutes les requêtes (sauf login) :
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

---

## 📱 PRIORITÉS DÉVELOPPEMENT

### Phase 1 : Essentiels
1. Login
2. Liste mes bons
3. Voir détails bon

### Phase 2 : Chargement
4. Scanner RFID (simulation)
5. Ajouter palette au chargement
6. Partir

### Phase 3 : Livraisons
7. Démarrer livraison
8. Scanner déchargement
9. Signature
10. Terminer livraison

### Phase 4 : Collecte
11. Scanner vides
12. Enregistrer collecte

---

## 📄 VOIR AUSSI

- **Spécifications complètes** : `MOBILE_DEV_SPEC.md`
- **Mock Data** : `MOBILE_MOCK_DATA.js`
- **API Swagger** : http://localhost:8000/docs

---

**Mode Offline** : Utilisez `MOBILE_MOCK_DATA.js` jusqu'à ce que l'API soit disponible.

