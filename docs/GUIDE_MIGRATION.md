# 🔄 GUIDE DE MIGRATION - GazTracker v1 → v2

## 📋 Vue d'ensemble

Ce guide explique comment migrer en toute sécurité de l'ancienne structure (v1) vers la nouvelle structure (v2) adaptée à la réalité terrain.

---

## ⚠️ PRÉREQUIS

### Avant de Commencer

1. ✅ **Backup complet de la base de données**
   ```bash
   pg_dump -U gaztracker_user gaztracker_db > backup_before_migration_$(date +%Y%m%d_%H%M%S).sql
   ```

2. ✅ **Arrêter tous les services**
   ```bash
   # Arrêter backend
   sudo systemctl stop gaztracker-backend
   
   # Arrêter workers/celery si existants
   sudo systemctl stop gaztracker-worker
   ```

3. ✅ **Vérifier l'espace disque**
   ```bash
   df -h
   # Prévoir au moins 2x la taille actuelle de la DB
   ```

4. ✅ **Créer un environnement de test**
   - Cloner la DB de production dans un environnement de test
   - Tester la migration sur cet environnement d'abord

---

## 📊 ANALYSE DE L'EXISTANT

### 1. Inventaire des Données Actuelles

```sql
-- Compter les entités existantes
SELECT 'users' AS table_name, COUNT(*) FROM users
UNION ALL
SELECT 'partners', COUNT(*) FROM partners
UNION ALL
SELECT 'palettes', COUNT(*) FROM palettes
UNION ALL
SELECT 'expeditions', COUNT(*) FROM expeditions
UNION ALL
SELECT 'palette_movements', COUNT(*) FROM palette_movements;
```

### 2. Identifier les Dépendances

```sql
-- Expeditions en cours (statut non terminal)
SELECT status, COUNT(*)
FROM expeditions
WHERE status NOT IN ('LIVREE', 'ANNULEE')
GROUP BY status;

-- Palettes en transit
SELECT status, COUNT(*)
FROM palettes
WHERE status IN ('EN_ROUTE', 'EN_RECEPTION')
GROUP BY status;
```

**⚠️ ACTION:** Terminer ou mettre en attente toutes les expéditions en cours avant migration.

---

## 🗺️ PLAN DE MIGRATION

### Phase 1: Préparation (1 jour)
1. Backup complet
2. Audit des données existantes
3. Identification des incohérences
4. Correction des anomalies
5. Freeze des opérations (mode maintenance)

### Phase 2: Migration Structure (2-3 heures)
1. Création nouvelles tables
2. Migration des données
3. Vérification intégrité
4. Création index et contraintes

### Phase 3: Tests (2-4 heures)
1. Tests unitaires migrations
2. Tests intégrité référentielle
3. Tests requêtes courantes
4. Validation données migres

### Phase 4: Déploiement (1-2 heures)
1. Déploiement nouveau code backend
2. Déploiement frontend
3. Redémarrage services
4. Tests smoke
5. Surveillance monitoring

### Phase 5: Post-Migration (1-2 jours)
1. Surveillance intensive
2. Correction bugs éventuels
3. Formation utilisateurs
4. Documentation mises à jour

**DURÉE TOTALE ESTIMÉE:** 3-5 jours

---

## 🔧 SCRIPTS DE MIGRATION

### Script 1: Création de la Nouvelle Structure

