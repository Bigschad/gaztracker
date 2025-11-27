# 📡 STRATÉGIE RFID - GazTracker

## 🎯 Vue d'Ensemble

Le système GazTracker utilise la **technologie RFID (Radio-Frequency Identification)** comme pilier central de sa stratégie de traçabilité. Cette technologie permet une identification automatique, rapide et fiable des actifs tout au long de la chaîne logistique.

---

## 📊 ARCHITECTURE RFID ACTUELLE ET FUTURE

### Phase 1 : RFID Palettes (ACTUEL - Production)

```
┌─────────────────────────────────────────┐
│         TAG RFID PALETTE                │
│  ┌───────────────────────────────────┐  │
│  │ ID Unique: RFID-2025-00001        │  │
│  │ Type: Passive UHF                 │  │
│  │ Fréquence: 860-960 MHz            │  │
│  │ Portée: 0-10 mètres               │  │
│  │ Durée vie: 10+ ans                │  │
│  └───────────────────────────────────┘  │
│                                         │
│  Palette Physique                       │
│  ├─ Structure métallique/bois          │
│  ├─ 24 bouteilles B28 (exemple)        │
│  └─ Tag RFID fixé solidement           │
└─────────────────────────────────────────┘
```

**Utilisation actuelle:**
- ✅ Identification unique de chaque palette
- ✅ Scan rapide lors des opérations
- ✅ Traçabilité complète des mouvements
- ✅ Inventaire automatisé

---

### Phase 2 : RFID Bouteilles (FUTUR - Long Terme)

```
┌─────────────────────────────────────────┐
│      TAG RFID BOUTEILLE                 │
│  ┌───────────────────────────────────┐  │
│  │ ID Unique: RFID-BTL-2026-00001    │  │
│  │ Type: Passive UHF Mini            │  │
│  │ Résistant: Chaleur + Pression     │  │
│  │ Position: Col de la bouteille     │  │
│  │ Portée: 0-3 mètres                │  │
│  └───────────────────────────────────┘  │
│                                         │
│  Bouteille de Gaz                       │
│  ├─ B28 (28 kg)                        │
│  ├─ Tag RFID intégré                   │
│  └─ Lié à la palette                   │
└─────────────────────────────────────────┘
```

**Bénéfices futurs:**
- 🔮 Traçabilité bouteille individuelle
- 🔮 Détection bouteilles manquantes
- 🔮 Historique complet par bouteille
- 🔮 Lutte contre contrefaçon
- 🔮 Gestion fines des rotations

---

## 🏗️ MODÈLE DE DONNÉES RFID

### Table `rfid_tags` (EXISTANT - CONSERVÉ)

```sql
CREATE TABLE rfid_tags (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identification
    tag_uid                 VARCHAR(50) UNIQUE NOT NULL,  -- UID physique du tag
    tag_code                VARCHAR(50) UNIQUE NOT NULL,  -- Code lisible (ex: RFID-2025-00001)
    label                   VARCHAR(255),                 -- Libellé descriptif
    
    -- Type de tag
    tag_type                rfid_tag_type NOT NULL,       -- PALETTE ou BOUTEILLE
    
    -- Association
    palette_id              UUID REFERENCES palettes(id) ON DELETE SET NULL,
    bouteille_id            UUID REFERENCES bouteilles(id) ON DELETE SET NULL,  -- FUTUR
    
    -- Statut
    status                  rfid_status DEFAULT 'ACTIF',
    is_active               BOOLEAN DEFAULT TRUE,
    
    -- Dates
    date_activation         TIMESTAMP,
    date_desactivation      TIMESTAMP,
    last_scan_date          TIMESTAMP,
    last_scan_location      VARCHAR(500),
    
    -- Métadonnées
    batch_number            VARCHAR(50),                  -- Lot de production
    manufacturer            VARCHAR(100),                 -- Fabricant du tag
    notes                   TEXT,
    
    created_at              TIMESTAMP DEFAULT NOW(),
    updated_at              TIMESTAMP DEFAULT NOW()
);

-- Types ENUM
CREATE TYPE rfid_tag_type AS ENUM (
    'PALETTE',
    'BOUTEILLE',      -- Pour phase future
    'CONTENEUR',      -- Optionnel: conteneurs de transport
    'AUTRE'
);

CREATE TYPE rfid_status AS ENUM (
    'ACTIF',          -- Opérationnel
    'INACTIF',        -- Temporairement désactivé
    'PERDU',          -- Tag perdu/non détecté
    'DEFECTUEUX',     -- Tag défaillant
    'DESACTIVE'       -- Désactivé définitivement
);

-- Index
CREATE INDEX idx_rfid_tag_uid ON rfid_tags(tag_uid);
CREATE INDEX idx_rfid_tag_code ON rfid_tags(tag_code);
CREATE INDEX idx_rfid_type ON rfid_tags(tag_type);
CREATE INDEX idx_rfid_status ON rfid_tags(status);
CREATE INDEX idx_rfid_palette ON rfid_tags(palette_id);
CREATE INDEX idx_rfid_last_scan ON rfid_tags(last_scan_date);
```

