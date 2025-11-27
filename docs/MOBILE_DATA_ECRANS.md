# 📱 DONNÉES & ÉCRANS - APPLICATION MOBILE

Document unique contenant toutes les données fictives et les champs nécessaires pour créer les écrans de l'application mobile chauffeur.

---

## 👤 UTILISATEUR (CHAUFFEUR)

### Données

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Koné Seydou",
  "email": "chauffeur1@transport.ci",
  "role": "CHAUFFEUR",
  "phone": "+225 07 90 00 00 01",
  "is_active": true
}
```

### Explication des champs

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | Identifiant unique du chauffeur |
| `name` | String | Nom complet du chauffeur |
| `email` | String | Email pour connexion |
| `role` | String | Rôle = "CHAUFFEUR" |
| `phone` | String | Numéro de téléphone |
| `is_active` | Boolean | Compte actif ou non |

### Utilisé dans

- **Écran Login** : email, password
- **Écran Profil** : name, email, phone
- **Header App** : name (affichage)

---

## 🔐 CONNEXION (LOGIN)

### Requête

```json
{
  "email": "chauffeur1@transport.ci",
  "password": "Chauf@123"
}
```

### Réponse

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Koné Seydou",
    "email": "chauffeur1@transport.ci",
    "role": "CHAUFFEUR",
    "phone": "+225 07 90 00 00 01"
  }
}
```

### Champs écran Login

- **Input Email** : email
- **Input Password** : password (masqué)
- **Bouton** : "Se connecter"
- **Affichage** : Message erreur si échec

---

## 🏷️ TAGS RFID

### Données (10 tags)

```json
[
  {
    "id": "650e8400-e29b-41d4-a716-446655440001",
    "tag_id": "RFID0001",
    "label": "Tag Palette #0001",
    "status": "ACTIVE",
    "assigned_to_palette": true,
    "palette_serial": "PAL-2025-00001"
  },
  {
    "id": "650e8400-e29b-41d4-a716-446655440002",
    "tag_id": "RFID0002",
    "label": "Tag Palette #0002",
    "status": "ACTIVE",
    "assigned_to_palette": true,
    "palette_serial": "PAL-2025-00002"
  },
  {
    "tag_id": "RFID9999",
    "label": "Tag Libre #9999",
    "status": "ACTIVE",
    "assigned_to_palette": false,
    "palette_serial": null
  }
]
```

### Explication des champs

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | Identifiant du tag |
| `tag_id` | String | Numéro RFID (ex: RFID0001) |
| `label` | String | Libellé descriptif |
| `status` | String | ACTIVE / INACTIVE / LOST |
| `assigned_to_palette` | Boolean | Tag assigné ou libre |
| `palette_serial` | String | Numéro palette si assigné |

### Champs écran "Gestion Tags RFID"

- **Liste** : tag_id, label, status
- **Indicateur** : ✅ si assigned, ⚪ si libre
- **Détails** : palette_serial si assigné
- **Bouton** : "Scanner" ou "Créer"
- **Filtre** : Tous / Assignés / Libres

---

## 📦 PALETTES

### Données Palettes Pleines (pour chargement)

```json
[
  {
    "id": "750e8400-e29b-41d4-a716-446655440001",
    "serial_number": "PAL-2025-00001",
    "type": "B12",
    "capacity": 24,
    "status": "AU_CENTRE",
    "is_full": true,
    "rfid_tag_id": "RFID0001",
    "location": "Centre Remplisseur Yopougon"
  },
  {
    "serial_number": "PAL-2025-00002",
    "type": "B12",
    "capacity": 24,
    "status": "AU_CENTRE",
    "is_full": true,
    "rfid_tag_id": "RFID0002"
  },
  {
    "serial_number": "PAL-2025-00003",
    "type": "B28",
    "capacity": 12,
    "status": "AU_CENTRE",
    "is_full": true,
    "rfid_tag_id": "RFID0003"
  }
]
```

### Données Palettes Vides (pour collecte)