```sql
-- Fichier: migration_001_create_new_tables.sql

-- 1. Créer types ENUM
CREATE TYPE partner_type_new AS ENUM (
    'GROSSISTE',
    'REVENDEUR',
    'TRANSPORTEUR',
    'AUTRE'
);

CREATE TYPE palette_status_new AS ENUM (
    'CREATION',
    'EN_STOCK_CENTRE',
    'EN_CHARGEMENT',
    'EN_ROUTE_ALLER',
    'LIVREE_GROSSISTE',
    'LIVREE_REVENDEUR',
    'EN_STOCK_GROSSISTE',
    'EN_STOCK_REVENDEUR',
    'EN_ROUTE_RETOUR',
    'RETOURNEE_CENTRE',
    'HORS_SERVICE'
);

-- 2. Créer table groupes
CREATE TABLE groupes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    address VARCHAR(500),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'Côte d''Ivoire',
    phone VARCHAR(20),
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Créer table grand_distributeurs
CREATE TABLE grand_distributeurs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    groupe_id UUID REFERENCES groupes(id) ON DELETE SET NULL,
    address VARCHAR(500),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'Côte d''Ivoire',
    phone VARCHAR(20),
    email VARCHAR(255),
    contact_name VARCHAR(255),
    contact_phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. Créer table centres_remplisseurs
CREATE TABLE centres_remplisseurs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    grand_distributeur_id UUID REFERENCES grand_distributeurs(id) ON DELETE CASCADE,
    address VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'Côte d''Ivoire',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    phone VARCHAR(20),
    email VARCHAR(255),
    contact_name VARCHAR(255),
    contact_phone VARCHAR(20),
    capacity_b28 INTEGER,
    capacity_b12 INTEGER,
    capacity_b6 INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 5. Créer table depots
CREATE TABLE depots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    partner_id UUID REFERENCES partners(id) ON DELETE CASCADE,
    address VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    contact_name VARCHAR(255),
    contact_phone VARCHAR(20),
    capacity_b28 INTEGER,
    capacity_b12 INTEGER,
    capacity_b6 INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    is_main_depot BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ... (Créer toutes les autres tables selon SCHEMA_DATABASE.md)

-- Créer index
CREATE INDEX idx_groupes_code ON groupes(code);
CREATE INDEX idx_grand_dist_groupe ON grand_distributeurs(groupe_id);
CREATE INDEX idx_centres_grand_dist ON centres_remplisseurs(grand_distributeur_id);
CREATE INDEX idx_depots_partner ON depots(partner_id);
-- ... (Tous les index)
```

---

### Script 2: Migration des Données