---

### Table `rfid_scans` (NOUVEAU - HISTORIQUE)

```sql
CREATE TABLE rfid_scans (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Tag scanné
    rfid_tag_id             UUID REFERENCES rfid_tags(id) ON DELETE CASCADE,
    tag_uid                 VARCHAR(50) NOT NULL,
    
    -- Contexte du scan
    scan_type               scan_type NOT NULL,
    scan_date               TIMESTAMP DEFAULT NOW(),
    
    -- Localisation
    centre_remplisseur_id   UUID REFERENCES centres_remplisseurs(id) ON DELETE SET NULL,
    depot_id                UUID REFERENCES depots(id) ON DELETE SET NULL,
    
    -- GPS
    latitude                DECIMAL(10, 8),
    longitude               DECIMAL(11, 8),
    location_address        VARCHAR(500),
    
    -- Document associé
    bon_enlevement_id       UUID REFERENCES bons_enlevement(id) ON DELETE SET NULL,
    bon_retour_id           UUID REFERENCES bons_reception_retour(id) ON DELETE SET NULL,
    livraison_detail_id     UUID REFERENCES livraisons_details(id) ON DELETE SET NULL,
    
    -- Utilisateur
    user_id                 UUID REFERENCES users(id) ON DELETE SET NULL,
    device_id               VARCHAR(100),  -- ID du lecteur RFID
    
    -- Métadonnées
    signal_strength         INTEGER,       -- Force du signal (RSSI)
    read_count              INTEGER,       -- Nombre de lectures
    notes                   TEXT,
    
    created_at              TIMESTAMP DEFAULT NOW()
);

-- Types de scan
CREATE TYPE scan_type AS ENUM (
    'CHARGEMENT',         -- Scan lors du chargement
    'DEPART',             -- Scan au départ
    'ARRIVEE',            -- Scan à l'arrivée
    'LIVRAISON',          -- Scan lors d'une livraison
    'INVENTAIRE',         -- Scan d'inventaire
    'CONTROLE',           -- Scan de contrôle qualité
    'VERIFICATION',       -- Scan de vérification
    'AUTRE'
);

-- Index
CREATE INDEX idx_rfid_scans_tag ON rfid_scans(rfid_tag_id);
CREATE INDEX idx_rfid_scans_date ON rfid_scans(scan_date);
CREATE INDEX idx_rfid_scans_type ON rfid_scans(scan_type);
CREATE INDEX idx_rfid_scans_bon_enl ON rfid_scans(bon_enlevement_id);
CREATE INDEX idx_rfid_scans_user ON rfid_scans(user_id);
```

---

## 📱 INTÉGRATION DANS LES WORKFLOWS

### 1. Workflow Palette avec RFID

