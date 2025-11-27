# 🗄️ SCHÉMA DE BASE DE DONNÉES - GazTracker (Corrigé)

## 📊 VUE D'ENSEMBLE

Ce document présente la nouvelle structure de base de données adaptée à la réalité opérationnelle.

---

## 🏗️ HIÉRARCHIE ORGANISATIONNELLE

### 1. Table `groupes`

```sql
CREATE TABLE groupes (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                VARCHAR(255) NOT NULL,
    code                VARCHAR(50) UNIQUE NOT NULL,
    address             VARCHAR(500),
    city                VARCHAR(100),
    postal_code         VARCHAR(20),
    country             VARCHAR(100) DEFAULT 'Côte d''Ivoire',
    phone               VARCHAR(20),
    email               VARCHAR(255),
    is_active           BOOLEAN DEFAULT TRUE,
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_groupes_code ON groupes(code);
CREATE INDEX idx_groupes_active ON groupes(is_active);
```

**Exemples de données:**
- Pétroci Holding (PETROCI)
- SODIGAZ (SODIGAZ)
- Pétro Ivoire (PETROIV)
- Total Energies CI (TOTALCI)

---

### 2. Table `grand_distributeurs`

```sql
CREATE TABLE grand_distributeurs (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                    VARCHAR(255) NOT NULL,
    code                    VARCHAR(50) UNIQUE NOT NULL,
    groupe_id               UUID REFERENCES groupes(id) ON DELETE SET NULL,
    address                 VARCHAR(500),
    city                    VARCHAR(100),
    postal_code             VARCHAR(20),
    country                 VARCHAR(100) DEFAULT 'Côte d''Ivoire',
    phone                   VARCHAR(20),
    email                   VARCHAR(255),
    contact_name            VARCHAR(255),
    contact_phone           VARCHAR(20),
    is_active               BOOLEAN DEFAULT TRUE,
    notes                   TEXT,
    created_at              TIMESTAMP DEFAULT NOW(),
    updated_at              TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_grand_dist_groupe ON grand_distributeurs(groupe_id);
CREATE INDEX idx_grand_dist_code ON grand_distributeurs(code);
CREATE INDEX idx_grand_dist_active ON grand_distributeurs(is_active);
```

**Exemples de données:**
- CEV3 (PETROCI) - Groupe: Pétroci
- TDC WEST AFRICA - Groupe: Pétroci
- Distribution SODIGAZ - Groupe: SODIGAZ

---

### 3. Table `centres_remplisseurs`

```sql
CREATE TABLE centres_remplisseurs (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                        VARCHAR(255) NOT NULL,
    code                        VARCHAR(50) UNIQUE NOT NULL,
    grand_distributeur_id       UUID REFERENCES grand_distributeurs(id) ON DELETE CASCADE,
    
    -- Adresse complète
    address                     VARCHAR(500) NOT NULL,
    city                        VARCHAR(100) NOT NULL,
    postal_code                 VARCHAR(20),
    country                     VARCHAR(100) DEFAULT 'Côte d''Ivoire',
    
    -- Coordonnées GPS
    latitude                    DECIMAL(10, 8),
    longitude                   DECIMAL(11, 8),
    
    -- Contact
    phone                       VARCHAR(20),
    email                       VARCHAR(255),
    contact_name                VARCHAR(255),
    contact_phone               VARCHAR(20),
    
    -- Capacité
    capacity_b28                INTEGER,  -- Capacité palettes B28
    capacity_b12                INTEGER,  -- Capacité palettes B12
    capacity_b6                 INTEGER,  -- Capacité palettes B6
    
    is_active                   BOOLEAN DEFAULT TRUE,
    notes                       TEXT,
    created_at                  TIMESTAMP DEFAULT NOW(),
    updated_at                  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_centres_grand_dist ON centres_remplisseurs(grand_distributeur_id);
CREATE INDEX idx_centres_code ON centres_remplisseurs(code);
CREATE INDEX idx_centres_active ON centres_remplisseurs(is_active);
CREATE INDEX idx_centres_location ON centres_remplisseurs(latitude, longitude);
```