```sql
-- Fichier: migration_002_migrate_data.sql

-- =============================================================================
-- ÉTAPE 1: CRÉER HIÉRARCHIE PAR DÉFAUT
-- =============================================================================

-- Créer un groupe par défaut
INSERT INTO groupes (id, name, code, city, is_active)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Groupe Principal',
    'PRINCIPAL',
    'Abidjan',
    TRUE
);

-- Créer un grand distributeur par défaut
INSERT INTO grand_distributeurs (id, name, code, groupe_id, city, is_active)
VALUES (
    '00000000-0000-0000-0000-000000000002',
    'Distributeur Principal',
    'DISTRIB01',
    '00000000-0000-0000-0000-000000000001',
    'Abidjan',
    TRUE
);

-- Créer un centre remplisseur par défaut
INSERT INTO centres_remplisseurs (
    id, name, code, grand_distributeur_id,
    address, city, is_active
)
VALUES (
    '00000000-0000-0000-0000-000000000003',
    'Centre Principal',
    'CENTRE01',
    '00000000-0000-0000-0000-000000000002',
    'Zone Industrielle',
    'Abidjan',
    TRUE
);

-- =============================================================================
-- ÉTAPE 2: MIGRER PARTNERS → GROSSISTES
-- =============================================================================

-- Les partners de type GROSSISTE ou FOURNISSEUR deviennent des GROSSISTES
-- Pas de modification nécessaire si le type existe déjà
UPDATE partners
SET type = 'GROSSISTE'::partner_type
WHERE type IN ('GROSSISTE', 'FOURNISSEUR');

-- =============================================================================
-- ÉTAPE 3: CRÉER DÉPÔTS PAR DÉFAUT POUR CHAQUE GROSSISTE
-- =============================================================================

INSERT INTO depots (
    id,
    name,
    code,
    partner_id,
    address,
    city,
    is_main_depot,
    is_active
)
SELECT
    uuid_generate_v4(),
    p.name || ' - Dépôt Principal',
    'DEP-' || LEFT(UPPER(REPLACE(p.name, ' ', '')), 6) || '-01',
    p.id,
    COALESCE(p.address, 'Adresse à compléter'),
    COALESCE(p.city, 'Abidjan'),
    TRUE,
    TRUE
FROM partners p
WHERE p.type = 'GROSSISTE'
AND NOT EXISTS (
    SELECT 1 FROM depots d WHERE d.partner_id = p.id
);

-- =============================================================================
-- ÉTAPE 4: MIGRER EXPEDITIONS → BONS_ENLEVEMENT
-- =============================================================================

-- Créer table temporaire pour mapper ancien → nouveau
CREATE TEMP TABLE expedition_mapping (
    old_expedition_id UUID,
    new_bon_enlevement_id UUID
);

-- Insérer dans bons_enlevement (simplifié)
INSERT INTO bons_enlevement (
    id,
    numero_bon,
    reference,
    centre_remplisseur_id,
    grossiste_id,
    depot_principal_id,
    vehicule_immatriculation,
    chauffeur_nom,
    date_creation,
    date_validation,
    date_depart,
    date_arrivee_finale,
    status,
    observations,
    validateur_centre_id,
    recepteur_final_id,
    palette_count,
    created_at,
    updated_at
)
SELECT
    e.id,
    e.reference_number,
    e.reference_number,
    '00000000-0000-0000-0000-000000000003'::UUID,  -- Centre par défaut
    e.grossiste_id,
    (SELECT id FROM depots WHERE partner_id = e.grossiste_id AND is_main_depot = TRUE LIMIT 1),
    e.vehicle_info,
    e.transporter,
    e.date_creation,
    e.date_creation,  -- Assume validé à la création
    e.date_departure,
    e.date_delivery,
    -- Mapping des statuts
    CASE e.status
        WHEN 'CREATION' THEN 'CREATION'::bon_enlevement_status
        WHEN 'EN_ATTENTE' THEN 'VALIDE'::bon_enlevement_status
        WHEN 'CREEE' THEN 'VALIDE'::bon_enlevement_status
        WHEN 'EN_TRANSIT' THEN 'EN_ROUTE'::bon_enlevement_status
        WHEN 'ARRIVEE' THEN 'EN_LIVRAISON'::bon_enlevement_status
        WHEN 'LIVREE' THEN 'TERMINE'::bon_enlevement_status
        WHEN 'ANNULEE' THEN 'ANNULE'::bon_enlevement_status
        ELSE 'CREATION'::bon_enlevement_status
    END,
    e.notes,
    e.created_by_id,
    e.validated_by_id,
    (SELECT COUNT(*) FROM palettes WHERE current_expedition_id = e.id),
    e.created_at,
    e.updated_at
FROM expeditions e;

-- Sauvegarder mapping
INSERT INTO expedition_mapping (old_expedition_id, new_bon_enlevement_id)
SELECT id, id FROM expeditions;

-- =============================================================================
-- ÉTAPE 5: MIGRER PALETTES
-- =============================================================================

-- Ajouter colonnes temporaires à palettes pour la migration
ALTER TABLE palettes
ADD COLUMN IF NOT EXISTS centre_remplisseur_actuel_id_temp UUID,
ADD COLUMN IF NOT EXISTS depot_actuel_id_temp UUID,
ADD COLUMN IF NOT EXISTS partner_actuel_id_temp UUID,
ADD COLUMN IF NOT EXISTS bon_enlevement_actuel_id_temp UUID;

-- Mettre à jour les nouvelles colonnes
UPDATE palettes p
SET
    centre_remplisseur_actuel_id_temp = CASE
        WHEN p.status IN ('CREATION', 'EN_STOCK') THEN '00000000-0000-0000-0000-000000000003'::UUID
        ELSE NULL
    END,
    depot_actuel_id_temp = CASE
        WHEN p.status = 'LIVREE' AND p.current_expedition_id IS NOT NULL THEN
            (SELECT be.depot_principal_id
             FROM bons_enlevement be
             WHERE be.id = p.current_expedition_id)
        ELSE NULL
    END,
    partner_actuel_id_temp = CASE
        WHEN p.status = 'LIVREE' AND p.current_expedition_id IS NOT NULL THEN
            (SELECT be.grossiste_id
             FROM bons_enlevement be
             WHERE be.id = p.current_expedition_id)
        ELSE NULL
    END,
    bon_enlevement_actuel_id_temp = CASE
        WHEN p.status IN ('EN_ROUTE', 'EN_RECEPTION') THEN p.current_expedition_id
        ELSE NULL
    END;

-- Mapper anciens statuts → nouveaux statuts
ALTER TABLE palettes ADD COLUMN IF NOT EXISTS status_new palette_status_new;

UPDATE palettes
SET status_new = CASE status::text
    WHEN 'CREATION' THEN 'CREATION'::palette_status_new
    WHEN 'EN_STOCK' THEN 'EN_STOCK_CENTRE'::palette_status_new
    WHEN 'EN_ROUTE' THEN 'EN_ROUTE_ALLER'::palette_status_new
    WHEN 'EN_RECEPTION' THEN 'LIVREE_GROSSISTE'::palette_status_new
    WHEN 'LIVREE' THEN 'EN_STOCK_GROSSISTE'::palette_status_new
    WHEN 'RETOURNEE' THEN 'RETOURNEE_CENTRE'::palette_status_new
    WHEN 'OUT' THEN 'HORS_SERVICE'::palette_status_new
    ELSE 'CREATION'::palette_status_new
END;

-- =============================================================================
-- ÉTAPE 6: FINALISER MIGRATION PALETTES
-- =============================================================================

-- Renommer anciennes colonnes
ALTER TABLE palettes RENAME COLUMN status TO status_old;
ALTER TABLE palettes RENAME COLUMN status_new TO status;

ALTER TABLE palettes RENAME COLUMN current_expedition_id TO current_expedition_id_old;

-- Ajouter nouvelles colonnes définitives
ALTER TABLE palettes
ADD COLUMN centre_remplisseur_actuel_id UUID REFERENCES centres_remplisseurs(id) ON DELETE SET NULL,
ADD COLUMN depot_actuel_id UUID REFERENCES depots(id) ON DELETE SET NULL,
ADD COLUMN partner_actuel_id UUID REFERENCES partners(id) ON DELETE SET NULL,
ADD COLUMN bon_enlevement_actuel_id UUID REFERENCES bons_enlevement(id) ON DELETE SET NULL,
ADD COLUMN bon_retour_actuel_id UUID REFERENCES bons_reception_retour(id) ON DELETE SET NULL;

-- Copier depuis colonnes temporaires
UPDATE palettes
SET
    centre_remplisseur_actuel_id = centre_remplisseur_actuel_id_temp,
    depot_actuel_id = depot_actuel_id_temp,
    partner_actuel_id = partner_actuel_id_temp,
    bon_enlevement_actuel_id = bon_enlevement_actuel_id_temp;

-- Supprimer colonnes temporaires
ALTER TABLE palettes
DROP COLUMN centre_remplisseur_actuel_id_temp,
DROP COLUMN depot_actuel_id_temp,
DROP COLUMN partner_actuel_id_temp,
DROP COLUMN bon_enlevement_actuel_id_temp;

-- =============================================================================
-- ÉTAPE 7: CRÉER LIVRAISON PAR DÉFAUT POUR CHAQUE BON
-- =============================================================================

-- Pour chaque bon d'enlèvement, créer une livraison unique au dépôt principal
INSERT INTO livraisons_details (
    id,
    bon_enlevement_id,
    ordre_livraison,
    depot_id,
    status,
    date_arrivee,
    date_depart,
    created_at,
    updated_at
)
SELECT
    uuid_generate_v4(),
    be.id,
    1,
    be.depot_principal_id,
    CASE be.status
        WHEN 'TERMINE' THEN 'LIVREE'::livraison_status
        WHEN 'EN_LIVRAISON' THEN 'EN_COURS'::livraison_status
        ELSE 'EN_ATTENTE'::livraison_status
    END,
    be.date_arrivee_finale,
    be.date_arrivee_finale,
    be.created_at,
    be.updated_at
FROM bons_enlevement be;

-- Lier palettes aux livraisons
INSERT INTO livraison_palettes (livraison_detail_id, palette_id)
SELECT
    ld.id,
    p.id
FROM palettes p
JOIN livraisons_details ld ON ld.bon_enlevement_id = p.bon_enlevement_actuel_id
WHERE p.bon_enlevement_actuel_id IS NOT NULL;

-- =============================================================================
-- ÉTAPE 8: MIGRER PALETTE_MOVEMENTS
-- =============================================================================

-- Ajouter nouvelles colonnes
ALTER TABLE palette_movements
ADD COLUMN IF NOT EXISTS bon_enlevement_id UUID REFERENCES bons_enlevement(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS centre_remplisseur_id UUID REFERENCES centres_remplisseurs(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS depot_id UUID REFERENCES depots(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS partner_id UUID REFERENCES partners(id) ON DELETE SET NULL;

-- Mapper expedition_id → bon_enlevement_id
UPDATE palette_movements pm
SET bon_enlevement_id = pm.expedition_id
WHERE pm.expedition_id IS NOT NULL;

-- Mapper actions
ALTER TABLE palette_movements ADD COLUMN IF NOT EXISTS action_new movement_action;

UPDATE palette_movements
SET action_new = CASE action::text
    WHEN 'CREATION' THEN 'CREATION'::movement_action
    WHEN 'SCANNING_DEPART' THEN 'DEPART_CENTRE'::movement_action
    WHEN 'SCANNING_ARRIVEE' THEN 'LIVRAISON_DEPOT'::movement_action
    WHEN 'VALIDATION_RECEPTION' THEN 'RECEPTION_DEPOT'::movement_action
    WHEN 'ASSIGNATION_EXPEDITION' THEN 'CHARGEMENT_CENTRE'::movement_action
    WHEN 'RETOUR_USINE' THEN 'RETOUR_ARRIVEE'::movement_action
    WHEN 'MISE_HORS_SERVICE' THEN 'MISE_HORS_SERVICE'::movement_action
    ELSE 'STOCKAGE'::movement_action
END;

-- Finaliser
ALTER TABLE palette_movements RENAME COLUMN action TO action_old;
ALTER TABLE palette_movements RENAME COLUMN action_new TO action;
```

