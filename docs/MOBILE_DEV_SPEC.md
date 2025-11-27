# 📱 SPÉCIFICATIONS - APPLICATION MOBILE CHAUFFEUR

## 🎯 Vue d'Ensemble

Application mobile pour les **chauffeurs** permettant de :
1. ✅ Gérer les tags RFID (CRUD)
2. ✅ Consulter les palettes avec tags
3. ✅ Voir ses bons d'enlèvement assignés
4. ✅ Charger les palettes (flash RFID)
5. ✅ Confirmer livraisons (flash RFID)
6. ✅ Collecter palettes vides (flash RFID)
7. ✅ Suivre les détails de trajet

---

## 📐 ARCHITECTURE

```
┌─────────────────────────────────────┐
│   APPLICATION MOBILE (React Native) │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Écran: Mes Enlèvements      │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Écran: Chargement RFID      │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Écran: Tournée Livraison    │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Écran: Collecte Vides       │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Écran: Gestion Tags RFID    │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
            │
            │ REST API
            ▼
┌─────────────────────────────────────┐
│      BACKEND GAZTRACKER API         │
│      http://api.gaztracker.ci       │
└─────────────────────────────────────┘
```

---

## 🔐 AUTHENTIFICATION

### Endpoint Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "chauffeur1@transport.ci",
  "password": "Chauf@123"
}
```

**Réponse 200** :
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

### Headers à utiliser

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

---

## 📦 1. GESTION TAGS RFID

### 1.1 Lister les tags RFID

```http
GET /api/v1/rfid-tags?status=ACTIVE&skip=0&limit=50
Authorization: Bearer {token}
```

**Réponse 200** :
```json
{
  "items": [
    {
      "id": "650e8400-e29b-41d4-a716-446655440001",
      "tag_id": "RFID0001",
      "label": "Tag Palette #0001",
      "status": "ACTIVE",
      "assigned_to_palette": true,
      "palette": {
        "id": "750e8400-e29b-41d4-a716-446655440001",
        "serial_number": "PAL-2025-00001",
        "type": "B12",
        "status": "AU_CENTRE"
      },
      "created_at": "2024-11-20T08:00:00Z",
      "last_scanned_at": "2024-11-25T10:30:00Z"
    },
    {
      "id": "650e8400-e29b-41d4-a716-446655440002",
      "tag_id": "RFID0002",
      "label": "Tag Palette #0002",
      "status": "ACTIVE",
      "assigned_to_palette": false,
      "palette": null,
      "created_at": "2024-11-20T08:05:00Z",
      "last_scanned_at": null
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 50
}
```

### 1.2 Scanner un tag RFID (Vérification)

```http
POST /api/v1/rfid-tags/scan
Authorization: Bearer {token}
Content-Type: application/json

{
  "tag_id": "RFID0001"
}
```

**Réponse 200** :
```json
{
  "tag": {
    "id": "650e8400-e29b-41d4-a716-446655440001",
    "tag_id": "RFID0001",
    "status": "ACTIVE",
    "assigned_to_palette": true
  },
  "palette": {
    "id": "750e8400-e29b-41d4-a716-446655440001",
    "serial_number": "PAL-2025-00001",
    "reference_code": "REF-0001",
    "type": "B12",
    "capacity": 24,
    "status": "AU_CENTRE",
    "is_full": true,
    "current_location": "Centre Remplisseur Yopougon"
  },
  "scan_timestamp": "2024-11-25T14:30:00Z"
}
```

### 1.3 Créer un tag RFID

```http
POST /api/v1/rfid-tags
Authorization: Bearer {token}
Content-Type: application/json

{
  "tag_id": "RFID9999",
  "label": "Nouveau Tag Test"
}
```

**Réponse 201** :
```json
{
  "id": "650e8400-e29b-41d4-a716-446655449999",
  "tag_id": "RFID9999",
  "label": "Nouveau Tag Test",
  "status": "ACTIVE",
  "assigned_to_palette": false,
  "created_at": "2024-11-25T14:35:00Z"
}
```

### 1.4 Associer tag à palette

```http
POST /api/v1/rfid-tags/{tag_id}/assign-palette
Authorization: Bearer {token}
Content-Type: application/json

{
  "palette_id": "750e8400-e29b-41d4-a716-446655440010"
}
```

**Réponse 200** :
```json
{
  "message": "Tag RFID0001 assigné à palette PAL-2025-00010",
  "tag": {
    "id": "650e8400-e29b-41d4-a716-446655440001",
    "tag_id": "RFID0001",
    "assigned_to_palette": true
  },
  "palette": {
    "id": "750e8400-e29b-41d4-a716-446655440010",
    "serial_number": "PAL-2025-00010",
    "rfid_tag_id": "RFID0001"
  }
}
```

---

## 📋 2. VOIR LES PALETTES

### 2.1 Lister toutes les palettes

```http
GET /api/v1/palettes?skip=0&limit=50
Authorization: Bearer {token}
```

**Réponse 200** :
```json
{
  "items": [
    {
      "id": "750e8400-e29b-41d4-a716-446655440001",
      "serial_number": "PAL-2025-00001",
      "reference_code": "REF-0001",
      "type": "B12",
      "capacity": 24,
      "status": "AU_CENTRE",
      "is_full": true,
      "rfid_tag": {
        "id": "650e8400-e29b-41d4-a716-446655440001",
        "tag_id": "RFID0001",
        "label": "Tag Palette #0001"
      },
      "current_location": {
        "type": "CENTRE",
        "name": "Centre Remplisseur Yopougon"
      },
      "last_updated": "2024-11-25T10:00:00Z"
    },
    {
      "id": "750e8400-e29b-41d4-a716-446655440002",
      "serial_number": "PAL-2025-00002",
      "reference_code": "REF-0002",
      "type": "B28",
      "capacity": 12,
      "status": "EN_ROUTE_LIVRAISON",
      "is_full": true,
      "rfid_tag": {
        "id": "650e8400-e29b-41d4-a716-446655440002",
        "tag_id": "RFID0002",
        "label": "Tag Palette #0002"
      },
      "current_bon": {
        "numero_bon": "00000001/11",
        "chauffeur_nom": "Koné Seydou"
      },
      "last_updated": "2024-11-25T11:00:00Z"
    }
  ],
  "total": 30,
  "skip": 0,
  "limit": 50
}
```

### 2.2 Filtrer palettes par statut

```http
GET /api/v1/palettes?status=AU_CENTRE&is_full=true&limit=20
Authorization: Bearer {token}
```

### 2.3 Rechercher palette par RFID

```http
GET /api/v1/palettes/by-rfid/{tag_id}
Authorization: Bearer {token}
```

**Réponse 200** :
```json
{
  "id": "750e8400-e29b-41d4-a716-446655440001",
  "serial_number": "PAL-2025-00001",
  "type": "B12",
  "capacity": 24,
  "status": "AU_CENTRE",
  "is_full": true,
  "rfid_tag_id": "RFID0001",
  "current_centre_remplisseur": {
    "id": "850e8400-e29b-41d4-a716-446655440001",
    "name": "Centre Remplisseur Yopougon",
    "code": "CR_YOP"
  }
}
```

---

## 🚛 3. MES BONS D'ENLÈVEMENT

### 3.1 Lister mes bons assignés

```http
GET /api/v1/bons-enlevement/my-assignments?status=VALIDE,EN_CHARGEMENT,EN_ROUTE,EN_LIVRAISON
Authorization: Bearer {token}
```

**Réponse 200** :
```json
{
  "items": [
    {
      "id": "850e8400-e29b-41d4-a716-446655440001",
      "numero_bon": "00000001/11",
      "status": "VALIDE",
      "date_creation": "2024-11-25T08:00:00Z",
      "date_validation": "2024-11-25T08:30:00Z",
      "centre_remplisseur": {
        "id": "950e8400-e29b-41d4-a716-446655440001",
        "name": "Centre Remplisseur Yopougon",
        "code": "CR_YOP",
        "address": "Zone Industrielle, Boulevard du Gabon",
        "city": "Yopougon",
        "latitude": 5.3364,
        "longitude": -4.0267,
        "phone": "+225 27 23 50 00 00"
      },
      "grossiste": {
        "id": "a50e8400-e29b-41d4-a716-446655440001",
        "name": "GAZ PLUS Distribution",
        "code": "GP001",
        "phone": "+225 27 26 00 00 01"
      },
      "depot_principal": {
        "id": "b50e8400-e29b-41d4-a716-446655440001",
        "name": "Dépôt Principal GAZ PLUS Adjamé",
        "code": "DP_GP_ADJ",
        "address": "Adjamé Marché, Rue 12",
        "city": "Adjamé",
        "latitude": 5.3515,
        "longitude": -4.0218
      },
      "vehicule": {
        "immatriculation": "AA-1234-BB",
        "chauffeur_nom": "Koné Seydou",
        "chauffeur_phone": "+225 07 90 00 00 01",
        "chauffeur_societe": "Transport Express"
      },
      "palettes_count": 0,
      "palettes_to_load": 5,
      "livraisons": [],
      "livraisons_count": 0,
      "collectes_count": 0,
      "instructions": "Livraison standard. Appeler avant arrivée."
    },
    {
      "id": "850e8400-e29b-41d4-a716-446655440002",
      "numero_bon": "00000002/11",
      "status": "EN_ROUTE",
      "date_creation": "2024-11-24T08:00:00Z",
      "date_chargement": "2024-11-24T09:00:00Z",
      "date_depart": "2024-11-24T10:00:00Z",
      "centre_remplisseur": {
        "name": "Centre Remplisseur Yopougon"
      },
      "grossiste": {
        "name": "SUPER GAZ IVOIRE"
      },
      "palettes_count": 8,
      "livraisons_count": 3,
      "livraisons": [
        {
          "ordre": 1,
          "depot": {
            "name": "Dépôt Principal SUPER GAZ Abobo",
            "address": "Abobo Gare",
            "latitude": 5.4167,
            "longitude": -4.0208
          },
          "status": "EN_ATTENTE",
          "palettes_a_livrer": 5
        },
        {
          "ordre": 2,
          "depot": {
            "name": "Boutique Espace Gaz Moderne PK18",
            "address": "Abobo PK18",
            "latitude": 5.4250,
            "longitude": -4.0150
          },
          "status": "EN_ATTENTE",
          "palettes_a_livrer": 3
        }
      ]
    }
  ],
  "total": 2
}
```

### 3.2 Détails d'un bon

```http
GET /api/v1/bons-enlevement/{bon_id}
Authorization: Bearer {token}
```

**Réponse 200** - Voir structure complète ci-dessus

---

## 📦 4. CHARGEMENT PALETTES (Flash RFID)

### 4.1 Démarrer le chargement

```http
POST /api/v1/bons-enlevement/{bon_id}/start-chargement
Authorization: Bearer {token}
Content-Type: application/json

{
  "palette_ids": [],
  "observations": "Début du chargement"
}
```

**Réponse 200** :
```json
{
  "id": "850e8400-e29b-41d4-a716-446655440001",
  "numero_bon": "00000001/11",
  "status": "EN_CHARGEMENT",
  "date_chargement": "2024-11-25T09:00:00Z",
  "palettes_count": 0,
  "message": "Chargement démarré. Commencez à flasher les palettes."
}
```

### 4.2 Ajouter une palette par flash RFID

```http
POST /api/v1/bons-enlevement/{bon_id}/add-palette-by-rfid
Authorization: Bearer {token}
Content-Type: application/json

{
  "rfid_tag_id": "RFID0001",
  "gps_latitude": 5.3364,
  "gps_longitude": -4.0267
}
```

**Réponse 200** :
```json
{
  "success": true,
  "message": "Palette PAL-2025-00001 ajoutée au chargement",
  "palette": {
    "id": "750e8400-e29b-41d4-a716-446655440001",
    "serial_number": "PAL-2025-00001",
    "type": "B12",
    "capacity": 24,
    "rfid_tag_id": "RFID0001",
    "status": "EN_CHARGEMENT"
  },
  "bon": {
    "numero_bon": "00000001/11",
    "palettes_count": 1,
    "palettes_to_load": 5
  },
  "scan_timestamp": "2024-11-25T09:05:00Z"
}
```

**Erreur 400** (Palette déjà chargée) :
```json
{
  "error": "ALREADY_LOADED",
  "message": "Palette PAL-2025-00001 déjà chargée sur ce bon",
  "details": {
    "palette_serial": "PAL-2025-00001",
    "already_in_bon": true
  }
}
```

**Erreur 400** (Palette non disponible) :
```json
{
  "error": "PALETTE_NOT_AVAILABLE",
  "message": "Palette PAL-2025-00005 n'est pas disponible (status: EN_ROUTE_LIVRAISON)",
  "details": {
    "palette_serial": "PAL-2025-00005",
    "current_status": "EN_ROUTE_LIVRAISON"
  }
}
```

### 4.3 Retirer une palette du chargement

```http
POST /api/v1/bons-enlevement/{bon_id}/remove-palette
Authorization: Bearer {token}
Content-Type: application/json

{
  "palette_id": "750e8400-e29b-41d4-a716-446655440001",
  "reason": "Palette endommagée"
}
```

### 4.4 Voir les palettes chargées

```http
GET /api/v1/bons-enlevement/{bon_id}/palettes
Authorization: Bearer {token}
```

**Réponse 200** :
```json
{
  "bon_numero": "00000001/11",
  "palettes_count": 5,
  "palettes": [
    {
      "id": "750e8400-e29b-41d4-a716-446655440001",
      "serial_number": "PAL-2025-00001",
      "type": "B12",
      "capacity": 24,
      "rfid_tag_id": "RFID0001",
      "status": "EN_CHARGEMENT",
      "loaded_at": "2024-11-25T09:05:00Z"
    },
    {
      "id": "750e8400-e29b-41d4-a716-446655440002",
      "serial_number": "PAL-2025-00002",
      "type": "B12",
      "capacity": 24,
      "rfid_tag_id": "RFID0002",
      "status": "EN_CHARGEMENT",
      "loaded_at": "2024-11-25T09:08:00Z"
    }
  ],
  "by_type": {
    "B6": 0,
    "B12": 5,
    "B28": 0
  }
}
```

### 4.5 Confirmer fin de chargement et partir

```http
POST /api/v1/bons-enlevement/{bon_id}/depart
Authorization: Bearer {token}
Content-Type: application/json

{
  "date_depart": "2024-11-25T10:00:00Z",
  "gps_latitude": 5.3364,
  "gps_longitude": -4.0267,
  "observations": "Départ vers Adjamé avec 5 palettes"
}
```

**Réponse 200** :
```json
{
  "id": "850e8400-e29b-41d4-a716-446655440001",
  "numero_bon": "00000001/11",
  "status": "EN_ROUTE",
  "date_depart": "2024-11-25T10:00:00Z",
  "palettes_count": 5,
  "message": "Bon d'enlèvement en route. Vous pouvez commencer les livraisons."
}
```

---

## 📍 5. LIVRAISONS (Flash RFID)

### 5.1 Démarrer une livraison

```http
POST /api/v1/bons-enlevement/{bon_id}/livraisons/{livraison_id}/start
Authorization: Bearer {token}
Content-Type: application/json

{
  "date_arrivee": "2024-11-25T11:00:00Z",
  "gps_latitude": 5.3515,
  "gps_longitude": -4.0218
}
```

**Réponse 200** :
```json
{
  "id": "c50e8400-e29b-41d4-a716-446655440001",
  "ordre": 1,
  "status": "EN_COURS",
  "depot": {
    "name": "Dépôt Principal GAZ PLUS Adjamé",
    "address": "Adjamé Marché, Rue 12",
    "contact_name": "Moussa Diallo",
    "contact_phone": "+225 07 80 00 00 01"
  },
  "palettes_a_livrer": 5,
  "palettes_livrees": 0,
  "date_arrivee": "2024-11-25T11:00:00Z",
  "message": "Livraison démarrée. Flashez les palettes à décharger."
}
```

### 5.2 Décharger palette (Flash RFID)

```http
POST /api/v1/bons-enlevement/{bon_id}/livraisons/{livraison_id}/unload-palette
Authorization: Bearer {token}
Content-Type: application/json

{
  "rfid_tag_id": "RFID0001",
  "gps_latitude": 5.3515,
  "gps_longitude": -4.0218
}
```

**Réponse 200** :
```json
{
  "success": true,
  "message": "Palette PAL-2025-00001 déchargée",
  "palette": {
    "serial_number": "PAL-2025-00001",
    "type": "B12",
    "rfid_tag_id": "RFID0001",
    "status": "AU_DEPOT"
  },
  "livraison": {
    "ordre": 1,
    "palettes_livrees": 1,
    "palettes_restantes": 4,
    "depot_name": "Dépôt Principal GAZ PLUS Adjamé"
  },
  "scan_timestamp": "2024-11-25T11:05:00Z"
}
```

### 5.3 Terminer la livraison (Signature)

```http
POST /api/v1/bons-enlevement/{bon_id}/livraisons/{livraison_id}/complete
Authorization: Bearer {token}
Content-Type: application/json

{
  "date_depart": "2024-11-25T11:30:00Z",
  "recepteur_nom": "Moussa Diallo",
  "recepteur_phone": "+225 07 80 00 00 01",
  "signature_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "observations": "Livraison effectuée avec succès"
}
```

**Réponse 200** :
```json
{
  "id": "c50e8400-e29b-41d4-a716-446655440001",
  "status": "LIVREE",
  "palettes_livrees": 5,
  "date_livraison": "2024-11-25T11:30:00Z",
  "recepteur": "Moussa Diallo",
  "message": "Livraison terminée avec succès"
}
```

---

## 🔄 6. COLLECTE PALETTES VIDES (Flash RFID)

### 6.1 Démarrer collecte vides

```http
POST /api/v1/bons-enlevement/{bon_id}/livraisons/{livraison_id}/start-collecte
Authorization: Bearer {token}
Content-Type: application/json

{
  "observations": "Début collecte palettes vides"
}
```

### 6.2 Collecter palette vide (Flash RFID)

```http
POST /api/v1/bons-enlevement/{bon_id}/livraisons/{livraison_id}/collect-empty
Authorization: Bearer {token}
Content-Type: application/json

{
  "rfid_tag_id": "RFID0050",
  "type_palette": "B12",
  "quantite_bouteilles_vides": 24,
  "gps_latitude": 5.3515,
  "gps_longitude": -4.0218
}
```

**Réponse 200** :
```json
{
  "success": true,
  "message": "Palette vide PAL-2025-00050 collectée",
  "collecte": {
    "id": "d50e8400-e29b-41d4-a716-446655440001",
    "palette_serial": "PAL-2025-00050",
    "type": "B12",
    "quantite_bouteilles": 24,
    "depot_name": "Dépôt Principal GAZ PLUS Adjamé"
  },
  "total_collectes": 3,
  "scan_timestamp": "2024-11-25T11:20:00Z"
}
```

### 6.3 Voir collectes effectuées

```http
GET /api/v1/bons-enlevement/{bon_id}/collectes
Authorization: Bearer {token}
```

**Réponse 200** :
```json
{
  "bon_numero": "00000001/11",
  "collectes_count": 8,
  "collectes": [
    {
      "id": "d50e8400-e29b-41d4-a716-446655440001",
      "type": "B12",
      "quantite_bouteilles": 24,
      "palette_serial": "PAL-2025-00050",
      "rfid_tag_id": "RFID0050",
      "depot_collecte": "Dépôt Principal GAZ PLUS Adjamé",
      "date_collecte": "2024-11-25T11:20:00Z"
    }
  ],
  "by_type": {
    "B6": 2,
    "B12": 5,
    "B28": 1
  },
  "total_bouteilles": 168
}
```

---

## 🗺️ 7. SUIVI TRAJET

### 7.1 Envoyer position GPS

```http
POST /api/v1/bons-enlevement/{bon_id}/update-position
Authorization: Bearer {token}
Content-Type: application/json

{
  "latitude": 5.3600,
  "longitude": -4.0100,
  "timestamp": "2024-11-25T10:30:00Z",
  "speed": 45.5,
  "heading": 120
}
```

**Réponse 200** :
```json
{
  "message": "Position mise à jour",
  "current_position": {
    "latitude": 5.3600,
    "longitude": -4.0100,
    "timestamp": "2024-11-25T10:30:00Z"
  },
  "distance_to_next_stop": 2.5,
  "eta_minutes": 8
}
```

### 7.2 Obtenir itinéraire

```http
GET /api/v1/bons-enlevement/{bon_id}/itineraire
Authorization: Bearer {token}
```

**Réponse 200** :
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
        "name": "Dépôt Principal GAZ PLUS Adjamé",
        "address": "Adjamé Marché, Rue 12",
        "latitude": 5.3515,
        "longitude": -4.0218,
        "contact": "Moussa Diallo",
        "phone": "+225 07 80 00 00 01"
      },
      "palettes_a_livrer": 5,
      "status": "EN_COURS",
      "distance_km": 2.3,
      "eta": "2024-11-25T11:00:00Z"
    },
    {
      "ordre": 2,
      "type": "LIVRAISON",
      "depot": {
        "name": "Dépôt Secondaire GAZ PLUS Williamsville",
        "address": "Williamsville, Carrefour Solibra",
        "latitude": 5.3892,
        "longitude": -3.9985
      },
      "palettes_a_livrer": 0,
      "status": "EN_ATTENTE",
      "distance_km": 5.1
    }
  ],
  "arrivee": {
    "name": "Dépôt Principal GAZ PLUS Adjamé",
    "latitude": 5.3515,
    "longitude": -4.0218
  },
  "total_distance_km": 7.4,
  "stops_count": 2,
  "stops_completed": 0
}
```

---

## 📊 MOCK DATA POUR DÉVELOPPEMENT

### Mock User (Chauffeur)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Koné Seydou",
  "email": "chauffeur1@transport.ci",
  "role": "CHAUFFEUR",
  "phone": "+225 07 90 00 00 01",
  "avatar_url": null,
  "is_active": true
}
```

### Mock Tags RFID (10 tags)

```json
[
  {"tag_id": "RFID0001", "label": "Tag #0001", "assigned": true, "palette_serial": "PAL-2025-00001"},
  {"tag_id": "RFID0002", "label": "Tag #0002", "assigned": true, "palette_serial": "PAL-2025-00002"},
  {"tag_id": "RFID0003", "label": "Tag #0003", "assigned": true, "palette_serial": "PAL-2025-00003"},
  {"tag_id": "RFID0004", "label": "Tag #0004", "assigned": true, "palette_serial": "PAL-2025-00004"},
  {"tag_id": "RFID0005", "label": "Tag #0005", "assigned": true, "palette_serial": "PAL-2025-00005"},
  {"tag_id": "RFID0050", "label": "Tag #0050", "assigned": true, "palette_serial": "PAL-2025-00050"},
  {"tag_id": "RFID0051", "label": "Tag #0051", "assigned": true, "palette_serial": "PAL-2025-00051"},
  {"tag_id": "RFID0052", "label": "Tag #0052", "assigned": true, "palette_serial": "PAL-2025-00052"},
  {"tag_id": "RFID9998", "label": "Tag #9998", "assigned": false, "palette_serial": null},
  {"tag_id": "RFID9999", "label": "Tag #9999", "assigned": false, "palette_serial": null}
]
```

### Mock Palettes (8 palettes)

```json
[
  {
    "serial_number": "PAL-2025-00001",
    "type": "B12",
    "capacity": 24,
    "status": "AU_CENTRE",
    "is_full": true,
    "rfid_tag_id": "RFID0001"
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
  },
  {
    "serial_number": "PAL-2025-00004",
    "type": "B6",
    "capacity": 48,
    "status": "AU_CENTRE",
    "is_full": true,
    "rfid_tag_id": "RFID0004"
  },
  {
    "serial_number": "PAL-2025-00005",
    "type": "B12",
    "capacity": 24,
    "status": "AU_CENTRE",
    "is_full": true,
    "rfid_tag_id": "RFID0005"
  },
  {
    "serial_number": "PAL-2025-00050",
    "type": "B12",
    "capacity": 24,
    "status": "AU_DEPOT",
    "is_full": false,
    "rfid_tag_id": "RFID0050"
  },
  {
    "serial_number": "PAL-2025-00051",
    "type": "B28",
    "capacity": 12,
    "status": "AU_DEPOT",
    "is_full": false,
    "rfid_tag_id": "RFID0051"
  },
  {
    "serial_number": "PAL-2025-00052",
    "type": "B6",
    "capacity": 48,
    "status": "AU_DEPOT",
    "is_full": false,
    "rfid_tag_id": "RFID0052"
  }
]
```

### Mock Bon d'Enlèvement

Voir section 3.1 ci-dessus pour structure complète.

---

## 🎨 WIREFRAMES ÉCRANS

### Écran 1 : Liste Mes Enlèvements

```
┌────────────────────────────────────┐
│  ← Mes Enlèvements          👤 👋  │
├────────────────────────────────────┤
│                                    │
│  ┌──────────────────────────────┐ │
│  │ 📋 Bon #00000001/11          │ │
│  │ ✅ VALIDE                    │ │
│  │ Centre: Yopougon             │ │
│  │ Destination: GAZ PLUS Adjamé │ │
│  │ Palettes: 0/5 chargées       │ │
│  │ [Démarrer Chargement] ───────→│ │
│  └──────────────────────────────┘ │
│                                    │
│  ┌──────────────────────────────┐ │
│  │ 📋 Bon #00000002/11          │ │
│  │ 🚛 EN_ROUTE                  │ │
│  │ Destination: SUPER GAZ Abobo │ │
│  │ Palettes: 8/8 chargées       │ │
│  │ Livraisons: 0/3 terminées    │ │
│  │ [Continuer Tournée] ─────────→│ │
│  └──────────────────────────────┘ │
│                                    │
└────────────────────────────────────┘
```

### Écran 2 : Chargement RFID

```
┌────────────────────────────────────┐
│  ← Chargement  Bon #00000001/11    │
├────────────────────────────────────┤
│                                    │
│  📊 Progression: 3/5 palettes      │
│  ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░  60%        │
│                                    │
│  ┌──────────────────────────────┐ │
│  │  📷 Scanner Tag RFID          │ │
│  │                                │ │
│  │      [🔍 FLASHER PALETTE]     │ │
│  │                                │ │
│  │  ou saisir manuellement:      │ │
│  │  [RFID____] [Valider]         │ │
│  └──────────────────────────────┘ │
│                                    │
│  ✅ Palettes chargées:             │
│  ┌──────────────────────────────┐ │
│  │ ✓ PAL-2025-00001 (B12) RFID1 │ │
│  │ ✓ PAL-2025-00002 (B12) RFID2 │ │
│  │ ✓ PAL-2025-00003 (B28) RFID3 │ │
│  └──────────────────────────────┘ │
│                                    │
│  [Terminer et Partir] ───────────→ │
│                                    │
└────────────────────────────────────┘
```

### Écran 3 : Tournée Livraison

```
┌────────────────────────────────────┐
│  ← Tournée  Bon #00000001/11       │
├────────────────────────────────────┤
│                                    │
│  🗺️ Itinéraire (2 stops)           │
│                                    │
│  1. ✅ Dépôt GAZ PLUS Adjamé       │
│     5 palettes livrées             │
│     ✓ Terminé à 11:30              │
│                                    │
│  2. 📍 Boutique Williamsville      │
│     [EN COURS]                     │
│     Arrivé à: 12:15                │
│     Contact: Aya Koné              │
│     Tel: +225 07 80 00 00 11       │
│                                    │
│     Palettes à livrer: 3           │
│     [📷 Flasher Déchargement] ────→│
│                                    │
│     Collecte vides: 5 collectées   │
│     [📷 Flasher Vides] ───────────→│
│                                    │
│     [✓ Terminer cette Livraison]  │
│                                    │
└────────────────────────────────────┘
```

### Écran 4 : Déchargement RFID

```
┌────────────────────────────────────┐
│  ← Déchargement  Livraison #1      │
├────────────────────────────────────┤
│                                    │
│  📍 Dépôt GAZ PLUS Adjamé          │
│  👤 Contact: Moussa Diallo          │
│                                    │
│  📊 À décharger: 5 palettes        │
│  ✅ Déchargées: 3 palettes         │
│  ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░  60%        │
│                                    │
│  ┌──────────────────────────────┐ │
│  │  📷 Scanner Palette           │ │
│  │                                │ │
│  │   [🔍 FLASHER POUR DÉCHARGER] │ │
│  │                                │ │
│  └──────────────────────────────┘ │
│                                    │
│  ✅ Déchargées:                    │
│  ┌──────────────────────────────┐ │
│  │ ✓ PAL-2025-00001 (B12) 11:05 │ │
│  │ ✓ PAL-2025-00002 (B12) 11:08 │ │
│  │ ✓ PAL-2025-00003 (B28) 11:12 │ │
│  └──────────────────────────────┘ │
│                                    │
│  🔄 Collecte vides [0] ──────────→ │
│                                    │
│  [Terminer et Signer] ──────────→  │
│                                    │
└────────────────────────────────────┘
```

### Écran 5 : Collecte Vides RFID

```
┌────────────────────────────────────┐
│  ← Collecte Vides  Livraison #1    │
├────────────────────────────────────┤
│                                    │
│  📍 Dépôt GAZ PLUS Adjamé          │
│                                    │
│  🔄 Palettes vides collectées: 5   │
│                                    │
│  ┌──────────────────────────────┐ │
│  │  📷 Scanner Palette Vide      │ │
│  │                                │ │
│  │  [🔍 FLASHER PALETTE VIDE]    │ │
│  │                                │ │
│  │  Type: [B12 ▼]                │ │
│  │  Bouteilles: [24]             │ │
│  └──────────────────────────────┘ │
│                                    │
│  ✅ Collectées:                    │
│  ┌──────────────────────────────┐ │
│  │ ✓ PAL-2025-00050 (B12 x24)   │ │
│  │ ✓ PAL-2025-00051 (B28 x12)   │ │
│  │ ✓ PAL-2025-00052 (B6 x48)    │ │
│  │ ✓ PAL-2025-00053 (B12 x24)   │ │
│  │ ✓ PAL-2025-00054 (B12 x24)   │ │
│  └──────────────────────────────┘ │
│                                    │
│  📊 Total: 132 bouteilles vides    │
│                                    │
│  [Terminer Collecte] ───────────→  │
│                                    │
└────────────────────────────────────┘
```

### Écran 6 : Signature

```
┌────────────────────────────────────┐
│  ← Signature  Livraison #1         │
├────────────────────────────────────┤
│                                    │
│  ✅ Résumé Livraison                │
│  • 5 palettes livrées              │
│  • 5 palettes vides collectées     │
│  • Durée: 30 minutes               │
│                                    │
│  👤 Récepteur:                      │
│  Nom: [Moussa Diallo___________]   │
│  Tel: [+225 07 80 00 00 01_____]   │
│                                    │
│  ✍️ Signature:                      │
│  ┌──────────────────────────────┐ │
│  │                                │ │
│  │                                │ │
│  │         (zone signature)       │ │
│  │                                │ │
│  │                                │ │
│  └──────────────────────────────┘ │
│  [Effacer]                         │
│                                    │
│  📝 Observations:                   │
│  [Livraison OK_______________]     │
│  [____________________________]    │
│                                    │
│  [✓ Confirmer et Continuer] ─────→ │
│                                    │
└────────────────────────────────────┘
```

### Écran 7 : Gestion Tags RFID

```
┌────────────────────────────────────┐
│  ← Tags RFID              [+ Créer]│
├────────────────────────────────────┤
│  🔍 [Rechercher tag________]       │
│                                    │
│  Filtres: [Tous ▼] [Actifs ▼]     │
│                                    │
│  ┌──────────────────────────────┐ │
│  │ 🏷️ RFID0001                   │ │
│  │ Tag Palette #0001             │ │
│  │ ✅ Actif | 📦 Assigné          │ │
│  │ Palette: PAL-2025-00001 (B12) │ │
│  │ Dernier scan: Aujourd'hui 10h │ │
│  └──────────────────────────────┘ │
│                                    │
│  ┌──────────────────────────────┐ │
│  │ 🏷️ RFID0002                   │ │
│  │ Tag Palette #0002             │ │
│  │ ✅ Actif | 📦 Assigné          │ │
│  │ Palette: PAL-2025-00002 (B12) │ │
│  │ Dernier scan: Hier 14h        │ │
│  └──────────────────────────────┘ │
│                                    │
│  ┌──────────────────────────────┐ │
│  │ 🏷️ RFID9999                   │ │
│  │ Tag Libre                     │ │
│  │ ✅ Actif | ⚪ Non assigné      │ │
│  │ [Assigner à Palette] ────────→│ │
│  └──────────────────────────────┘ │
│                                    │
└────────────────────────────────────┘
```

---

## 🔧 DÉVELOPPEMENT OFFLINE

### Créer Mock API Service

```javascript
// mockApiService.js
const MOCK_MODE = true; // Activer pour dev offline

export class ApiService {
  async login(email, password) {
    if (MOCK_MODE) {
      await delay(500); // Simuler latence réseau
      return MOCK_LOGIN_RESPONSE;
    }
    return fetch('/api/v1/auth/login', { /* ... */ });
  }
  
  async scanRFID(tagId) {
    if (MOCK_MODE) {
      await delay(300);
      const palette = MOCK_PALETTES.find(p => p.rfid_tag_id === tagId);
      if (!palette) {
        throw new Error('Tag RFID non trouvé');
      }
      return {
        tag: { tag_id: tagId, status: 'ACTIVE' },
        palette: palette,
        scan_timestamp: new Date().toISOString()
      };
    }
    return fetch('/api/v1/rfid-tags/scan', { /* ... */ });
  }
  
  // ... autres méthodes
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

### Mock Data Constants

```javascript
// mockData.js
export const MOCK_USER = {
  id: "550e8400-e29b-41d4-a716-446655440001",
  name: "Koné Seydou",
  email: "chauffeur1@transport.ci",
  role: "CHAUFFEUR"
};

export const MOCK_BONS = [
  // ... voir section Mock Data ci-dessus
];

export const MOCK_PALETTES = [
  // ... voir section Mock Data ci-dessus
];

export const MOCK_TAGS = [
  // ... voir section Mock Data ci-dessus
];
```

---

## 📱 TECHNOLOGIES RECOMMANDÉES

### Framework
- **React Native** (iOS + Android)
- **Expo** pour faciliter le développement

### Librairies
- **React Navigation** - Navigation
- **React Native Paper** - UI Components
- **React Native Camera** - Scanner RFID/QR
- **React Native Maps** - Cartes et GPS
- **AsyncStorage** - Stockage local
- **Axios** - Requêtes HTTP
- **React Query** - Cache et sync API

### RFID
- **React Native NFC Manager** - Lecture tags NFC/RFID
- Fallback QR Code si NFC non disponible

---

## ✅ CHECKLIST DÉVELOPPEMENT

### Phase 1 : Setup
- [ ] Créer projet React Native
- [ ] Configurer navigation
- [ ] Créer service API avec mock data
- [ ] Tester mock data fonctionne

### Phase 2 : Authentification
- [ ] Écran login
- [ ] Stocker token
- [ ] Gérer session

### Phase 3 : Tags RFID
- [ ] Liste tags
- [ ] Scanner tag (simulation)
- [ ] Créer tag
- [ ] Assigner tag à palette

### Phase 4 : Mes Enlèvements
- [ ] Liste bons assignés
- [ ] Détails d'un bon
- [ ] Filtres par statut

### Phase 5 : Chargement
- [ ] Démarrer chargement
- [ ] Scanner palette (simulation)
- [ ] Liste palettes chargées
- [ ] Confirmer départ

### Phase 6 : Livraisons
- [ ] Itinéraire tournée
- [ ] Démarrer livraison
- [ ] Scanner déchargement
- [ ] Signature électronique
- [ ] Terminer livraison

### Phase 7 : Collecte Vides
- [ ] Scanner palette vide
- [ ] Saisir quantité bouteilles
- [ ] Liste vides collectés
- [ ] Récapitulatif

### Phase 8 : GPS et Carte
- [ ] Afficher carte
- [ ] Position actuelle
- [ ] Itinéraire vers stop
- [ ] Mise à jour position

### Phase 9 : Mode Offline
- [ ] Stocker données localement
- [ ] Queue de synchronisation
- [ ] Gérer conflits

### Phase 10 : Tests
- [ ] Tests unitaires
- [ ] Tests d'intégration
- [ ] Tests sur devices réels

---

## 🚀 DÉMARRAGE RAPIDE

1. **Créer projet** :
```bash
npx create-expo-app gaztracker-mobile
cd gaztracker-mobile
```

2. **Installer dépendances** :
```bash
npm install @react-navigation/native @react-navigation/stack
npm install react-native-paper axios
npm install @react-native-async-storage/async-storage
```

3. **Créer mockApiService.js** avec les données ci-dessus

4. **Commencer par l'écran de login** avec mock data

5. **Tester en mode offline** avant de connecter à l'API réelle

---

## 📞 SUPPORT

Pour questions sur l'API :
- Consulter `API_ROUTES_SUMMARY.md`
- Swagger : http://localhost:8000/docs
- Postman Guide : `POSTMAN_GUIDE.md`

---

**Date** : 25 novembre 2024  
**Version** : 1.0  
**Status** : ✅ Prêt pour développement mobile offline