**Exemples de données:**
- Atelier de TDC WEST AFRICA Sarl (Yopougon)
- Centre CEV3 Abidjan (Zone Industrielle)
- Centre Remplisseur Bouaké

---

### 4. Table `partners` (Modifiée)

```sql
CREATE TYPE partner_type AS ENUM (
    'GROSSISTE',
    'REVENDEUR',
    'TRANSPORTEUR',
    'AUTRE'
);

CREATE TABLE partners (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                    VARCHAR(255) NOT NULL,
    type                    partner_type NOT NULL DEFAULT 'GROSSISTE',
    code                    VARCHAR(50) UNIQUE NOT NULL,
    
    -- Pour REVENDEUR: lien avec son grossiste
    parent_grossiste_id     UUID REFERENCES partners(id) ON DELETE SET NULL,
    
    -- Adresse
    address                 VARCHAR(500),
    city                    VARCHAR(100),
    postal_code             VARCHAR(20),
    country                 VARCHAR(100) DEFAULT 'Côte d''Ivoire',
    
    -- Contact
    phone                   VARCHAR(20),
    email                   VARCHAR(255),
    contact_name            VARCHAR(255),
    contact_phone           VARCHAR(20),
    
    is_active               BOOLEAN DEFAULT TRUE,
    notes                   TEXT,
    created_at              TIMESTAMP DEFAULT NOW(),
    updated_at              TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_partners_type ON partners(type);
CREATE INDEX idx_partners_code ON partners(code);
CREATE INDEX idx_partners_active ON partners(is_active);
CREATE INDEX idx_partners_parent ON partners(parent_grossiste_id);
```

**Hiérarchie:**
- Grossiste: `parent_grossiste_id = NULL`
- Revendeur: `parent_grossiste_id → ID du grossiste`

---

### 5. Table `depots`

```sql
CREATE TABLE depots (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                    VARCHAR(255) NOT NULL,
    code                    VARCHAR(50) UNIQUE NOT NULL,
    partner_id              UUID REFERENCES partners(id) ON DELETE CASCADE,
    
    -- Localisation
    address                 VARCHAR(500) NOT NULL,
    city                    VARCHAR(100) NOT NULL,
    postal_code             VARCHAR(20),
    latitude                DECIMAL(10, 8),
    longitude               DECIMAL(11, 8),
    
    -- Contact sur place
    contact_name            VARCHAR(255),
    contact_phone           VARCHAR(20),
    
    -- Capacité
    capacity_b28            INTEGER,
    capacity_b12            INTEGER,
    capacity_b6             INTEGER,
    
    is_active               BOOLEAN DEFAULT TRUE,
    is_main_depot           BOOLEAN DEFAULT FALSE,  -- Dépôt principal
    notes                   TEXT,
    created_at              TIMESTAMP DEFAULT NOW(),
    updated_at              TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_depots_partner ON depots(partner_id);
CREATE INDEX idx_depots_code ON depots(code);
CREATE INDEX idx_depots_active ON depots(is_active);
CREATE INDEX idx_depots_main ON depots(is_main_depot);
CREATE INDEX idx_depots_location ON depots(latitude, longitude);
```

---

## 📦 GESTION DES PALETTES

### 6. Table `palettes` (Modifiée)