---

### Script 3: Nettoyage et Vérification

```sql
-- Fichier: migration_003_cleanup_verify.sql

-- =============================================================================
-- NETTOYAGE
-- =============================================================================

-- Supprimer colonnes obsolètes après vérification
-- ALTER TABLE palettes DROP COLUMN IF EXISTS status_old;
-- ALTER TABLE palettes DROP COLUMN IF EXISTS current_expedition_id_old;
-- ALTER TABLE palette_movements DROP COLUMN IF EXISTS action_old;
-- ALTER TABLE palette_movements DROP COLUMN IF EXISTS expedition_id;

-- Renommer expeditions → expeditions_old (archivage)
ALTER TABLE expeditions RENAME TO expeditions_old;

-- =============================================================================
-- VÉRIFICATIONS
-- =============================================================================

-- 1. Vérifier que toutes les palettes ont une localisation
SELECT
    COUNT(*) AS palettes_sans_localisation
FROM palettes
WHERE centre_remplisseur_actuel_id IS NULL
AND depot_actuel_id IS NULL
AND partner_actuel_id IS NULL
AND status NOT IN ('HORS_SERVICE');

-- 2. Vérifier intégrité bons d'enlèvement
SELECT
    COUNT(*) AS bons_sans_depot
FROM bons_enlevement
WHERE depot_principal_id IS NULL;

-- 3. Vérifier que chaque grossiste a au moins un dépôt
SELECT
    p.name AS grossiste_sans_depot
FROM partners p
WHERE p.type = 'GROSSISTE'
AND NOT EXISTS (
    SELECT 1 FROM depots d WHERE d.partner_id = p.id
);

-- 4. Compter entités migrées
SELECT 'groupes' AS entite, COUNT(*) AS total FROM groupes
UNION ALL
SELECT 'grand_distributeurs', COUNT(*) FROM grand_distributeurs
UNION ALL
SELECT 'centres_remplisseurs', COUNT(*) FROM centres_remplisseurs
UNION ALL
SELECT 'depots', COUNT(*) FROM depots
UNION ALL
SELECT 'bons_enlevement', COUNT(*) FROM bons_enlevement
UNION ALL
SELECT 'palettes', COUNT(*) FROM palettes
UNION ALL
SELECT 'livraisons_details', COUNT(*) FROM livraisons_details;

-- 5. Vérifier cohérence compteurs
SELECT
    be.numero_bon,
    be.palette_count AS compteur,
    COUNT(p.id) AS palettes_reelles
FROM bons_enlevement be
LEFT JOIN palettes p ON p.bon_enlevement_actuel_id = be.id
GROUP BY be.id, be.numero_bon, be.palette_count
HAVING be.palette_count != COUNT(p.id);
```

