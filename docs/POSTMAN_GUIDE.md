# 📡 GUIDE POSTMAN - GAZTRACKER API

Ce guide vous aide à tester l'API GazTracker avec Postman.

---

## 🚀 DÉMARRER L'API

### 1. Lancer le serveur FastAPI

```bash
# Depuis la racine du projet
cd C:\Users\Schad225\Documents\Projets\gaztracker

# Lancer avec uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Résultat attendu** :
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2. Vérifier l'API

Ouvrez votre navigateur : http://localhost:8000

**Vous devriez voir** :
```json
{
  "name": "GazTracker",
  "version": "1.0.0",
  "environment": "development",
  "docs": "/docs",
  "status": "healthy"
}
```

### 3. Accéder à la documentation Swagger

Ouvrez : http://localhost:8000/docs

Vous verrez toutes les routes API disponibles avec une interface interactive.

---

## 📚 ROUTES API DISPONIBLES

### 🏢 HIÉRARCHIE

#### **Groupes** (`/api/v1/groupes`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/v1/groupes` | Créer un groupe |
| GET | `/api/v1/groupes` | Lister tous les groupes |
| GET | `/api/v1/groupes/count` | Compter les groupes |
| GET | `/api/v1/groupes/{id}` | Obtenir un groupe avec stats |
| PATCH | `/api/v1/groupes/{id}` | Modifier un groupe |
| DELETE | `/api/v1/groupes/{id}` | Supprimer un groupe |
| POST | `/api/v1/groupes/{id}/activate` | Activer un groupe |
| POST | `/api/v1/groupes/{id}/deactivate` | Désactiver un groupe |

#### **Centres Remplisseurs** (`/api/v1/centres-remplisseurs`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/v1/centres-remplisseurs` | Créer un centre |
| GET | `/api/v1/centres-remplisseurs` | Lister tous les centres |
| GET | `/api/v1/centres-remplisseurs/nearby` | Centres à proximité (GPS) |
| GET | `/api/v1/centres-remplisseurs/{id}` | Obtenir un centre avec stats |
| PATCH | `/api/v1/centres-remplisseurs/{id}` | Modifier un centre |
| DELETE | `/api/v1/centres-remplisseurs/{id}` | Supprimer un centre |
| POST | `/api/v1/centres-remplisseurs/{id}/activate` | Activer un centre |
| POST | `/api/v1/centres-remplisseurs/{id}/deactivate` | Désactiver un centre |

#### **Dépôts** (`/api/v1/depots`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/v1/depots` | Créer un dépôt |
| GET | `/api/v1/depots` | Lister tous les dépôts |
| GET | `/api/v1/depots/locations` | Locations GPS des dépôts |
| GET | `/api/v1/depots/nearby` | Dépôts à proximité (GPS) |
| GET | `/api/v1/depots/{id}` | Obtenir un dépôt avec stats |
| PATCH | `/api/v1/depots/{id}` | Modifier un dépôt |
| DELETE | `/api/v1/depots/{id}` | Supprimer un dépôt |
| POST | `/api/v1/depots/{id}/set-main` | Définir comme dépôt principal |

### 🚛 WORKFLOW BON D'ENLÈVEMENT

#### **Bons d'Enlèvement** (`/api/v1/bons-enlevement`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/v1/bons-enlevement` | Créer un bon d'enlèvement |
| GET | `/api/v1/bons-enlevement` | Lister tous les bons |
| GET | `/api/v1/bons-enlevement/{id}` | Obtenir un bon avec stats |
| PATCH | `/api/v1/bons-enlevement/{id}` | Modifier un bon (CREATION only) |
| POST | `/api/v1/bons-enlevement/{id}/valider` | Valider le bon (→ VALIDE) |
| POST | `/api/v1/bons-enlevement/{id}/start-chargement` | Démarrer chargement (→ EN_CHARGEMENT) |
| POST | `/api/v1/bons-enlevement/{id}/depart` | Marquer départ (→ EN_ROUTE) |
| POST | `/api/v1/bons-enlevement/{id}/start-livraison` | Démarrer livraisons (→ EN_LIVRAISON) |
| POST | `/api/v1/bons-enlevement/{id}/terminer` | Terminer bon (→ TERMINE) |
| POST | `/api/v1/bons-enlevement/{id}/annuler` | Annuler le bon |