```
┌─────────────────────────────────────────────────────────────┐
│ ÉTAPE 1: CRÉATION PALETTE                                   │
└─────────────────────────────────────────────────────────────┘

[Opérateur Centre]
    │
    │ 1. Créer palette dans système
    │ 2. Scanner tag RFID
    │    → Lecture UID: E200 6017 3401 0250 0000 1234
    │ 3. Association automatique:
    │    - Palette.id ← → RFIDTag.id
    │    - Tag activé
    │
    ↓
[Palette créée avec RFID associé]
[RFIDScan créé: type=VERIFICATION]

┌─────────────────────────────────────────────────────────────┐
│ ÉTAPE 2: CHARGEMENT POUR BON D'ENLÈVEMENT                  │
└─────────────────────────────────────────────────────────────┘

[Opérateur Centre]
    │
    │ Lors du chargement:
    │ 1. Scanner palette RFID
    │ 2. Vérifications automatiques:
    │    ✓ Tag actif
    │    ✓ Palette existe
    │    ✓ Palette disponible (EN_STOCK_CENTRE)
    │    ✓ Palette assignable au bon
    │ 3. Confirmation visuelle/sonore
    │ 4. Palette ajoutée au bon
    │
    ↓
[RFIDScan créé: type=CHARGEMENT, bon_enlevement_id=XXX]
[Palette.status → EN_CHARGEMENT]
[PaletteMovement créé: CHARGEMENT_CENTRE]

┌─────────────────────────────────────────────────────────────┐
│ ÉTAPE 3: DÉPART                                             │
└─────────────────────────────────────────────────────────────┘

[Responsable Centre]
    │
    │ Avant départ:
    │ 1. Scan toutes palettes du camion
    │ 2. Vérification comptage:
    │    - Attendu: 7 palettes
    │    - Scanné: 7 palettes
    │    ✓ OK
    │ 3. Validation départ
    │
    ↓
[7 RFIDScan créés: type=DEPART]
[BonEnlevement.status → EN_ROUTE]

┌─────────────────────────────────────────────────────────────┐
│ ÉTAPE 4: LIVRAISON DÉPÔT 1                                 │
└─────────────────────────────────────────────────────────────┘

[Chauffeur via App Mobile]
    │
    │ À l'arrivée dépôt 1:
    │ 1. Scanner palettes à livrer
    │    - Palette 44-127-78 ✓
    │    - Palette 77-121-125 ✓
    │ 2. Confirmation livraison
    │ 3. Signature récepteur
    │
    ↓
[2 RFIDScan créés: type=LIVRAISON, livraison_detail_id=XXX]
[2 Palettes.status → LIVREE_REVENDEUR]

┌─────────────────────────────────────────────────────────────┐
│ ÉTAPE 5: ARRIVÉE FINALE                                    │
└─────────────────────────────────────────────────────────────┘

[Récepteur Grossiste]
    │
    │ Au dépôt principal:
    │ 1. Scanner palettes restantes
    │    - 3 palettes scannées ✓
    │ 2. Validation OTP
    │ 3. Bon terminé
    │
    ↓
[3 RFIDScan créés: type=ARRIVEE]
[BonEnlevement.status → TERMINE]
```

---

### 2. Inventaire RFID Automatisé

```python
# Service: rfid_inventory_service.py

async def perform_rfid_inventory(
    centre_id: UUID,
    user_id: UUID,
    session: AsyncSession
) -> InventoryResult:
    """
    Effectuer inventaire RFID automatique
    
    Utilise un lecteur RFID longue portée pour scanner
    toutes les palettes présentes dans un centre
    """
    
    # 1. Lancer scan RFID (intégration hardware)
    scanned_tags = await rfid_reader.scan_area(
        timeout=30,  # 30 secondes
        power=HIGH   # Haute puissance pour longue portée
    )
    
    # 2. Récupérer palettes attendues
    expected_palettes = await session.execute(
        select(Palette)
        .where(
            Palette.centre_remplisseur_actuel_id == centre_id,
            Palette.status == PaletteStatus.EN_STOCK_CENTRE
        )
    )
    expected_tags = {p.rfid_tag.tag_uid for p in expected_palettes}
    
    # 3. Comparer
    found_tags = set(scanned_tags)
    
    missing = expected_tags - found_tags  # Manquantes
    extra = found_tags - expected_tags    # En trop
    
    # 4. Créer RFIDScan pour chaque tag trouvé
    for tag_uid in found_tags:
        rfid_tag = await get_tag_by_uid(tag_uid, session)
        scan = RFIDScan(
            rfid_tag_id=rfid_tag.id,
            tag_uid=tag_uid,
            scan_type=ScanType.INVENTAIRE,
            centre_remplisseur_id=centre_id,
            user_id=user_id
        )
        session.add(scan)
    
    # 5. Alertes pour manquantes
    if missing:
        await create_alert(
            type="PALETTES_MANQUANTES",
            count=len(missing),
            tags=missing
        )
    
    await session.commit()
    
    return InventoryResult(
        total_expected=len(expected_tags),
        total_found=len(found_tags),
        missing_tags=missing,
        extra_tags=extra,
        accuracy=len(found_tags) / len(expected_tags) * 100
    )
```

