# 🧪 GUIDE DE TEST - GAZTRACKER BACKEND

Ce guide vous aide à tester l'infrastructure backend complète de GazTracker.

---

## 📋 PRÉ-REQUIS

1. **PostgreSQL** installé et en cours d'exécution
2. **Redis** installé et en cours d'exécution (optionnel pour cette phase)
3. **Python 3.11+** installé
4. **Variables d'environnement** configurées dans `.env`

---

## 🗄️ ÉTAPE 1 : CONFIGURATION BASE DE DONNÉES

### 1.1 Créer la base de données

```bash
# Connexion à PostgreSQL
psql -U postgres

# Créer la base de données de test
CREATE DATABASE gaztracker_test;

# Créer l'utilisateur (si nécessaire)
CREATE USER gaztracker WITH PASSWORD 'your_password';

# Donner les permissions
GRANT ALL PRIVILEGES ON DATABASE gaztracker_test TO gaztracker;

# Quitter
\q
```

### 1.2 Configurer `.env`

Créez ou mettez à jour votre fichier `.env` :

```env
# Database
DATABASE_URL=postgresql://gaztracker:your_password@localhost:5432/gaztracker_test

# Redis (optionnel pour tests)
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_NAME=GazTracker
DEBUG=True
```

---

## 🔄 ÉTAPE 2 : APPLIQUER LES MIGRATIONS

### 2.1 Vérifier la configuration Alembic

```bash
# Vérifier que alembic.ini pointe vers la bonne DB
cat alembic.ini | grep sqlalchemy.url
```

### 2.2 Appliquer toutes les migrations

```bash
# Depuis la racine du projet
cd C:\Users\Schad225\Documents\Projets\gaztracker

# Appliquer les migrations
alembic upgrade head
```

**Résultat attendu** :
```
INFO  [alembic.runtime.migration] Running upgrade  -> 502160f9945d, initial migration create all tables
INFO  [alembic.runtime.migration] Running upgrade 502160f9945d -> 1a8dff9c71d0, migrate palette to rfid tag relationship
...
INFO  [alembic.runtime.migration] Running upgrade 2025_11_12_2300 -> phase1_hierarchy, Phase 1: Add new hierarchy models and workflow documents
```

### 2.3 Vérifier les tables créées

```bash
# Se connecter à la base
psql -U gaztracker -d gaztracker_test

# Lister les tables
\dt

# Vérifier quelques tables importantes
\d groupes
\d grand_distributeurs
\d centres_remplisseurs
\d depots
\d bons_enlevement
\d bons_reception_retour

# Quitter
\q
```

**Tables attendues (principales)** :
- `groupes`
- `grand_distributeurs`
- `centres_remplisseurs`
- `depots`
- `partners`
- `bons_enlevement`
- `livraisons_details`
- `collectes_vides`
- `bons_reception_retour`
- `details_retour`
- `palettes`
- `palette_movements`
- `rfid_tags`
- `users`

---

## 🌱 ÉTAPE 3 : PEUPLER AVEC DONNÉES DE TEST

### 3.1 Exécuter le script de seed

```bash
# Depuis la racine du projet
python scripts/seed_test_data.py
```

**Résultat attendu** :
```
🚀 GazTracker - Database Seed Script
============================================================
🌱 Starting database seed...

📦 Creating Groupes...
✅ Created 3 Groupes

🏢 Creating Grands Distributeurs...
✅ Created 3 Grands Distributeurs

🏭 Creating Centres Remplisseurs...
✅ Created 3 Centres Remplisseurs

🤝 Creating Partners (Grossistes)...
✅ Created 3 Grossistes

📍 Creating Dépôts...
✅ Created 6 Dépôts

🏪 Creating Revendeurs...
✅ Created 2 Revendeurs

👤 Creating Users...
✅ Created 6 Users

🏷️ Creating RFID Tags...
✅ Created 50 RFID Tags

📦 Creating Palettes...
✅ Created 30 Palettes

============================================================
✨ SEED COMPLETED SUCCESSFULLY! ✨
============================================================
```

### 3.2 Vérifier les données

```bash
# Se connecter à la base
psql -U gaztracker -d gaztracker_test

# Vérifier les données
SELECT name, code FROM groupes;
SELECT name, code FROM grand_distributeurs;
SELECT name, code, city FROM centres_remplisseurs;
SELECT name, type FROM partners;
SELECT name, is_main_depot FROM depots;

# Compter les enregistrements
SELECT 'groupes' as table_name, COUNT(*) FROM groupes
UNION ALL
SELECT 'grand_distributeurs', COUNT(*) FROM grand_distributeurs
UNION ALL
SELECT 'centres_remplisseurs', COUNT(*) FROM centres_remplisseurs
UNION ALL
SELECT 'partners', COUNT(*) FROM partners
UNION ALL
SELECT 'depots', COUNT(*) FROM depots
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'palettes', COUNT(*) FROM palettes;
```

---

## 🧪 ÉTAPE 4 : TESTER LES SERVICES

### 4.1 Créer un script de test Python

Créez `scripts/test_services.py` :