```json
[
  {
    "serial_number": "PAL-2025-00050",
    "type": "B12",
    "capacity": 24,
    "status": "AU_DEPOT",
    "is_full": false,
    "rfid_tag_id": "RFID0050",
    "location": "Dépôt GAZ PLUS Adjamé"
  },
  {
    "serial_number": "PAL-2025-00051",
    "type": "B28",
    "capacity": 12,
    "status": "AU_DEPOT",
    "is_full": false,
    "rfid_tag_id": "RFID0051"
  }
]
```

### Explication des champs

| Champ | Type | Description |
|-------|------|-------------|
| `serial_number` | String | Numéro de série unique |
| `type` | String | B6 / B12 / B28 (taille bouteilles) |
| `capacity` | Number | Nombre de bouteilles (B6=48, B12=24, B28=12) |
| `status` | String | AU_CENTRE / EN_CHARGEMENT / EN_ROUTE / AU_DEPOT |
| `is_full` | Boolean | Palette pleine (true) ou vide (false) |
| `rfid_tag_id` | String | Tag RFID associé |
| `location` | String | Localisation actuelle |

### Types de palettes

- **B6** : Bouteilles 6kg → Capacité 48 bouteilles
- **B12** : Bouteilles 12kg → Capacité 24 bouteilles
- **B28** : Bouteilles 28kg → Capacité 12 bouteilles

### Champs écran "Liste Palettes"

- **Item liste** : serial_number, type, status
- **Badge** : Couleur selon status
- **Icône** : 📦 si pleine, ⚪ si vide
- **Détails** : capacity, location, rfid_tag_id

---

## 🚛 BON D'ENLÈVEMENT (VALIDE - Prêt pour chargement)

### Données

```json
{
  "id": "850e8400-e29b-41d4-a716-446655440001",
  "numero_bon": "00000001/11",
  "status": "VALIDE",
  "date_creation": "2024-11-25T08:00:00Z",
  "date_validation": "2024-11-25T08:30:00Z",
  "otp_code": "AB12CD",
  
  "centre_remplisseur": {
    "name": "Centre Remplisseur Yopougon",
    "address": "Zone Industrielle, Boulevard du Gabon",
    "city": "Yopougon",
    "latitude": 5.3364,
    "longitude": -4.0267,
    "phone": "+225 27 23 50 00 00",
    "contact_name": "Konan Kouassi"
  },
  
  "grossiste": {
    "name": "GAZ PLUS Distribution",
    "phone": "+225 27 26 00 00 01",
    "contact_name": "Moussa Diallo"
  },
  
  "depot_principal": {
    "name": "Dépôt Principal GAZ PLUS Adjamé",
    "address": "Adjamé Marché, Rue 12",
    "city": "Adjamé",
    "latitude": 5.3515,
    "longitude": -4.0218,
    "contact_name": "Moussa Diallo",
    "contact_phone": "+225 07 80 00 00 01"
  },
  
  "vehicule": {
    "immatriculation": "AA-1234-BB",
    "chauffeur_nom": "Koné Seydou",
    "chauffeur_phone": "+225 07 90 00 00 01"
  },
  
  "palettes_count": 0,
  "palettes_to_load": 5,
  "instructions": "Livraison standard. Appeler avant arrivée."
}
```

### Explication des champs

| Champ | Type | Description |
|-------|------|-------------|
| `numero_bon` | String | Numéro unique du bon (format: XXXXXXXX/MM) |
| `status` | String | VALIDE / EN_CHARGEMENT / EN_ROUTE / EN_LIVRAISON / TERMINE |
| `otp_code` | String | Code 6 caractères pour validation finale |
| `centre_remplisseur` | Object | Centre de départ |
| `grossiste` | Object | Client grossiste |
| `depot_principal` | Object | Destination finale |
| `vehicule` | Object | Infos camion et chauffeur |
| `palettes_count` | Number | Palettes déjà chargées |
| `palettes_to_load` | Number | Palettes à charger au total |
| `instructions` | String | Instructions particulières |

### Champs écran "Liste Mes Bons"

- **Titre** : 📋 Bon #`numero_bon`
- **Badge** : `status` avec couleur
  - VALIDE = vert
  - EN_ROUTE = bleu
  - EN_LIVRAISON = orange
  - TERMINE = gris