---

## 🔮 ROADMAP RFID

### Phase 1 : Palettes (ACTUEL) ✅

**Timeline:** Déjà implémenté

**Fonctionnalités:**
- ✅ Tag RFID UHF par palette
- ✅ Scan lors chargement/déchargement
- ✅ Inventaire automatisé
- ✅ Traçabilité complète
- ✅ Historique des scans

**Hardware:**
- Lecteurs RFID fixes (portiques)
- Lecteurs RFID mobiles (pistolets)
- Tags RFID passifs UHF

---

### Phase 2 : Bouteilles (FUTUR - 12-18 mois) 🔮

**Timeline:** 2026

**Objectifs:**
- 🔮 Tag RFID sur chaque bouteille
- 🔮 Traçabilité individuelle
- 🔮 Détection bouteilles manquantes
- 🔮 Anti-contrefaçon

**Défis techniques:**
- Résistance tag (chaleur, pression)
- Position optimale sur bouteille
- Coût unitaire du tag
- Processus d'intégration industrielle

**Préparation base de données:**

```sql
-- Table bouteilles (à créer)
CREATE TABLE bouteilles (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identification
    serial_number           VARCHAR(50) UNIQUE NOT NULL,
    rfid_tag_id             UUID REFERENCES rfid_tags(id) ON DELETE SET NULL,
    
    -- Type
    type                    palette_type NOT NULL,  -- B6, B12, B28
    
    -- Association palette
    palette_actuelle_id     UUID REFERENCES palettes(id) ON DELETE SET NULL,
    
    -- Fabrication
    date_fabrication        DATE,
    usine_fabrication       VARCHAR(255),
    
    -- Statut
    status                  bouteille_status,
    
    -- Cycles
    nombre_remplissages     INTEGER DEFAULT 0,
    derniere_verification   DATE,
    prochaine_verification  DATE,
    
    -- Sécurité
    date_peremption         DATE,
    
    created_at              TIMESTAMP DEFAULT NOW(),
    updated_at              TIMESTAMP DEFAULT NOW()
);

CREATE TYPE bouteille_status AS ENUM (
    'NEUVE',
    'EN_SERVICE',
    'A_VERIFIER',
    'EN_REPARATION',
    'HORS_SERVICE'
);

-- Relation Palette ← → Bouteilles
CREATE TABLE palette_bouteilles (
    palette_id              UUID REFERENCES palettes(id) ON DELETE CASCADE,
    bouteille_id            UUID REFERENCES bouteilles(id) ON DELETE CASCADE,
    position_palette        INTEGER,  -- Position sur la palette (1-24)
    date_association        TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (palette_id, bouteille_id)
);
```

---

### Phase 3 : IoT & Temps Réel (FUTUR - 18-24 mois) 🔮

**Timeline:** 2027

**Vision:**
- 🔮 Lecteurs RFID connectés IoT
- 🔮 Tracking temps réel automatique
- 🔮 Alertes instantanées
- 🔮 Tableaux de bord live

**Technologies:**
- Gateway IoT
- MQTT protocol
- WebSockets temps réel
- Cloud computing

---

## 🛠️ INTÉGRATION HARDWARE

### Lecteurs RFID Recommandés

#### 1. Lecteur Fixe (Portique)

**Modèle:** Zebra FX9600 ou équivalent

**Spécifications:**
- Fréquence: 860-960 MHz (UHF)
- Portée: jusqu'à 10m
- Taux lecture: 600+ tags/seconde
- Interface: Ethernet, RS-232
- Antennes: 4 ports

**Utilisation:**
- Entrée/Sortie centre remplisseur
- Zones de chargement
- Zones de stockage

**Prix:** ~2000-3000 € HT

---

#### 2. Lecteur Mobile (Pistolet)

**Modèle:** Zebra MC3300R ou équivalent

**Spécifications:**
- Fréquence: UHF RFID
- Portée: jusqu'à 3m
- Écran: Android
- Batterie: Journée complète
- Robuste: IP65

**Utilisation:**
- Scan mobile par chauffeurs
- Inventaires manuels
- Vérifications ponctuelles

**Prix:** ~1500-2000 € HT par unité

---

### API d'Intégration