---

## 🧪 SCÉNARIOS DE TEST

### Scénario 1 : Tester la Hiérarchie

#### 1.1 Lister les Groupes

```http
GET http://localhost:8000/api/v1/groupes
```

**Réponse attendue** (si seed exécuté) :
```json
[
  {
    "id": "...",
    "name": "Pétroci Holding",
    "code": "PETROCI",
    "is_active": true
  },
  ...
]
```

#### 1.2 Obtenir un Groupe avec Stats

```http
GET http://localhost:8000/api/v1/groupes/{groupe_id}
```

**Réponse** :
```json
{
  "id": "...",
  "name": "Pétroci Holding",
  "code": "PETROCI",
  "grand_distributeurs_count": 2,
  ...
}
```

#### 1.3 Lister les Centres Remplisseurs

```http
GET http://localhost:8000/api/v1/centres-remplisseurs
```

#### 1.4 Centres à Proximité

```http
GET http://localhost:8000/api/v1/centres-remplisseurs/nearby?latitude=5.3364&longitude=-4.0267&radius_km=20
```

### Scénario 2 : Workflow Bon d'Enlèvement Complet

#### 2.1 Créer un Bon d'Enlèvement

```http
POST http://localhost:8000/api/v1/bons-enlevement
Content-Type: application/json

{
  "centre_remplisseur_id": "...",
  "grossiste_id": "...",
  "depot_principal_id": "...",
  "vehicule_immatriculation": "AA-1234-BB",
  "chauffeur_nom": "Koné Seydou",
  "chauffeur_societe": "Transport Express",
  "chauffeur_phone": "+225 07 90 00 00 01"
}
```

**Réponse** : Status CREATION avec `numero_bon` généré automatiquement

#### 2.2 Valider le Bon

```http
POST http://localhost:8000/api/v1/bons-enlevement/{bon_id}/valider
Content-Type: application/json

{
  "validateur_centre_id": "...",
  "observations": "Bon validé pour expédition"
}
```

**Réponse** : Status VALIDE + `otp_code` généré

#### 2.3 Démarrer le Chargement

```http
POST http://localhost:8000/api/v1/bons-enlevement/{bon_id}/start-chargement
Content-Type: application/json

{
  "palette_ids": [
    "palette_id_1",
    "palette_id_2",
    "palette_id_3"
  ],
  "observations": "Chargement de 3 palettes B12"
}
```

**Réponse** : Status EN_CHARGEMENT

#### 2.4 Marquer le Départ

```http
POST http://localhost:8000/api/v1/bons-enlevement/{bon_id}/depart
Content-Type: application/json

{
  "date_depart": "2024-11-20T08:00:00Z",
  "observations": "Départ vers Adjamé"
}
```

**Réponse** : Status EN_ROUTE

#### 2.5 Démarrer les Livraisons

```http
POST http://localhost:8000/api/v1/bons-enlevement/{bon_id}/start-livraison
```

**Réponse** : Status EN_LIVRAISON

#### 2.6 Terminer le Bon

```http
POST http://localhost:8000/api/v1/bons-enlevement/{bon_id}/terminer
Content-Type: application/json

{
  "recepteur_final_id": "...",
  "date_arrivee_finale": "2024-11-20T14:00:00Z",
  "otp_code": "123456",
  "observations": "Livraison complétée avec succès"
}
```

**Réponse** : Status TERMINE

---

## 🔍 PARAMÈTRES DE FILTRAGE