- **Infos** : 
  - Centre : `centre_remplisseur.name`
  - Destination : `depot_principal.name`
  - Palettes : `palettes_count`/`palettes_to_load`
- **Bouton** : 
  - "Démarrer Chargement" si VALIDE
  - "Continuer Tournée" si EN_ROUTE

### Champs écran "Détails Bon"

- **En-tête** :
  - Numéro : `numero_bon`
  - Status : `status`
  - Date : `date_creation`
  
- **Centre (Départ)** :
  - Nom : `centre_remplisseur.name`
  - Adresse : `centre_remplisseur.address`
  - Contact : `centre_remplisseur.contact_name`
  - Tél : `centre_remplisseur.phone`
  
- **Destination** :
  - Nom : `depot_principal.name`
  - Adresse : `depot_principal.address`
  - Contact : `depot_principal.contact_name`
  - Tél : `depot_principal.contact_phone`
  
- **Véhicule** :
  - Immatriculation : `vehicule.immatriculation`
  - Chauffeur : `vehicule.chauffeur_nom`
  
- **Progression** :
  - Barre : `palettes_count` / `palettes_to_load`
  - Texte : "X/Y palettes"

---

## 📦 ÉCRAN CHARGEMENT

### Champs à afficher

```
┌────────────────────────────────────┐
│  ← Chargement  Bon #00000001/11    │
├────────────────────────────────────┤
│                                    │
│  📊 Progression: 3/5 palettes      │  ← palettes_count / palettes_to_load
│  ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░  60%        │  ← Barre de progression
│                                    │
│  📷 SCANNER TAG RFID               │
│  [Input RFID____] [Scanner]       │  ← Input pour tag_id
│                                    │
│  ✅ Palettes chargées:             │
│  ┌──────────────────────────────┐ │
│  │ ✓ PAL-2025-00001 (B12)       │ │  ← serial_number (type)
│  │   RFID0001 - 10:05           │ │  ← rfid_tag_id - heure
│  │                                │ │
│  │ ✓ PAL-2025-00002 (B12)       │ │
│  │   RFID0002 - 10:08           │ │
│  └──────────────────────────────┘ │
│                                    │
│  [Terminer et Partir]             │  ← Actif si count = to_load
│                                    │
└────────────────────────────────────┘
```

### Données à gérer

**Palette scannée (après flash)** :
```json
{
  "success": true,
  "palette": {
    "serial_number": "PAL-2025-00001",
    "type": "B12",
    "rfid_tag_id": "RFID0001",
    "status": "EN_CHARGEMENT"
  },
  "palettes_count": 1,
  "scan_time": "10:05"
}
```

---

## 🚛 BON EN ROUTE (Avec tournée)

### Données

```json
{
  "id": "850e8400-e29b-41d4-a716-446655440002",
  "numero_bon": "00000002/11",
  "status": "EN_ROUTE",
  "date_depart": "2024-11-24T10:00:00Z",
  "palettes_count": 8,
  
  "livraisons": [
    {
      "id": "c50e8400-e29b-41d4-a716-446655440001",
      "ordre": 1,
      "status": "LIVREE",
      "depot": {
        "name": "Dépôt Principal SUPER GAZ Abobo",
        "address": "Abobo Gare, Avenue Principale",
        "latitude": 5.4167,
        "longitude": -4.0208,
        "contact_name": "Ibrahim Coulibaly",
        "contact_phone": "+225 07 80 00 00 03"
      },
      "palettes_a_livrer": 5,
      "palettes_livrees": 5,
      "date_livraison": "2024-11-24T11:30:00Z"
    },
    {
      "ordre": 2,
      "status": "EN_COURS",
      "depot": {
        "name": "Espace Gaz Moderne PK18",
        "address": "Abobo PK18",
        "latitude": 5.4250,
        "longitude": -4.0150,
        "contact_name": "Adama Sanogo",
        "contact_phone": "+225 05 00 00 00 02"
      },
      "palettes_a_livrer": 3,
      "palettes_livrees": 0,
      "date_arrivee": "2024-11-24T12:15:00Z"
    }
  ],
  
  "collectes": [
    {
      "type": "B12",
      "quantite_bouteilles": 24,
      "palette_serial": "PAL-2025-00080",
      "rfid_tag_id": "RFID0080",
      "depot_nom": "Dépôt Principal SUPER GAZ Abobo",
      "date_collecte": "2024-11-24T11:25:00Z"
    }
  ]
}
```