```sql
CREATE TYPE palette_type AS ENUM ('B6', 'B12', 'B28');

CREATE TYPE palette_status AS ENUM (
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

CREATE TABLE palettes (
    id                              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identifiants
    serial_number                   VARCHAR(20) UNIQUE NOT NULL,
    reference_code                  VARCHAR(50) UNIQUE,
    rfid_tag_id                     UUID REFERENCES rfid_tags(id) ON DELETE SET NULL UNIQUE,
    
    -- Type et caractéristiques
    type                            palette_type NOT NULL,
    capacity                        INTEGER,  -- Nombre de bouteilles
    manufacturing_date              DATE,
    
    -- Statut
    status                          palette_status NOT NULL DEFAULT 'CREATION',
    
    -- Localisation actuelle
    centre_remplisseur_actuel_id    UUID REFERENCES centres_remplisseurs(id) ON DELETE SET NULL,
    depot_actuel_id                 UUID REFERENCES depots(id) ON DELETE SET NULL,
    partner_actuel_id               UUID REFERENCES partners(id) ON DELETE SET NULL,
    
    -- Trajet en cours
    bon_enlevement_actuel_id        UUID REFERENCES bons_enlevement(id) ON DELETE SET NULL,
    bon_retour_actuel_id            UUID REFERENCES bons_reception_retour(id) ON DELETE SET NULL,
    
    -- GPS
    location_latitude               DECIMAL(10, 8),
    location_longitude              DECIMAL(11, 8),
    location_address                VARCHAR(500),
    
    -- Audit
    created_by_id                   UUID REFERENCES users(id) ON DELETE SET NULL,
    notes                           TEXT,
    created_at                      TIMESTAMP DEFAULT NOW(),
    updated_at                      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_palettes_serial ON palettes(serial_number);
CREATE INDEX idx_palettes_rfid ON palettes(rfid_tag_id);
CREATE INDEX idx_palettes_type_status ON palettes(type, status);
CREATE INDEX idx_palettes_centre_actuel ON palettes(centre_remplisseur_actuel_id);
CREATE INDEX idx_palettes_depot_actuel ON palettes(depot_actuel_id);
CREATE INDEX idx_palettes_partner_actuel ON palettes(partner_actuel_id);
CREATE INDEX idx_palettes_bon_enlevement ON palettes(bon_enlevement_actuel_id);
CREATE INDEX idx_palettes_bon_retour ON palettes(bon_retour_actuel_id);
```

---

## 🚚 FLUX ALLER - BON D'ENLÈVEMENT

### 7. Table `bons_enlevement`

```sql
CREATE TYPE bon_enlevement_status AS ENUM (
    'CREATION',
    'VALIDE',
    'EN_CHARGEMENT',
    'EN_ROUTE',
    'EN_LIVRAISON',
    'TERMINE',
    'ANNULE'
);

CREATE TABLE bons_enlevement (
    id                              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Numéros
    numero_bon                      VARCHAR(50) UNIQUE NOT NULL,
    reference                       VARCHAR(100) UNIQUE NOT NULL,
    
    -- Origine
    centre_remplisseur_id           UUID REFERENCES centres_remplisseurs(id) ON DELETE SET NULL,
    
    -- Destination
    grossiste_id                    UUID REFERENCES partners(id) ON DELETE SET NULL,
    depot_principal_id              UUID REFERENCES depots(id) ON DELETE SET NULL,
    
    -- Transport
    vehicule_immatriculation        VARCHAR(50),
    chauffeur_nom                   VARCHAR(255),
    chauffeur_societe               VARCHAR(255),
    chauffeur_phone                 VARCHAR(20),
    
    -- Dates
    date_creation                   TIMESTAMP DEFAULT NOW(),
    date_validation                 TIMESTAMP,
    date_chargement                 TIMESTAMP,
    date_depart                     TIMESTAMP,
    date_arrivee_finale             TIMESTAMP,
    
    -- Statut
    status                          bon_enlevement_status DEFAULT 'CREATION',
    
    -- Informations
    observations                    TEXT,
    instructions_livraison          TEXT,
    
    -- Validation
    validateur_centre_id            UUID REFERENCES users(id) ON DELETE SET NULL,
    recepteur_final_id              UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- OTP sécurité
    otp_code                        VARCHAR(10),
    otp_expiry                      TIMESTAMP,
    
    -- Compteurs
    palette_count                   INTEGER DEFAULT 0,
    livraison_count                 INTEGER DEFAULT 0,
    
    created_at                      TIMESTAMP DEFAULT NOW(),
    updated_at                      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_bons_enl_numero ON bons_enlevement(numero_bon);
CREATE INDEX idx_bons_enl_centre ON bons_enlevement(centre_remplisseur_id);
CREATE INDEX idx_bons_enl_grossiste ON bons_enlevement(grossiste_id);
CREATE INDEX idx_bons_enl_status ON bons_enlevement(status);
CREATE INDEX idx_bons_enl_date_creation ON bons_enlevement(date_creation);
CREATE INDEX idx_bons_enl_date_depart ON bons_enlevement(date_depart);
```