```python
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from app.database import SessionLocal
from app.services.groupe_service import GroupeService
from app.services.centre_remplisseur_service import CentreRemplisseurService
from app.services.bon_enlevement_service import BonEnlevementService

async def test_services():
    db = SessionLocal()
    
    try:
        print("🧪 Testing Services...\n")
        
        # Test 1: Get all Groupes
        print("1️⃣ Testing GroupeService.get_all()")
        groupes = await GroupeService.get_all(db)
        print(f"   ✅ Found {len(groupes)} groupes")
        for g in groupes:
            print(f"      - {g.name} ({g.code})")
        
        # Test 2: Get Groupe with stats
        if groupes:
            print(f"\n2️⃣ Testing GroupeService.get_with_stats()")
            stats = await GroupeService.get_with_stats(db, groupes[0].id)
            print(f"   ✅ Groupe: {stats['groupe'].name}")
            print(f"      Grand Distributeurs: {stats['grand_distributeurs_count']}")
        
        # Test 3: Get all Centres
        print(f"\n3️⃣ Testing CentreRemplisseurService.get_all()")
        centres = await CentreRemplisseurService.get_all(db)
        print(f"   ✅ Found {len(centres)} centres")
        for c in centres:
            print(f"      - {c.name} ({c.code})")
        
        # Test 4: Get active centres count
        count = await CentreRemplisseurService.count(db, is_active=True)
        print(f"\n4️⃣ Active centres count: {count}")
        
        print("\n✨ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_services())
```

### 4.2 Exécuter les tests

```bash
python scripts/test_services.py
```

**Résultat attendu** :
```
🧪 Testing Services...

1️⃣ Testing GroupeService.get_all()
   ✅ Found 3 groupes
      - Pétroci Holding (PETROCI)
      - SODIGAZ (SODIGAZ)
      - Pétro Ivoire (PETRO_IV)

2️⃣ Testing GroupeService.get_with_stats()
   ✅ Groupe: Pétroci Holding
      Grand Distributeurs: 2

3️⃣ Testing CentreRemplisseurService.get_all()
   ✅ Found 3 centres
      - Centre Remplisseur Yopougon (CR_YOP)
      - Centre Remplisseur Koumassi (CR_KOU)
      - Centre Remplisseur Marcory (CR_MAR)

4️⃣ Active centres count: 3

✨ All tests passed!
```

---

## 📊 ÉTAPE 5 : TESTER LES WORKFLOWS

### 5.1 Script de test Workflow Bon d'Enlèvement

Créez `scripts/test_workflow_bon_enlevement.py` pour tester le cycle complet.

### 5.2 Scénario de test

1. **Créer un Bon d'Enlèvement**
2. **Valider le bon** (génération OTP)
3. **Charger les palettes**
4. **Départ du centre**
5. **Livraison à un dépôt**
6. **Collecte de vides**
7. **Terminer le bon**

---

## ✅ ÉTAPE 6 : VÉRIFICATIONS FINALES

### 6.1 Checklist de vérification

- [ ] Toutes les migrations appliquées sans erreur
- [ ] Toutes les tables créées
- [ ] Données de test insérées avec succès
- [ ] Services CRUD fonctionnels
- [ ] Relations entre tables correctes
- [ ] Indexes créés
- [ ] Contraintes de clés étrangères actives
- [ ] Enum types PostgreSQL créés

### 6.2 Commandes de vérification rapide

```sql
-- Vérifier les contraintes de clés étrangères
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_name LIKE '%bon%';

-- Vérifier les enums
SELECT n.nspname as schema, t.typname as typename 
FROM pg_type t 
LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace 
WHERE (t.typrelid = 0 OR (SELECT c.relkind = 'c' FROM pg_catalog.pg_class c WHERE c.oid = t.typrelid)) 
AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_type el WHERE el.oid = t.typelem AND el.typarray = t.oid)
AND n.nspname NOT IN ('pg_catalog', 'information_schema')
AND t.typname LIKE '%status%' OR t.typname LIKE '%type%';
```

---

## 🐛 DÉPANNAGE

### Problème : Migration échoue

```bash
# Réinitialiser les migrations
alembic downgrade base
alembic upgrade head
```

### Problème : Données en conflit

```bash
# Nettoyer la base et recommencer
python scripts/seed_test_data.py  # Répondre 'y' pour continuer
```

### Problème : Service échoue

- Vérifier que les données de seed ont bien été créées
- Vérifier les relations entre tables
- Consulter les logs d'erreur Python

---

## 📝 NOTES

- **IMPORTANT** : Ces tests sont sur une base de DÉVELOPPEMENT
- Ne JAMAIS exécuter sur la base de PRODUCTION
- Les mots de passe de test sont simples, à changer en production
- Les coordonnées GPS sont approximatives

---

## ✅ PROCHAINES ÉTAPES

Une fois les tests réussis :

1. **Créer les routes API** FastAPI
2. **Tester avec Postman/Swagger**
3. **Tests unitaires automatisés**
4. **Tests d'intégration**
5. **Déploiement en staging**

---

**Date:** 20 novembre 2024  
**Version Backend:** Phase 1-4 Complètes  
**Status:** ✅ Prêt pour tests