### Lister avec Filtres

```http
GET http://localhost:8000/api/v1/groupes?skip=0&limit=10&is_active=true&search=Petrci
```

**Paramètres disponibles** :
- `skip`: Nombre d'enregistrements à sauter (pagination)
- `limit`: Nombre max d'enregistrements à retourner
- `is_active`: Filtrer par statut actif
- `search`: Recherche par nom ou code

### Filtrer les Bons d'Enlèvement

```http
GET http://localhost:8000/api/v1/bons-enlevement?status=VALIDE&centre_id=...&date_from=2024-11-01&limit=50
```

**Paramètres** :
- `status`: CREATION, VALIDE, EN_CHARGEMENT, EN_ROUTE, EN_LIVRAISON, TERMINE, ANNULE
- `centre_id`: UUID du centre remplisseur
- `grossiste_id`: UUID du grossiste
- `date_from`, `date_to`: Plage de dates
- `search`: Recherche par numéro, chauffeur, véhicule

---

## 💡 TIPS POSTMAN

### 1. Créer un Environment

Dans Postman, créez un environment "GazTracker Local" :

```
BASE_URL = http://localhost:8000
API_V1_PREFIX = /api/v1
```

Utilisez `{{BASE_URL}}{{API_V1_PREFIX}}/groupes` dans vos requêtes.

### 2. Sauvegarder les IDs

Après avoir créé un groupe, sauvegardez son ID :

```javascript
// Dans Tests tab de Postman
var jsonData = pm.response.json();
pm.environment.set("groupe_id", jsonData.id);
```

Réutilisez : `{{groupe_id}}`

### 3. Collection Postman

Organisez vos requêtes par dossiers :
- 📁 Hiérarchie
  - 📁 Groupes
  - 📁 Centres Remplisseurs
  - 📁 Dépôts
- 📁 Workflow Bon d'Enlèvement
- 📁 Workflow Bon de Réception Retour

---

## ⚠️ CODES D'ERREUR

| Code | Signification |
|------|---------------|
| 200 | OK - Succès |
| 201 | Created - Ressource créée |
| 204 | No Content - Suppression réussie |
| 400 | Bad Request - Validation échouée |
| 404 | Not Found - Ressource introuvable |
| 409 | Conflict - Duplicata (code/email) |
| 422 | Unprocessable Entity - Erreur validation Pydantic |
| 500 | Internal Server Error |

---

## 🐛 DÉPANNAGE

### Problème : 404 Not Found

- Vérifier que le serveur est bien lancé
- Vérifier l'URL : http://localhost:8000 (pas http://127.0.0.1:8000)
- Vérifier le préfixe `/api/v1/`

### Problème : 422 Validation Error

- Vérifier le format JSON
- Vérifier les champs requis
- Vérifier les types de données (UUID, dates, etc.)

### Problème : 409 Conflict

- Le code ou l'email existe déjà
- Utiliser un code/email différent

### Problème : 400 Business Rule

- Vérifier l'état de la ressource
- Exemple : Ne peut valider qu'un bon en CREATION

---

## 📖 DOCUMENTATION INTERACTIVE

La meilleure façon de tester l'API est via **Swagger UI** :

http://localhost:8000/docs

**Avantages** :
- ✅ Interface interactive
- ✅ Tous les endpoints visibles
- ✅ Schémas de données affichés
- ✅ Tester directement depuis le navigateur
- ✅ Voir les exemples de réponses

---

## 🎯 PROCHAINES ÉTAPES

Une fois l'API testée avec succès :

1. **Créer une collection Postman complète**
2. **Tester les workflows de bout en bout**
3. **Ajouter tests automatisés (pytest)**
4. **Documenter les cas d'erreur**
5. **Créer le frontend React/Vue**

---

**Date:** 20 novembre 2024  
**Version API:** v1.0  
**Status:** ✅ Prêt pour tests Postman