---

### 8. Table `livraisons_details`

```sql
CREATE TYPE livraison_status AS ENUM (
    'EN_ATTENTE',
    'EN_COURS',
    'LIVREE',
    'PROBLEME',
    'ANNULEE'
);

CREATE TABLE livraisons_details (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bon_enlevement_id       UUID REFERENCES bons_enlevement(id) ON DELETE CASCADE,
    ordre_livraison         INTEGER NOT NULL,  -- 1, 2, 3...
    
    -- Destination
    depot_id                UUID REFERENCES depots(id) ON DELETE SET NULL,
    revendeur_id            UUID REFERENCES partners(id) ON DELETE SET NULL,
    
    -- Dates
    date_arrivee            TIMESTAMP,
    date_depart             TIMESTAMP,
    
    -- Statut
    status                  livraison_status DEFAULT 'EN_ATTENTE',
    
    -- Réception
    recepteur_nom           VARCHAR(255),
    recepteur_signature     TEXT,  -- Base64 ou path
    observations            TEXT,
    problemes               TEXT,
    
    -- GPS
    latitude_arrivee        DECIMAL(10, 8),
    longitude_arrivee       DECIMAL(11, 8),
    
    created_at              TIMESTAMP DEFAULT NOW(),
    updated_at              TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_livraisons_bon ON livraisons_details(bon_enlevement_id);
CREATE INDEX idx_livraisons_depot ON livraisons_details(depot_id);
CREATE INDEX idx_livraisons_ordre ON livraisons_details(bon_enlevement_id, ordre_livraison);
```

---

### 9. Table `livraison_palettes` (Association Many-to-Many)

```sql
CREATE TABLE livraison_palettes (
    livraison_detail_id     UUID REFERENCES livraisons_details(id) ON DELETE CASCADE,
    palette_id              UUID REFERENCES palettes(id) ON DELETE CASCADE,
    created_at              TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (livraison_detail_id, palette_id)
);

CREATE INDEX idx_livr_pal_livraison ON livraison_palettes(livraison_detail_id);
CREATE INDEX idx_livr_pal_palette ON livraison_palettes(palette_id);
```

---

### 10. Table `collectes_vides`

```sql
CREATE TABLE collectes_vides (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bon_enlevement_id           UUID REFERENCES bons_enlevement(id) ON DELETE CASCADE,
    livraison_detail_id         UUID REFERENCES livraisons_details(id) ON DELETE SET NULL,
    depot_id                    UUID REFERENCES depots(id) ON DELETE SET NULL,
    
    -- Détails collecte
    type_bouteille              palette_type NOT NULL,
    quantite_bouteilles_vides   INTEGER NOT NULL DEFAULT 0,
    quantite_palettes_vides     INTEGER NOT NULL DEFAULT 0,
    
    date_collecte               TIMESTAMP DEFAULT NOW(),
    collecteur_nom              VARCHAR(255),
    observations                TEXT,
    
    created_at                  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_collectes_bon ON collectes_vides(bon_enlevement_id);
CREATE INDEX idx_collectes_livraison ON collectes_vides(livraison_detail_id);
CREATE INDEX idx_collectes_depot ON collectes_vides(depot_id);
```

---

## 🔙 FLUX RETOUR - BON DE RÉCEPTION RETOUR

### 11. Table `bons_reception_retour`