---

## 📝 CHECKLIST POST-MIGRATION

### Vérifications Techniques

- [ ] Toutes les migrations Alembic ont réussi
- [ ] Aucune erreur dans les logs de migration
- [ ] Toutes les contraintes FK sont valides
- [ ] Tous les index sont créés
- [ ] Les triggers fonctionnent
- [ ] Les vues sont créées et fonctionnelles

### Vérifications Données

- [ ] Nombre de palettes cohérent (avant = après)
- [ ] Nombre de bons cohérent
- [ ] Toutes les palettes ont une localisation (sauf HS)
- [ ] Tous les grossistes ont au moins un dépôt
- [ ] Tous les bons ont une destination valide
- [ ] Historique palette_movements conservé

### Vérifications Fonctionnelles

- [ ] Login utilisateurs fonctionne
- [ ] Création de bon d'enlèvement fonctionne
- [ ] Affichage liste palettes fonctionne
- [ ] Scan RFID fonctionne
- [ ] Génération PDF fonctionne
- [ ] Notifications fonctionnent

### Vérifications Performance

- [ ] Temps de réponse API < 200ms
- [ ] Requêtes complexes < 1s
- [ ] Pas de N+1 queries
- [ ] Cache Redis fonctionne

---

## 🔙 PROCÉDURE DE ROLLBACK