```python
# rfid_reader_api.py

from typing import List
import asyncio

class RFIDReaderAPI:
    """Interface avec lecteurs RFID hardware"""
    
    def __init__(self, reader_ip: str, reader_port: int):
        self.ip = reader_ip
        self.port = reader_port
        self.connected = False
    
    async def connect(self):
        """Se connecter au lecteur RFID"""
        # Implémentation spécifique au fabricant
        pass
    
    async def scan_single(self, timeout: int = 5) -> str:
        """Scanner un seul tag RFID"""
        # Retourne UID du tag
        pass
    
    async def scan_multiple(self, timeout: int = 30) -> List[str]:
        """Scanner plusieurs tags RFID"""
        # Retourne liste des UIDs
        pass
    
    async def start_continuous_scan(self):
        """Démarrer scan continu (pour portique)"""
        pass
    
    async def stop_continuous_scan(self):
        """Arrêter scan continu"""
        pass
    
    def on_tag_detected(self, callback):
        """Callback lors détection tag"""
        pass

# Service d'intégration
class RFIDService:
    """Service métier RFID"""
    
    async def scan_and_register(
        self,
        reader: RFIDReaderAPI,
        context: ScanContext,
        session: AsyncSession
    ) -> RFIDScan:
        """
        Scanner et enregistrer dans DB
        """
        # 1. Scanner
        tag_uid = await reader.scan_single(timeout=5)
        
        if not tag_uid:
            raise RFIDScanError("Aucun tag détecté")
        
        # 2. Récupérer tag depuis DB
        rfid_tag = await self.get_tag_by_uid(tag_uid, session)
        
        if not rfid_tag:
            raise RFIDTagNotFoundError(f"Tag {tag_uid} inconnu")
        
        # 3. Vérifier statut
        if rfid_tag.status != RFIDStatus.ACTIF:
            raise RFIDTagInactiveError(f"Tag {tag_uid} inactif")
        
        # 4. Créer scan
        scan = RFIDScan(
            rfid_tag_id=rfid_tag.id,
            tag_uid=tag_uid,
            scan_type=context.scan_type,
            user_id=context.user_id,
            # ... autres champs
        )
        session.add(scan)
        
        # 5. Mettre à jour last_scan
        rfid_tag.last_scan_date = datetime.utcnow()
        rfid_tag.last_scan_location = context.location
        
        await session.commit()
        
        return scan
```

---

## 📊 RAPPORTS ET STATISTIQUES RFID

### KPIs RFID

```sql
-- 1. Taux de lecture réussie
SELECT 
    DATE(scan_date) as date,
    COUNT(*) as total_scans,
    COUNT(DISTINCT rfid_tag_id) as tags_uniques,
    AVG(signal_strength) as signal_moyen
FROM rfid_scans
WHERE scan_date >= NOW() - INTERVAL '30 days'
GROUP BY DATE(scan_date)
ORDER BY date DESC;

-- 2. Tags problématiques
SELECT 
    rt.tag_code,
    rt.status,
    COUNT(rs.id) as nombre_scans,
    MAX(rs.scan_date) as dernier_scan,
    NOW() - MAX(rs.scan_date) as jours_sans_scan
FROM rfid_tags rt
LEFT JOIN rfid_scans rs ON rt.id = rs.rfid_tag_id
WHERE rt.tag_type = 'PALETTE'
GROUP BY rt.id, rt.tag_code, rt.status
HAVING NOW() - MAX(rs.scan_date) > INTERVAL '30 days'
ORDER BY jours_sans_scan DESC;

-- 3. Performance par utilisateur
SELECT 
    u.first_name || ' ' || u.last_name as utilisateur,
    COUNT(rs.id) as scans_effectues,
    COUNT(DISTINCT DATE(rs.scan_date)) as jours_actifs,
    AVG(rs.read_count) as lectures_moyennes
FROM rfid_scans rs
JOIN users u ON rs.user_id = u.id
WHERE rs.scan_date >= NOW() - INTERVAL '30 days'
GROUP BY u.id, utilisateur
ORDER BY scans_effectues DESC;
```

---

## ⚠️ GESTION DES PROBLÈMES RFID

### Problèmes Courants

#### 1. Tag Non Détecté

**Causes:**
- Tag défectueux
- Batterie lecteur faible
- Interférences métalliques
- Distance trop grande

**Solutions:**
- Vérifier batterie lecteur
- Rapprocher lecteur du tag
- Réessayer plusieurs fois
- Signaler tag défectueux