### Champs écran "Tournée"

```
┌────────────────────────────────────┐
│  ← Tournée  Bon #00000002/11       │
├────────────────────────────────────┤
│  🗺️ Itinéraire (2 stops)           │
│                                    │
│  1. ✅ Dépôt SUPER GAZ Abobo       │  ← ordre. status depot.name
│     5 palettes livrées             │  ← palettes_livrees
│     ✓ Terminé à 11:30              │  ← date_livraison
│                                    │
│  2. 📍 Boutique PK18               │  ← ordre. (📍 = EN_COURS)
│     [EN COURS]                     │  ← status
│     Arrivé à: 12:15                │  ← date_arrivee
│     Contact: Adama Sanogo          │  ← depot.contact_name
│     Tel: +225 05 00 00 00 02      │  ← depot.contact_phone
│                                    │
│     Palettes à livrer: 3           │  ← palettes_a_livrer
│     [📷 Flasher Déchargement]     │
│                                    │
│     Vides collectés: 1             │  ← collectes.length
│     [📷 Flasher Vides]            │
│                                    │
└────────────────────────────────────┘
```

### Status livraison

- **EN_ATTENTE** : ⏳ Pas encore arrivé
- **EN_COURS** : 📍 En cours (affiché en orange)
- **LIVREE** : ✅ Terminée (affiché en vert)

---

## 📍 ÉCRAN LIVRAISON (Déchargement)

### Champs à afficher

```
┌────────────────────────────────────┐
│  ← Déchargement  Stop #1           │
├────────────────────────────────────┤
│  📍 Dépôt SUPER GAZ Abobo          │  ← depot.name
│  👤 Contact: Ibrahim Coulibaly      │  ← depot.contact_name
│  📞 +225 07 80 00 00 03            │  ← depot.contact_phone
│                                    │
│  📊 À décharger: 5 palettes        │  ← palettes_a_livrer
│  ✅ Déchargées: 3 palettes         │  ← palettes_livrees
│  ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░  60%        │
│                                    │
│  📷 SCANNER PALETTE                │
│  [Input RFID____] [Décharger]     │
│                                    │
│  ✅ Déchargées:                    │
│  ┌──────────────────────────────┐ │
│  │ ✓ PAL-2025-00001 (B12) 11:05 │ │  ← serial (type) heure
│  │ ✓ PAL-2025-00002 (B12) 11:08 │ │
│  │ ✓ PAL-2025-00003 (B28) 11:12 │ │
│  └──────────────────────────────┘ │
│                                    │
│  [Terminer et Signer]             │  ← Actif si tout déchargé
│                                    │
└────────────────────────────────────┘
```

### Données palette déchargée

```json
{
  "success": true,
  "palette": {
    "serial_number": "PAL-2025-00001",
    "type": "B12",
    "rfid_tag_id": "RFID0001",
    "status": "AU_DEPOT"
  },
  "palettes_livrees": 3,
  "palettes_restantes": 2,
  "scan_time": "11:05"
}
```

---

## 🔄 ÉCRAN COLLECTE VIDES

### Champs à afficher