### En cas de problème pendant la migration

```bash
# 1. Arrêter tous les services
sudo systemctl stop gaztracker-backend

# 2. Restaurer le backup
psql -U gaztracker_user -d postgres -c "DROP DATABASE gaztracker_db;"
psql -U gaztracker_user -d postgres -c "CREATE DATABASE gaztracker_db;"
psql -U gaztracker_user -d gaztracker_db < backup_before_migration_XXXXXXXX.sql

# 3. Redémarrer avec l'ancienne version du code
git checkout v1.0  # Tag de l'ancienne version
sudo systemctl start gaztracker-backend

# 4. Analyser les logs pour identifier le problème
tail -f /var/log/gaztracker/error.log
```

---

## 📚 DONNÉES DE TEST POST-MIGRATION

### Script de Création de Données Complètes

```python
# Fichier: scripts/create_complete_test_data.py

import asyncio
from app.database import db_manager
from app.models import *
from datetime import datetime, timedelta
import uuid

async def create_complete_hierarchy():
    """Créer hiérarchie complète pour tests"""
    
    async with db_manager.get_session() as session:
        # 1. Créer groupe
        groupe = Groupe(
            name="Pétroci Holding",
            code="PETROCI",
            city="Abidjan",
            phone="+225 27 20 20 25 00"
        )
        session.add(groupe)
        await session.flush()
        
        # 2. Créer grand distributeur
        grand_dist = GrandDistributeur(
            name="CEV3 (PETROCI)",
            code="CEV3",
            groupe_id=groupe.id,
            city="Abidjan"
        )
        session.add(grand_dist)
        await session.flush()
        
        # 3. Créer centre remplisseur
        centre = CentreRemplisseur(
            name="Atelier TDC WEST AFRICA Sarl",
            code="TDC-YOP",
            grand_distributeur_id=grand_dist.id,
            address="Zone Industrielle Yopougon",
            city="Abidjan",
            latitude=5.345,
            longitude=-4.082,
            capacity_b28=500,
            capacity_b12=300,
            capacity_b6=200
        )
        session.add(centre)
        await session.flush()
        
        # 4. Créer grossiste
        grossiste = Partner(
            name="TDC WEST AFRICA Sarl",
            type=PartnerType.GROSSISTE,
            code="TDC-001",
            city="Abidjan",
            phone="+225 07 12 34 56 78"
        )
        session.add(grossiste)
        await session.flush()
        
        # 5. Créer dépôt principal grossiste
        depot_principal = Depot(
            name="Dépôt Principal TDC",
            code="TDC-DEP-01",
            partner_id=grossiste.id,
            address="Atelier TDC Yopougon",
            city="Abidjan",
            is_main_depot=True,
            latitude=5.345,
            longitude=-4.082
        )
        session.add(depot_principal)
        await session.flush()
        
        # 6. Créer revendeurs
        revendeurs = []
        for i, name in enumerate(["Kouassi Jean", "Seka Rose", "Jules Konan"]):
            revendeur = Partner(
                name=name,
                type=PartnerType.REVENDEUR,
                code=f"REV-{i+1:03d}",
                parent_grossiste_id=grossiste.id,
                city="Abidjan"
            )
            session.add(revendeur)
            await session.flush()
            
            # Créer dépôt revendeur
            depot_rev = Depot(
                name=f"Dépôt {name}",
                code=f"REV-{i+1:03d}-DEP-01",
                partner_id=revendeur.id,
                address=f"Quartier Zone {i+1}",
                city="Abidjan",
                is_main_depot=True
            )
            session.add(depot_rev)
            revendeurs.append((revendeur, depot_rev))
        
        await session.commit()
        
        print("✅ Hiérarchie créée avec succès")
        return {
            'groupe': groupe,
            'grand_dist': grand_dist,
            'centre': centre,
            'grossiste': grossiste,
            'depot_principal': depot_principal,
            'revendeurs': revendeurs
        }

if __name__ == "__main__":
    asyncio.run(create_complete_hierarchy())
```