```sql
CREATE TYPE bon_retour_status AS ENUM (
    'CREATION',
    'EN_ROUTE',
    'ARRIVE',
    'EN_CONTROLE',
    'VALIDE',
    'REFUSE'
);

CREATE TABLE bons_reception_retour (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Numéros
    numero_bl                   VARCHAR(50) UNIQUE NOT NULL,
    numero_reception            VARCHAR(50) UNIQUE NOT NULL,
    
    -- Origine
    grossiste_id                UUID REFERENCES partners(id) ON DELETE SET NULL,
    depot_depart_id             UUID REFERENCES depots(id) ON DELETE SET NULL,
    
    -- Destination
    centre_remplisseur_id       UUID REFERENCES centres_remplisseurs(id) ON DELETE SET NULL,
    
    -- Transport
    vehicule_immatriculation    VARCHAR(50),
    transporteur_nom            VARCHAR(255),
    transporteur_societe        VARCHAR(255),
    
    -- Dates
    date_creation               TIMESTAMP DEFAULT NOW(),
    date_depart                 TIMESTAMP,
    date_arrivee                TIMESTAMP,
    date_controle               TIMESTAMP,
    date_validation             TIMESTAMP,
    
    -- Statut
    status                      bon_retour_status DEFAULT 'CREATION',
    
    -- Contrôle qualité
    controleur_id               UUID REFERENCES users(id) ON DELETE SET NULL,
    magasinier_id               UUID REFERENCES users(id) ON DELETE SET NULL,
    observations                TEXT,
    manquants                   TEXT,
    
    -- Signatures
    client_signature            TEXT,
    magasinier_signature        TEXT,
    controleur_signature        TEXT,
    
    -- Compteurs
    palette_count               INTEGER DEFAULT 0,
    palette_acceptees           INTEGER DEFAULT 0,
    palette_refusees            INTEGER DEFAULT 0,
    
    created_at                  TIMESTAMP DEFAULT NOW(),
    updated_at                  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_bons_ret_numero_bl ON bons_reception_retour(numero_bl);
CREATE INDEX idx_bons_ret_grossiste ON bons_reception_retour(grossiste_id);
CREATE INDEX idx_bons_ret_centre ON bons_reception_retour(centre_remplisseur_id);
CREATE INDEX idx_bons_ret_status ON bons_reception_retour(status);
CREATE INDEX idx_bons_ret_date_creation ON bons_reception_retour(date_creation);
```

---

### 12. Table `details_retour`

```sql
CREATE TABLE details_retour (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bon_reception_retour_id     UUID REFERENCES bons_reception_retour(id) ON DELETE CASCADE,
    
    -- Type de matériel
    libelle                     VARCHAR(255),
    type_bouteille              palette_type,
    
    -- Quantités
    quantite_palettes           INTEGER DEFAULT 0,
    quantite_bouteilles_vides   INTEGER DEFAULT 0,
    quantite_vrac               INTEGER DEFAULT 0,
    
    -- Références
    references_palettes         TEXT,  -- Ex: "35-53-55, 52-59-61"
    
    observations                TEXT,
    
    created_at                  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_details_ret_bon ON details_retour(bon_reception_retour_id);
```

---

## 📜 HISTORIQUE ET AUDIT

### 13. Table `palette_movements` (Modifiée)

```sql
CREATE TYPE movement_action AS ENUM (
    'CREATION',
    'CHARGEMENT_CENTRE',
    'DEPART_CENTRE',
    'LIVRAISON_DEPOT',
    'RECEPTION_DEPOT',
    'STOCKAGE',
    'RETOUR_DEPART',
    'RETOUR_ARRIVEE',
    'CONTROLE_QUALITE',
    'VALIDATION_RETOUR',
    'MISE_HORS_SERVICE'
);

CREATE TABLE palette_movements (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    palette_id                  UUID REFERENCES palettes(id) ON DELETE CASCADE,
    
    -- Documents associés
    bon_enlevement_id           UUID REFERENCES bons_enlevement(id) ON DELETE SET NULL,
    bon_reception_retour_id     UUID REFERENCES bons_reception_retour(id) ON DELETE SET NULL,
    livraison_detail_id         UUID REFERENCES livraisons_details(id) ON DELETE SET NULL,
    
    -- Localisation
    centre_remplisseur_id       UUID REFERENCES centres_remplisseurs(id) ON DELETE SET NULL,
    depot_id                    UUID REFERENCES depots(id) ON DELETE SET NULL,
    partner_id                  UUID REFERENCES partners(id) ON DELETE SET NULL,
    
    -- Action
    action                      movement_action NOT NULL,
    status_before               VARCHAR(50),
    status_after                VARCHAR(50),
    
    -- Date/Heure
    timestamp                   TIMESTAMP DEFAULT NOW(),
    
    -- Utilisateur
    user_id                     UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- GPS
    latitude                    DECIMAL(10, 8),
    longitude                   DECIMAL(11, 8),
    location_address            VARCHAR(500),
    
    -- Détails supplémentaires
    details                     JSONB,
    notes                       TEXT
);

CREATE INDEX idx_movements_palette ON palette_movements(palette_id);
CREATE INDEX idx_movements_timestamp ON palette_movements(timestamp);
CREATE INDEX idx_movements_action ON palette_movements(action);
CREATE INDEX idx_movements_bon_enl ON palette_movements(bon_enlevement_id);
CREATE INDEX idx_movements_bon_ret ON palette_movements(bon_reception_retour_id);
```