```
┌────────────────────────────────────┐
│  ← Collecte Vides  Stop #1         │
├────────────────────────────────────┤
│  📍 Dépôt SUPER GAZ Abobo          │  ← depot.name
│                                    │
│  🔄 Palettes vides: 5 collectées   │  ← collectes.length
│                                    │
│  📷 SCANNER PALETTE VIDE           │
│  [Input RFID____]                 │
│                                    │
│  Type: [B12 ▼]                    │  ← Select: B6/B12/B28
│  Bouteilles: [24]                 │  ← Input nombre
│                                    │
│  [Collecter]                       │
│                                    │
│  ✅ Collectées:                    │
│  ┌──────────────────────────────┐ │
│  │ ✓ PAL-2025-00050 (B12 x24)   │ │  ← serial (type xQté)
│  │ ✓ PAL-2025-00051 (B28 x12)   │ │
│  │ ✓ PAL-2025-00052 (B6 x48)    │ │
│  └──────────────────────────────┘ │
│                                    │
│  📊 Total: 84 bouteilles vides     │  ← Somme quantités
│                                    │
└────────────────────────────────────┘
```

### Données collecte vide

```json
{
  "success": true,
  "collecte": {
    "palette_serial": "PAL-2025-00050",
    "type": "B12",
    "quantite_bouteilles": 24,
    "rfid_tag_id": "RFID0050",
    "depot_nom": "Dépôt SUPER GAZ Abobo"
  },
  "total_collectes": 5,
  "total_bouteilles": 84
}
```

---

## ✍️ ÉCRAN SIGNATURE

### Champs à afficher

```
┌────────────────────────────────────┐
│  ← Signature  Livraison Stop #1    │
├────────────────────────────────────┤
│  ✅ Résumé Livraison                │
│  • 5 palettes livrées              │  ← palettes_livrees
│  • 5 palettes vides collectées     │  ← collectes.length
│  • Durée: 30 minutes               │  ← Calculé
│                                    │
│  👤 Récepteur:                      │
│  Nom: [Ibrahim Coulibaly_______]   │  ← Input (pré-rempli contact)
│  Tel: [+225 07 80 00 00 03_____]   │  ← Input (pré-rempli)
│                                    │
│  ✍️ Signature:                      │
│  ┌──────────────────────────────┐ │
│  │                                │ │
│  │    (zone de dessin)            │ │  ← Canvas pour signer
│  │                                │ │
│  └──────────────────────────────┘ │
│  [Effacer]                         │
│                                    │
│  📝 Observations:                   │
│  [Livraison OK_______________]     │  ← TextArea
│                                    │
│  [✓ Confirmer et Continuer]       │
│                                    │
└────────────────────────────────────┘
```

### Données à envoyer

```json
{
  "recepteur_nom": "Ibrahim Coulibaly",
  "recepteur_phone": "+225 07 80 00 00 03",
  "signature_base64": "data:image/png;base64,iVBORw0KGg...",
  "observations": "Livraison OK",
  "date_signature": "2024-11-24T11:30:00Z"
}
```

---

## 🗺️ ÉCRAN ITINÉRAIRE

### Données

```json
{
  "depart": {
    "name": "Centre Remplisseur Yopougon",
    "latitude": 5.3364,
    "longitude": -4.0267,
    "departed_at": "2024-11-25T10:00:00Z"
  },
  
  "stops": [
    {
      "ordre": 1,
      "type": "LIVRAISON",
      "depot": {
        "name": "Dépôt SUPER GAZ Abobo",
        "address": "Abobo Gare, Avenue Principale",
        "latitude": 5.4167,
        "longitude": -4.0208,
        "contact": "Ibrahim Coulibaly",
        "phone": "+225 07 80 00 00 03"
      },
      "palettes": 5,
      "status": "EN_COURS",
      "distance_km": 2.3
    },
    {
      "ordre": 2,
      "type": "LIVRAISON",
      "depot": {
        "name": "Espace Gaz Moderne PK18",
        "latitude": 5.4250,
        "longitude": -4.0150
      },
      "palettes": 3,
      "status": "EN_ATTENTE",
      "distance_km": 1.8
    }
  ],
  
  "current_position": {
    "latitude": 5.3800,
    "longitude": -4.0200,
    "speed": 45.5,
    "heading": 120,
    "timestamp": "2024-11-25T10:30:00Z"
  },
  
  "total_distance_km": 4.1,
  "stops_completed": 0,
  "stops_total": 2
}
```

### Champs carte