---

## 📊 RAPPORT DE MIGRATION

### Template de Rapport

```markdown
# Rapport de Migration GazTracker v1 → v2

**Date:** YYYY-MM-DD
**Durée totale:** X heures
**Responsable:** [Nom]

## Résumé

- ✅ Migration réussie
- ⚠️ Problèmes mineurs résolus
- ❌ Échec (rollback effectué)

## Statistiques

### Avant Migration
- Utilisateurs: X
- Partners: Y
- Palettes: Z
- Expéditions: W

### Après Migration
- Groupes: A
- Grand Distributeurs: B
- Centres Remplisseurs: C
- Dépôts: D
- Bons Enlèvement: E
- Palettes: Z (conservées)

## Problèmes Rencontrés

1. **Problème:** Description
   **Solution:** Description
   **Impact:** Aucun / Mineur / Majeur

## Tests Effectués

- [x] Tests unitaires
- [x] Tests intégration
- [x] Tests performance
- [x] Tests utilisateurs

## Actions de Suivi

- [ ] Formation utilisateurs (Date)
- [ ] Documentation mise à jour (Date)
- [ ] Surveillance renforcée 7 jours

## Signatures

- Responsable technique: _____________
- Responsable métier: _____________
```

---

## 🎓 FORMATION POST-MIGRATION

### Points Clés à Former

1. **Nouvelle hiérarchie**
   - Groupe → Grand Distributeur → Centre
   - Grossiste → Revendeur → Dépôts

2. **Nouveaux documents**
   - Bon d'Enlèvement vs Bon de Réception Retour
   - Différences avec anciennes "Expéditions"

3. **Nouvelles fonctionnalités**
   - Tournées multi-dépôts
   - Collecte bouteilles vides
   - Contrôle qualité retours

4. **Nouveaux workflows**
   - Création bon → Validation → Chargement → Livraison
   - Retour → Contrôle → Validation

---

## ☎️ SUPPORT MIGRATION

### Contacts

- **Support technique:** tech@gaztracker.com
- **Urgences:** +225 XX XX XX XX XX
- **Slack:** #migration-support

### Problèmes Fréquents

#### Problème: Palettes sans localisation
```sql
-- Solution: Affecter au centre par défaut
UPDATE palettes
SET centre_remplisseur_actuel_id = '00000000-0000-0000-0000-000000000003'
WHERE centre_remplisseur_actuel_id IS NULL
AND depot_actuel_id IS NULL
AND partner_actuel_id IS NULL
AND status = 'EN_STOCK_CENTRE';
```

#### Problème: Grossiste sans dépôt
```sql
-- Solution: Créer dépôt automatique
-- Voir script migration étape 3
```

---

**FIN DU GUIDE DE MIGRATION**

Ce guide assure une migration sûre et réversible de l'ancienne vers la nouvelle structure.