---

## 👥 UTILISATEURS ET AUTHENTIFICATION

### 14. Table `users` (Modifiée)

```sql
CREATE TYPE user_role AS ENUM (
    'ADMIN',
    'RESPONSABLE_CENTRE',
    'OPERATEUR_CENTRE',
    'MAGASINIER_CENTRE',
    'CONTROLEUR_QUALITE',
    'CHAUFFEUR',
    'RESPONSABLE_GROSSISTE',
    'OPERATEUR_GROSSISTE',
    'RESPONSABLE_REVENDEUR',
    'OPERATEUR_REVENDEUR'
);

CREATE TABLE users (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Authentification
    email                   VARCHAR(255) UNIQUE NOT NULL,
    password_hash           VARCHAR(255) NOT NULL,
    
    -- Informations personnelles
    first_name              VARCHAR(100) NOT NULL,
    last_name               VARCHAR(100) NOT NULL,
    phone_number            VARCHAR(20),
    
    -- Rôle et affectation
    role                    user_role NOT NULL DEFAULT 'OPERATEUR_CENTRE',
    
    -- Affectation organisationnelle
    centre_remplisseur_id   UUID REFERENCES centres_remplisseurs(id) ON DELETE SET NULL,
    partner_id              UUID REFERENCES partners(id) ON DELETE SET NULL,
    depot_id                UUID REFERENCES depots(id) ON DELETE SET NULL,
    
    -- Statut
    is_active               BOOLEAN DEFAULT TRUE,
    is_verified             BOOLEAN DEFAULT FALSE,
    
    created_at              TIMESTAMP DEFAULT NOW(),
    updated_at              TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_centre ON users(centre_remplisseur_id);
CREATE INDEX idx_users_partner ON users(partner_id);
```

---

## 📊 DIAGRAMME RELATIONNEL

```
┌─────────────┐
│   groupes   │
└──────┬──────┘
       │ 1:N
       ↓
┌──────────────────────┐
│ grand_distributeurs  │
└──────┬───────────────┘
       │ 1:N
       ↓
┌───────────────────────┐      ┌────────────┐
│ centres_remplisseurs  │      │  partners  │
└──────┬────────────────┘      └─────┬──────┘
       │                              │
       │ 1:N                          │ 1:N
       │                              │
       │         ┌────────────────────┼──────────────┐
       │         │                    │              │
       ↓         ↓                    ↓              ↓
┌──────────────────────┐      ┌─────────────┐  ┌─────────────┐
│  bons_enlevement     │      │   depots    │  │  partners   │
│  (ALLER)             │      │             │  │  (revendeur)│
└──────┬───────────────┘      └──────┬──────┘  └─────────────┘
       │                             │
       │ 1:N                         │
       ↓                             │
┌──────────────────────┐             │
│ livraisons_details   │─────────────┘
└──────┬───────────────┘
       │
       │ M:N
       ↓
┌──────────────────────┐
│     palettes         │←──────────────────┐
└──────┬───────────────┘                   │
       │                                   │
       │ 1:N                               │
       ↓                                   │
┌──────────────────────┐                   │
│ palette_movements    │                   │
└──────────────────────┘                   │
                                           │
┌──────────────────────┐                   │
│ bons_reception_retour│                   │
│  (RETOUR)            │───────────────────┘
└──────┬───────────────┘
       │ 1:N
       ↓
┌──────────────────────┐
│   details_retour     │
└──────────────────────┘
```

---

## 🔐 CONTRAINTES ET RÈGLES MÉTIER

### Contraintes de Cohérence

