# 🚀 DÉMARRAGE RAPIDE - API GAZTRACKER

Guide ultra-rapide pour démarrer et tester l'API en 5 minutes.

---

## ⚡ ÉTAPE 1 : PRÉPARER LA BASE DE DONNÉES (2 min)

```bash
# 1. Appliquer les migrations
alembic upgrade head

# 2. Peupler avec données de test
python scripts/seed_test_data.py
```

✅ **Résultat** : Base de données prête avec données réalistes.

---

## ⚡ ÉTAPE 2 : DÉMARRER L'API (30 sec)

```bash
# Depuis la racine du projet
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Résultat** : API en cours d'exécution sur http://localhost:8000

---

## ⚡ ÉTAPE 3 : TESTER L'API (2 min)

### Option A : Navigateur (Plus simple)

Ouvrez : **http://localhost:8000/docs**

Vous verrez l'interface Swagger interactive avec toutes les routes.

### Option B : Postman

1. Créer une nouvelle requête
2. `GET http://localhost:8000/api/v1/groupes`
3. Cliquer "Send"

**Réponse attendue** :
```json
[
  {
    "id": "...",
    "name": "Pétroci Holding",
    "code": "PETROCI",
    "is_active": true
  }
]
```

---

## 🎯 TEST COMPLET EN 3 REQUÊTES

### 1️⃣ Lister les Groupes

```bash
curl http://localhost:8000/api/v1/groupes
```

### 2️⃣ Lister les Centres Remplisseurs

```bash
curl http://localhost:8000/api/v1/centres-remplisseurs
```

### 3️⃣ Créer un Bon d'Enlèvement

```bash
curl -X POST http://localhost:8000/api/v1/bons-enlevement \
  -H "Content-Type: application/json" \
  -d '{
    "centre_remplisseur_id": "COPIER_ID_DU_CENTRE",
    "grossiste_id": "COPIER_ID_DU_GROSSISTE",
    "vehicule_immatriculation": "AB-1234-CD",
    "chauffeur_nom": "Test Chauffeur",
    "chauffeur_societe": "Test Transport"
  }'
```

---

## 📊 ROUTES PRINCIPALES

| Ressource | Endpoint | Action |
|-----------|----------|--------|
| **Groupes** | `GET /api/v1/groupes` | Lister |
| **Centres** | `GET /api/v1/centres-remplisseurs` | Lister |
| **Dépôts** | `GET /api/v1/depots` | Lister |
| **Bons** | `POST /api/v1/bons-enlevement` | Créer |
| **Bons** | `GET /api/v1/bons-enlevement` | Lister |

---

## 🎨 INTERFACE SWAGGER

L'interface Swagger vous permet de :
- ✅ Voir toutes les routes disponibles
- ✅ Tester les endpoints directement
- ✅ Voir les schémas de données
- ✅ Voir les exemples de requêtes/réponses
- ✅ Télécharger la spécification OpenAPI

**URL** : http://localhost:8000/docs

---

## 🔍 VÉRIFICATIONS RAPIDES

### ✅ Vérifier l'API fonctionne

```bash
curl http://localhost:8000/health
```

**Réponse** :
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### ✅ Vérifier les données

```bash
# Compter les groupes
curl http://localhost:8000/api/v1/groupes/count
# Réponse : {"count": 3}

# Lister centres actifs
curl "http://localhost:8000/api/v1/centres-remplisseurs?is_active=true"
```

---

## 📝 CREDENTIALS DE TEST

Créés par le script de seed :

```
Admin:       admin@gaztracker.ci / Admin@123
Logistique:  logistique@cev3.ci / Log@123
Chauffeur:   chauffeur1@transport.ci / Chauf@123
Grossiste:   contact@gazplus.ci / Gros@123
```

⚠️ **Note** : L'authentification sera ajoutée dans une phase ultérieure.

---

## 🐛 PROBLÈMES COURANTS

### Erreur : "Address already in use"

Le port 8000 est déjà utilisé.

**Solution** :
```bash
# Utiliser un autre port
uvicorn app.main:app --reload --port 8001
```

### Erreur : "No module named 'app'"

Vous n'êtes pas dans le bon répertoire.

**Solution** :
```bash
cd C:\Users\Schad225\Documents\Projets\gaztracker
python -m uvicorn app.main:app --reload
```

### Erreur : Database connection failed

La base de données n'est pas démarrée ou mal configurée.

**Solution** :
1. Vérifier PostgreSQL est en cours d'exécution
2. Vérifier `.env` contient la bonne DATABASE_URL
3. Tester connexion : `psql -U gaztracker -d gaztracker_test`

---

## 📚 DOCUMENTATION COMPLÈTE

Pour plus de détails, consultez :
- **`POSTMAN_GUIDE.md`** - Guide complet Postman avec tous les scénarios
- **`GUIDE_TEST.md`** - Guide de test complet
- **`BACKEND_COMPLETE_README.md`** - Vue d'ensemble backend
- **Swagger UI** - http://localhost:8000/docs

---

## 🎉 C'EST TOUT !

Vous avez maintenant une API fonctionnelle que vous pouvez tester via :
- ✅ Swagger UI (http://localhost:8000/docs)
- ✅ Postman
- ✅ cURL
- ✅ Tout autre client HTTP

**Bon test ! 🚀**

---

**Temps total** : ~5 minutes  
**Niveau** : Débutant  
**Prérequis** : PostgreSQL installé