- **Marqueur départ** : `depart` (vert)
- **Marqueurs stops** : `stops[]` (orange si EN_COURS, rouge si EN_ATTENTE, vert si LIVREE)
- **Position actuelle** : `current_position` (bleu avec direction)
- **Ligne trajet** : Relier tous les points

### Infos à afficher

- **Distance totale** : `total_distance_km` km
- **Stops** : `stops_completed` / `stops_total`
- **Vitesse** : `current_position.speed` km/h
- **Prochain stop** : Premier EN_ATTENTE ou EN_COURS

---

## 📊 STATUTS ET COULEURS

### Bon d'Enlèvement

| Status | Badge | Couleur | Icône |
|--------|-------|---------|-------|
| CREATION | BROUILLON | Gris | 📝 |
| VALIDE | PRÊT | Vert | ✅ |
| EN_CHARGEMENT | CHARGEMENT | Bleu clair | 📦 |
| EN_ROUTE | EN ROUTE | Bleu | 🚛 |
| EN_LIVRAISON | LIVRAISON | Orange | 📍 |
| TERMINE | TERMINÉ | Vert foncé | ✔️ |
| ANNULE | ANNULÉ | Rouge | ❌ |

### Palette

| Status | Badge | Couleur |
|--------|-------|---------|
| AU_CENTRE | Au centre | Vert |
| EN_CHARGEMENT | Chargement | Bleu clair |
| EN_ROUTE_LIVRAISON | En route | Bleu |
| AU_DEPOT | Au dépôt | Orange |
| EN_ROUTE_RETOUR | Retour | Violet |

### Livraison

| Status | Badge | Couleur | Icône |
|--------|-------|---------|-------|
| EN_ATTENTE | En attente | Gris | ⏳ |
| EN_COURS | En cours | Orange | 📍 |
| LIVREE | Livrée | Vert | ✅ |

---

## 🔢 TYPES DE BOUTEILLES

| Type | Poids | Capacité Palette | Utilisation |
|------|-------|------------------|-------------|
| **B6** | 6 kg | 48 bouteilles | Ménages |
| **B12** | 12 kg | 24 bouteilles | Restaurants |
| **B28** | 28 kg | 12 bouteilles | Industries |

---

## 📱 RÉSUMÉ DES ÉCRANS

### 1. **Login**
- Email, Password
- Bouton "Se connecter"

### 2. **Liste Mes Bons**
- Cards avec : numero_bon, status, centre, destination
- Palettes : count/total
- Bouton action selon status

### 3. **Détails Bon**
- Toutes infos bon
- Centre (départ)
- Destination
- Véhicule
- Progression

### 4. **Chargement**
- Scanner RFID (input)
- Liste palettes chargées
- Barre progression
- Bouton "Partir"

### 5. **Tournée**
- Liste stops numérotés
- Status chaque stop
- Infos contact
- Boutons actions

### 6. **Livraison**
- Scanner déchargement
- Liste déchargées
- Progression
- Bouton "Terminer et Signer"

### 7. **Collecte Vides**
- Scanner palette vide
- Select type (B6/B12/B28)
- Input quantité
- Liste collectées
- Total bouteilles

### 8. **Signature**
- Résumé livraison
- Input récepteur
- Canvas signature
- TextArea observations
- Bouton "Confirmer"

### 9. **Itinéraire (Carte)**
- Carte avec markers
- Ligne trajet
- Position actuelle
- Infos distance/vitesse

### 10. **Gestion Tags RFID**
- Liste tags
- Scanner/Créer
- Assigner à palette
- Filtres

---

## ✅ DONNÉES DISPONIBLES POUR TESTS

- **1 Chauffeur** : Koné Seydou
- **10 Tags RFID** : RFID0001 à RFID0005 (assignés), RFID9998-9999 (libres)
- **8 Palettes** : 5 pleines au centre, 3 vides au dépôt
- **2 Bons** : 1 VALIDE (à charger), 1 EN_ROUTE (avec 2 livraisons)
- **5 Collectes vides** : Déjà effectuées sur bon 2

---

**Ce document contient toutes les structures de données nécessaires pour créer les écrans de l'application mobile ! 📱**