---

#### 2. Lecture Multiple

**Causes:**
- Plusieurs tags dans le champ
- Réflexions radio

**Solutions:**
- Scanner tag par tag
- Utiliser mode scan unique
- Éloigner autres palettes

---

#### 3. Tag Perdu

**Procédure:**
1. Recherche RFID intensive
2. Vérifier historique scans
3. Si non trouvé après 7 jours:
   - Marquer status = PERDU
   - Créer nouveau tag
   - Alert management

```sql
-- Marquer tag comme perdu
UPDATE rfid_tags
SET 
    status = 'PERDU',
    date_desactivation = NOW(),
    notes = 'Tag perdu après recherche intensive'
WHERE id = 'UUID_TAG';

-- Créer nouveau tag pour la palette
INSERT INTO rfid_tags (
    tag_uid,
    tag_code,
    tag_type,
    palette_id,
    status
) VALUES (
    'NEW_UID',
    'RFID-2025-NEW',
    'PALETTE',
    'UUID_PALETTE',
    'ACTIF'
);
```

---

## 💰 COÛTS RFID

### Investissement Initial

| Élément | Quantité | Prix Unitaire | Total |
|---------|----------|---------------|-------|
| **Tags RFID Palette** | 500 | 1-2 € | 750-1000 € |
| **Lecteur Fixe (Portique)** | 2 | 2500 € | 5000 € |
| **Lecteur Mobile (Pistolet)** | 5 | 1750 € | 8750 € |
| **Antennes supplémentaires** | 4 | 200 € | 800 € |
| **Installation** | - | - | 2000 € |
| **Formation** | - | - | 1500 € |
| **TOTAL PHASE 1** | | | **18 800 € HT** |

### Coûts Récurrents

| Élément | Annuel |
|---------|--------|
| **Tags remplacement** | 500-1000 € |
| **Maintenance hardware** | 1500 € |
| **TOTAL ANNUEL** | **2000-2500 € HT** |

### ROI

**Gains estimés:**
- Réduction temps inventaire: -70% → 15h/mois économisées
- Réduction erreurs: -50% → Moins de litiges
- Palettes retrouvées: +40% → Moins d'achats

**ROI attendu:** 12-18 mois

---

## ✅ CHECKLIST IMPLÉMENTATION RFID

### Phase 1 : Palettes (6-8 semaines)

**Semaine 1-2: Achat Hardware**
- [ ] Commander lecteurs fixes
- [ ] Commander lecteurs mobiles
- [ ] Commander tags RFID
- [ ] Commander antennes

**Semaine 3-4: Installation**
- [ ] Installer portiques entrée/sortie
- [ ] Installer lecteurs zones de chargement
- [ ] Configurer réseau
- [ ] Tests connectivity

**Semaine 5-6: Intégration Logicielle**
- [ ] Développer API intégration
- [ ] Tests scan simples
- [ ] Tests scan multiples
- [ ] Tests portiques automatiques

**Semaine 7-8: Déploiement**
- [ ] Former opérateurs
- [ ] Former chauffeurs
- [ ] Phase pilote (50 palettes)
- [ ] Ajustements
- [ ] Déploiement complet

---

## 📞 SUPPORT RFID

### Contacts Fournisseurs

**Hardware:**
- Zebra Technologies
- Impinj
- Alien Technology

**Tags:**
- Confidex
- Smartrac
- Avery Dennison

### Support Technique

**En cas de problème:**
1. Consulter documentation hardware
2. Vérifier connexions réseau
3. Tester avec autre lecteur
4. Contacter support fournisseur

---

## 🎯 CONCLUSION

La stratégie RFID de GazTracker repose sur :

✅ **Phase 1 (ACTUEL):** Tags sur palettes
- Implémentation mature
- ROI prouvé
- Scalable

🔮 **Phase 2 (FUTUR):** Tags sur bouteilles
- Traçabilité ultime
- Anti-contrefaçon
- Nécessite R&D

La technologie RFID est le **pilier central** de la traçabilité GazTracker, permettant une identification rapide, fiable et automatisée tout au long de la chaîne logistique.

---

**Version:** 1.0  
**Date:** 20 novembre 2024  
**Statut:** Phase 1 (Palettes) ✅ | Phase 2 (Bouteilles) 🔮