```sql
-- Un revendeur ne peut pas être parent d'un autre revendeur
ALTER TABLE partners
ADD CONSTRAINT check_parent_is_grossiste
CHECK (
    parent_grossiste_id IS NULL OR
    type = 'REVENDEUR'
);

-- Une palette ne peut être qu'à un seul endroit à la fois
ALTER TABLE palettes
ADD CONSTRAINT check_single_location
CHECK (
    (centre_remplisseur_actuel_id IS NOT NULL)::int +
    (depot_actuel_id IS NOT NULL)::int +
    (partner_actuel_id IS NOT NULL)::int <= 1
);

-- Une palette ne peut être dans qu'un seul trajet à la fois
ALTER TABLE palettes
ADD CONSTRAINT check_single_journey
CHECK (
    (bon_enlevement_actuel_id IS NOT NULL)::int +
    (bon_retour_actuel_id IS NOT NULL)::int <= 1
);

-- Ordre de livraison doit être unique par bon
ALTER TABLE livraisons_details
ADD CONSTRAINT unique_ordre_par_bon
UNIQUE (bon_enlevement_id, ordre_livraison);
```

---

## 📈 VUES UTILES

### Vue: Stock par Centre

```sql
CREATE VIEW v_stock_par_centre AS
SELECT
    c.id AS centre_id,
    c.name AS centre_name,
    p.type AS palette_type,
    COUNT(*) AS quantite,
    SUM(p.capacity) AS total_bouteilles
FROM centres_remplisseurs c
LEFT JOIN palettes p ON p.centre_remplisseur_actuel_id = c.id
WHERE p.status = 'EN_STOCK_CENTRE'
GROUP BY c.id, c.name, p.type;
```

### Vue: Stock par Dépôt

```sql
CREATE VIEW v_stock_par_depot AS
SELECT
    d.id AS depot_id,
    d.name AS depot_name,
    pt.name AS partner_name,
    p.type AS palette_type,
    COUNT(*) AS quantite,
    SUM(p.capacity) AS total_bouteilles
FROM depots d
JOIN partners pt ON d.partner_id = pt.id
LEFT JOIN palettes p ON p.depot_actuel_id = d.id
WHERE p.status IN ('EN_STOCK_GROSSISTE', 'EN_STOCK_REVENDEUR')
GROUP BY d.id, d.name, pt.name, p.type;
```

### Vue: Palettes en Circulation

```sql
CREATE VIEW v_palettes_en_circulation AS
SELECT
    p.type,
    p.status,
    COUNT(*) AS quantite
FROM palettes p
WHERE p.status NOT IN ('EN_STOCK_CENTRE', 'HORS_SERVICE')
GROUP BY p.type, p.status;
```

### Vue: Performance Chauffeurs

```sql
CREATE VIEW v_performance_chauffeurs AS
SELECT
    be.chauffeur_nom,
    COUNT(DISTINCT be.id) AS bons_realises,
    SUM(be.palette_count) AS palettes_livrees,
    AVG(EXTRACT(EPOCH FROM (be.date_arrivee_finale - be.date_depart))/3600) AS duree_moyenne_heures
FROM bons_enlevement be
WHERE be.status = 'TERMINE'
GROUP BY be.chauffeur_nom
ORDER BY palettes_livrees DESC;
```

---

## 🎯 REQUÊTES COURANTES

### 1. Palettes d'un Bon d'Enlèvement

```sql
SELECT
    p.serial_number,
    p.type,
    p.status,
    ld.ordre_livraison,
    d.name AS destination_depot
FROM palettes p
JOIN livraison_palettes lp ON p.id = lp.palette_id
JOIN livraisons_details ld ON lp.livraison_detail_id = ld.id
JOIN depots d ON ld.depot_id = d.id
WHERE p.bon_enlevement_actuel_id = 'UUID_DU_BON'
ORDER BY ld.ordre_livraison, p.serial_number;
```

### 2. Historique Complet d'une Palette

```sql
SELECT
    pm.timestamp,
    pm.action,
    pm.status_before,
    pm.status_after,
    u.first_name || ' ' || u.last_name AS utilisateur,
    COALESCE(c.name, d.name, pt.name) AS localisation
FROM palette_movements pm
LEFT JOIN users u ON pm.user_id = u.id
LEFT JOIN centres_remplisseurs c ON pm.centre_remplisseur_id = c.id
LEFT JOIN depots d ON pm.depot_id = d.id
LEFT JOIN partners pt ON pm.partner_id = pt.id
WHERE pm.palette_id = 'UUID_PALETTE'
ORDER BY pm.timestamp DESC;
```

### 3. Bons d'Enlèvement en Cours

```sql
SELECT
    be.numero_bon,
    be.status,
    c.name AS centre_depart,
    g.name AS grossiste,
    be.chauffeur_nom,
    be.palette_count,
    be.date_depart,
    be.date_arrivee_finale
FROM bons_enlevement be
JOIN centres_remplisseurs c ON be.centre_remplisseur_id = c.id
JOIN partners g ON be.grossiste_id = g.id
WHERE be.status IN ('EN_ROUTE', 'EN_LIVRAISON')
ORDER BY be.date_depart DESC;
```

### 4. Taux de Retour par Grossiste

```sql
SELECT
    p.name AS grossiste,
    COUNT(DISTINCT be.id) AS bons_enlevement,
    COUNT(DISTINCT brr.id) AS bons_retour,
    ROUND(COUNT(DISTINCT brr.id)::numeric / NULLIF(COUNT(DISTINCT be.id), 0) * 100, 2) AS taux_retour_pct
FROM partners p
LEFT JOIN bons_enlevement be ON p.id = be.grossiste_id
LEFT JOIN bons_reception_retour brr ON p.id = brr.grossiste_id
WHERE p.type = 'GROSSISTE'
GROUP BY p.id, p.name
ORDER BY taux_retour_pct DESC;
```

---

## 🔄 TRIGGERS

### Auto-Increment Compteurs

```sql
-- Trigger: Mettre à jour palette_count du bon d'enlèvement
CREATE OR REPLACE FUNCTION update_bon_enlevement_palette_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE bons_enlevement
    SET palette_count = (
        SELECT COUNT(*)
        FROM palettes
        WHERE bon_enlevement_actuel_id = NEW.bon_enlevement_actuel_id
    )
    WHERE id = NEW.bon_enlevement_actuel_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_palette_count
AFTER INSERT OR UPDATE ON palettes
FOR EACH ROW
WHEN (NEW.bon_enlevement_actuel_id IS NOT NULL)
EXECUTE FUNCTION update_bon_enlevement_palette_count();
```

### Audit Automatique

```sql
-- Trigger: Créer mouvement automatiquement lors d'un changement de statut
CREATE OR REPLACE FUNCTION log_palette_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO palette_movements (
            palette_id,
            action,
            status_before,
            status_after,
            centre_remplisseur_id,
            depot_id,
            partner_id,
            timestamp
        ) VALUES (
            NEW.id,
            'STATUS_CHANGE',
            OLD.status::text,
            NEW.status::text,
            NEW.centre_remplisseur_actuel_id,
            NEW.depot_actuel_id,
            NEW.partner_actuel_id,
            NOW()
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_log_status_change
AFTER UPDATE ON palettes
FOR EACH ROW
EXECUTE FUNCTION log_palette_status_change();
```

---

## 📊 OPTIMISATIONS

### Partitionnement (pour gros volumes)

```sql
-- Partitionner palette_movements par mois
CREATE TABLE palette_movements_2025_01 PARTITION OF palette_movements
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE palette_movements_2025_02 PARTITION OF palette_movements
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Etc.
```

### Index Full-Text Search

```sql
-- Pour recherche textuelle sur observations, notes, etc.
CREATE INDEX idx_bons_enl_observations_fts
ON bons_enlevement
USING gin(to_tsvector('french', observations));

CREATE INDEX idx_palettes_notes_fts
ON palettes
USING gin(to_tsvector('french', notes));
```

---

**FIN DU SCHÉMA DE BASE DE DONNÉES**

Ce schéma complet assure la traçabilité totale des palettes depuis leur création jusqu'à leur retour, en passant par tous les acteurs de la chaîne logistique.

