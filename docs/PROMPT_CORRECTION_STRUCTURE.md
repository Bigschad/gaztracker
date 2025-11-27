# 🔧 PROMPT DE CORRECTION - Structure GazTracker selon Réalité Terrain

## 📋 CONTEXTE

Le projet GazTracker actuel utilise une structure simplifiée qui ne reflète pas la réalité opérationnelle de la chaîne de distribution du gaz butane. Ce document décrit les changements nécessaires pour aligner le système avec l'organisation réelle du terrain.

---

## 🏢 ORGANISATION RÉELLE DU TERRAIN

### Hiérarchie des Acteurs

```
GROUPE (Pétroci, SODIGAZ, Pétro Ivoire, etc.)
    ↓
GRAND DISTRIBUTEUR (plusieurs par groupe)
    ↓
CENTRE REMPLISSEUR (plusieurs par grand distributeur)
    ↓
GROSSISTE (client du grand ditributeur reavitallé par ses centres remplisseur)
    ↓
REVENDEUR (client du grossiste)
```

### Description des Acteurs

1. **GROUPE**
   - Grande entité chargée de fournir le gaz butane
   - Exemples: Pétroci Holding, SODIGAZ, Pétro Ivoire, Total Energies CI
   - Propriétaire des infrastructures majeures

2. **GRAND DISTRIBUTEUR**
   - Opère pour le compte d'un GROUPE
   - Gère plusieurs centres remplisseurs
   - Exemples: CEV3 (Petroci), IDC WEST AFRICA

3. **CENTRE REMPLISSEUR**
   - Infrastructure physique de conditionnement et remplissage
   - Appartient au grand distributeur
   - Point de départ des expéditions
   - Stocke et remplit les bouteilles de gaz
   - Exemples: Atelier de IDC WEST AFRICA Sarl, Centre de CEV3

4. **GROSSISTE**
   - Client du centre remplisseur
   - Possède un ou plusieurs dépôts
   - Possède ou affrète des camions pour le transport
   - Achète les palettes de bouteilles pleines
   - Revend aux revendeurs ou au public

5. **REVENDEUR**
   - Client du grossiste
   - Possède un ou plusieurs dépôts
   - Revend au détail

---

## 🚚 FLUX OPÉRATIONNEL

### 1️⃣ TRAJET ALLER - Bon d'Enlèvement

**Document:** Bon d'enlèvement (voir image fournie)

**Point de départ:** Centre remplisseur du grand distributeur

**Point d'arrivée:** 
- Option A: Dépôt du grossiste (livraison directe)
- Option B: Tour des dépôts des revendeurs du grossiste (livraison multi-points)

**Transport:** 
- Camion affrété par le GROSSISTE
- Chauffeur: Employé ou prestataire du grossiste

**Contenu du trajet:**
- **CHARGEMENT**: Palettes avec bouteilles PLEINES (depuis centre remplisseur)
- **COLLECTE**: Palettes avec bouteilles VIDES (depuis dépôts visités)
- **DESTINATION FINALE**: Les palettes pleines terminent au dépôt du grossiste (après éventuelles livraisons aux revendeurs)

**Informations du bon d'enlèvement:**
- Numéro du bon
- Date
- Véhicule (immatriculation)
- Chauffeur (nom, société)
- Client (Grossiste)
- Référence des palettes (numéros de série)
- Désignation (type de bouteilles: B6, B12, B28)
- Quantité (#24# dans l'exemple = nombre de bouteilles)
- Observations (destination, instructions spéciales)
- Signatures (émetteur, récepteur)

### 2️⃣ TRAJET RETOUR - Bon de Réception Retour

**Document:** Bon de réception retour (voir image fournie)

**Point de départ:** Dépôt du grossiste

**Point d'arrivée:** Centre remplisseur

**Transport:** 
- Même camion (retour)
- Transporteur: Nom du chauffeur/société

**Contenu du trajet:**
- **RETOUR**: Palettes avec bouteilles VIDES
- **RETOUR**: Palettes vides (structure physique)
- Décompte: Bouteilles de BB (bon de besoin) reçues

**Informations du bon de réception retour:**
- Numéro du BL (Bon de Livraison)
- Date
- Véhicule (immatriculation)
- Reçu de (client/grossiste)
- Pour compte (centre/société)
- Transporteur
- Libellé (type de matériel)
- Déconsignation ou matériel (références des palettes)
- Bouteilles vides ou vrac (quantité)
- Observations/Manquants
- Client (signature)
- Magasinier (signature)
- Contrôle qualité (signature)

---

## 🔄 MODIFICATIONS NÉCESSAIRES

### 1. Modèle de Données - Nouvelle Structure

#### A. Créer un nouveau modèle `Groupe`

```python
class Groupe(Base, TimestampMixin):
    """
    Groupe - Grande entité fournisseur de gaz butane
    
    Exemples: Pétroci Holding, SODIGAZ, Pétro Ivoire, Total Energies CI
    """
    __tablename__ = "groupes"
    
    id: UUID
    name: str  # Nom du groupe (ex: "Pétroci Holding")
    code: str  # Code unique (ex: "PETROCI")
    address: str
    city: str
    phone: str
    email: str
    is_active: bool
    notes: str
    
    # Relations
    grand_distributeurs: relationship("GrandDistributeur")
```

#### B. Créer un nouveau modèle `GrandDistributeur`

```python
class GrandDistributeur(Base, TimestampMixin):
    """
    Grand Distributeur - Opère pour un groupe
    
    Exemples: CEV3, TDC WEST AFRICA
    """
    __tablename__ = "grand_distributeurs"
    
    id: UUID
    name: str  # Nom (ex: "CEV3 (PETROCI)")
    code: str  # Code unique
    groupe_id: UUID  # FK → groupes.id
    address: str
    city: str
    phone: str
    email: str
    is_active: bool
    notes: str
    
    # Relations
    groupe: relationship("Groupe")
    centres_remplisseurs: relationship("CentreRemplisseur")
```

#### C. Créer un nouveau modèle `CentreRemplisseur`

```python
class CentreRemplisseur(Base, TimestampMixin):
    """
    Centre Remplisseur - Infrastructure de conditionnement et remplissage
    
    Exemples: Atelier de TDC WEST AFRICA Sarl, Centre CEV3 Abidjan
    """
    __tablename__ = "centres_remplisseurs"
    
    id: UUID
    name: str  # Nom du centre
    code: str  # Code unique
    grand_distributeur_id: UUID  # FK → grand_distributeurs.id
    address: str
    city: str
    postal_code: str
    country: str
    phone: str
    email: str
    contact_name: str  # Responsable du centre
    contact_phone: str
    is_active: bool
    latitude: float
    longitude: float
    notes: str
    
    # Relations
    grand_distributeur: relationship("GrandDistributeur")
    bons_enlevement: relationship("BonEnlevement")  # Départs
    bons_reception_retour: relationship("BonReceptionRetour")  # Retours
```

#### D. Modifier le modèle `Partner` existant

```python
class PartnerType(str, enum.Enum):
    """Types de partenaires"""
    GROSSISTE = "GROSSISTE"
    REVENDEUR = "REVENDEUR"
    TRANSPORTEUR = "TRANSPORTEUR"
    AUTRE = "AUTRE"

class Partner(Base, TimestampMixin):
    """
    Partner - Grossiste ou Revendeur
    """
    __tablename__ = "partners"
    
    id: UUID
    name: str
    type: PartnerType
    code: str  # Code client unique
    
    # Pour REVENDEUR: lien avec son grossiste
    parent_grossiste_id: UUID | None  # FK → partners.id (self-reference)
    
    # Informations complètes
    address: str
    city: str
    postal_code: str
    country: str
    phone: str
    email: str
    contact_name: str
    contact_phone: str
    is_active: bool
    notes: str
    
    # Relations
    parent_grossiste: relationship("Partner", remote_side=[id])
    revendeurs: relationship("Partner", back_populates="parent_grossiste")
    depots: relationship("Depot")  # Nouveaux dépôts
```

#### E. Créer un nouveau modèle `Depot`

```python
class Depot(Base, TimestampMixin):
    """
    Dépôt - Point de stockage d'un grossiste ou revendeur
    """
    __tablename__ = "depots"
    
    id: UUID
    name: str  # Nom du dépôt
    code: str  # Code unique
    partner_id: UUID  # FK → partners.id (grossiste ou revendeur)
    
    # Localisation
    address: str
    city: str
    postal_code: str
    latitude: float
    longitude: float
    
    # Contact sur place
    contact_name: str
    contact_phone: str
    
    is_active: bool
    is_main_depot: bool  # Dépôt principal du partner
    notes: str
    
    # Relations
    partner: relationship("Partner")
    livraisons_arrivees: relationship("LivraisonDetail")
```

#### F. Remplacer `Expedition` par `BonEnlevement`

```python
class BonEnlevementStatus(str, enum.Enum):
    """Statuts du bon d'enlèvement"""
    CREATION = "CREATION"
    VALIDE = "VALIDE"  # Validé par le centre
    EN_CHARGEMENT = "EN_CHARGEMENT"  # Chargement en cours
    EN_ROUTE = "EN_ROUTE"  # En transit
    EN_LIVRAISON = "EN_LIVRAISON"  # Livraisons en cours (multi-dépôts)
    TERMINE = "TERMINE"  # Toutes livraisons effectuées
    ANNULE = "ANNULE"

class BonEnlevement(Base, TimestampMixin):
    """
    Bon d'Enlèvement - Document ALLER (Centre → Grossiste/Revendeurs)
    
    Trajet: Centre remplisseur → Dépôt(s)
    Contenu: Palettes PLEINES (livraison) + Collecte VIDES
    """
    __tablename__ = "bons_enlevement"
    
    id: UUID
    numero_bon: str  # Numéro unique du bon (ex: "00000201/08")
    reference: str  # Référence interne
    
    # Origine
    centre_remplisseur_id: UUID  # FK → centres_remplisseurs.id
    
    # Destination principale (grossiste commanditaire)
    grossiste_id: UUID  # FK → partners.id
    depot_principal_id: UUID  # FK → depots.id (dépôt final du grossiste)
    
    # Transport
    vehicule_immatriculation: str
    chauffeur_nom: str
    chauffeur_societe: str  # Société du chauffeur
    chauffeur_phone: str
    
    # Dates
    date_creation: datetime
    date_validation: datetime  # Validation par le centre
    date_chargement: datetime  # Début chargement
    date_depart: datetime  # Départ du centre
    date_arrivee_finale: datetime  # Arrivée au dépôt principal
    
    # Statut
    status: BonEnlevementStatus
    
    # Informations supplémentaires
    observations: str
    instructions_livraison: str
    
    # Validation
    validateur_centre_id: UUID  # FK → users.id (qui a validé au centre)
    recepteur_final_id: UUID  # FK → users.id (qui a réceptionné au dépôt principal)
    
    # OTP pour sécurisation
    otp_code: str
    otp_expiry: datetime
    
    # Relations
    centre_remplisseur: relationship("CentreRemplisseur")
    grossiste: relationship("Partner")
    depot_principal: relationship("Depot")
    palettes: relationship("Palette")  # Palettes dans ce bon
    livraisons: relationship("LivraisonDetail")  # Détails des livraisons multi-dépôts
    collectes_vides: relationship("CollecteVide")  # Bouteilles vides collectées
```

#### G. Créer `LivraisonDetail` (pour livraisons multi-dépôts)

```python
class LivraisonStatus(str, enum.Enum):
    """Statut d'une livraison"""
    EN_ATTENTE = "EN_ATTENTE"
    EN_COURS = "EN_COURS"
    LIVREE = "LIVREE"
    PROBLEME = "PROBLEME"
    ANNULEE = "ANNULEE"

class LivraisonDetail(Base, TimestampMixin):
    """
    Détail de livraison - Une étape du trajet d'un bon d'enlèvement
    
    Utilisé quand le camion fait un tour de livraisons (multi-dépôts)
    """
    __tablename__ = "livraisons_details"
    
    id: UUID
    bon_enlevement_id: UUID  # FK → bons_enlevement.id
    ordre_livraison: int  # Ordre dans la tournée (1, 2, 3...)
    
    # Destination
    depot_id: UUID  # FK → depots.id
    revendeur_id: UUID  # FK → partners.id (si revendeur, sinon NULL pour grossiste)
    
    # Dates
    date_arrivee: datetime
    date_depart: datetime
    
    # Statut
    status: LivraisonStatus
    
    # Palettes livrées à ce dépôt
    # (relationMany-to-Many via table d'association)
    
    # Réception
    recepteur_nom: str
    recepteur_signature: str  # Base64 ou path
    observations: str
    problemes: str
    
    # Relations
    bon_enlevement: relationship("BonEnlevement")
    depot: relationship("Depot")
    revendeur: relationship("Partner")
    palettes_livrees: relationship("Palette", secondary="livraison_palettes")
```

#### H. Créer `CollecteVide` (collecte des bouteilles vides)

```python
class CollecteVide(Base, TimestampMixin):
    """
    Collecte Vide - Collecte de bouteilles vides lors d'une livraison
    """
    __tablename__ = "collectes_vides"
    
    id: UUID
    bon_enlevement_id: UUID  # FK → bons_enlevement.id
    livraison_detail_id: UUID | None  # FK → livraisons_details.id (si multi-dépôts)
    depot_id: UUID  # FK → depots.id (où la collecte a eu lieu)
    
    # Détails de la collecte
    type_bouteille: PaletteType  # B6, B12, B28
    quantite_bouteilles_vides: int
    quantite_palettes_vides: int  # Structures palettes vides
    
    date_collecte: datetime
    collecteur_nom: str  # Souvent le chauffeur
    observations: str
    
    # Relations
    bon_enlevement: relationship("BonEnlevement")
    livraison_detail: relationship("LivraisonDetail")
    depot: relationship("Depot")
```

#### I. Créer `BonReceptionRetour`

```python
class BonReceptionRetourStatus(str, enum.Enum):
    """Statuts du bon de réception retour"""
    CREATION = "CREATION"
    EN_ROUTE = "EN_ROUTE"
    ARRIVE = "ARRIVE"
    EN_CONTROLE = "EN_CONTROLE"
    VALIDE = "VALIDE"
    REFUSE = "REFUSE"

class BonReceptionRetour(Base, TimestampMixin):
    """
    Bon de Réception Retour - Document RETOUR (Grossiste → Centre)
    
    Trajet: Dépôt grossiste → Centre remplisseur
    Contenu: Palettes VIDES + Bouteilles vides
    """
    __tablename__ = "bons_reception_retour"
    
    id: UUID
    numero_bl: str  # Numéro du BL (ex: "BL N°75 du 13.08.25")
    numero_reception: str  # Numéro de réception (ex: "0001320/08 MB")
    
    # Origine
    grossiste_id: UUID  # FK → partners.id
    depot_depart_id: UUID  # FK → depots.id
    
    # Destination
    centre_remplisseur_id: UUID  # FK → centres_remplisseurs.id
    
    # Transport
    vehicule_immatriculation: str
    transporteur_nom: str
    transporteur_societe: str
    
    # Dates
    date_creation: datetime
    date_depart: datetime
    date_arrivee: datetime
    date_controle: datetime
    date_validation: datetime
    
    # Statut
    status: BonReceptionRetourStatus
    
    # Contenu du retour
    # (Détails via relations)
    
    # Contrôle qualité
    controleur_id: UUID  # FK → users.id
    magasinier_id: UUID  # FK → users.id
    observations: str
    manquants: str  # Palettes/bouteilles manquantes
    
    # Signatures
    client_signature: str  # Grossiste
    magasinier_signature: str
    controleur_signature: str
    
    # Relations
    grossiste: relationship("Partner")
    depot_depart: relationship("Depot")
    centre_remplisseur: relationship("CentreRemplisseur")
    palettes_retournees: relationship("Palette")
    details_retour: relationship("DetailRetour")
```

#### J. Créer `DetailRetour`

```python
class DetailRetour(Base, TimestampMixin):
    """
    Détail Retour - Détail du contenu d'un bon de réception retour
    """
    __tablename__ = "details_retour"
    
    id: UUID
    bon_reception_retour_id: UUID  # FK → bons_reception_retour.id
    
    # Type de matériel
    libelle: str  # "Palettes de BB N°", "Bouteilles 6 Kg", etc.
    type_bouteille: PaletteType | None
    
    # Quantités
    quantite_palettes: int
    quantite_bouteilles_vides: int
    quantite_vrac: int  # Bouteilles en vrac (sans palette)
    
    # Références des palettes
    references_palettes: str  # Ex: "35-53-55, 52-59-61"
    
    observations: str
    
    # Relations
    bon_reception_retour: relationship("BonReceptionRetour")
```

#### K. Modifier le modèle `Palette`

```python
class PaletteStatus(str, enum.Enum):
    """Statuts de palette"""
    CREATION = "CREATION"
    EN_STOCK_CENTRE = "EN_STOCK_CENTRE"  # En stock au centre remplisseur
    EN_CHARGEMENT = "EN_CHARGEMENT"  # En cours de chargement
    EN_ROUTE_ALLER = "EN_ROUTE_ALLER"  # En transit (aller)
    LIVREE_GROSSISTE = "LIVREE_GROSSISTE"  # Livrée au grossiste
    LIVREE_REVENDEUR = "LIVREE_REVENDEUR"  # Livrée au revendeur
    EN_STOCK_GROSSISTE = "EN_STOCK_GROSSISTE"
    EN_STOCK_REVENDEUR = "EN_STOCK_REVENDEUR"
    EN_ROUTE_RETOUR = "EN_ROUTE_RETOUR"  # En transit (retour)
    RETOURNEE_CENTRE = "RETOURNEE_CENTRE"  # Retournée au centre
    HORS_SERVICE = "HORS_SERVICE"

class Palette(Base, TimestampMixin):
    """Palette modifiée pour refléter le nouveau flux"""
    __tablename__ = "palettes"
    
    id: UUID
    serial_number: str
    reference_code: str
    rfid_tag_id: UUID
    type: PaletteType
    status: PaletteStatus
    
    # Localisation actuelle
    centre_remplisseur_actuel_id: UUID | None  # FK → centres_remplisseurs.id
    depot_actuel_id: UUID | None  # FK → depots.id
    partner_actuel_id: UUID | None  # FK → partners.id
    
    # Trajet en cours
    bon_enlevement_actuel_id: UUID | None  # FK → bons_enlevement.id
    bon_retour_actuel_id: UUID | None  # FK → bons_reception_retour.id
    
    # Historique
    # ...
    
    # Relations
    centre_remplisseur_actuel: relationship("CentreRemplisseur")
    depot_actuel: relationship("Depot")
    partner_actuel: relationship("Partner")
    bon_enlevement_actuel: relationship("BonEnlevement")
    bon_retour_actuel: relationship("BonReceptionRetour")
```

#### L. Adapter `PaletteMovement`

```python
class MovementAction(str, enum.Enum):
    """Actions possibles"""
    CREATION = "CREATION"
    CHARGEMENT_CENTRE = "CHARGEMENT_CENTRE"
    DEPART_CENTRE = "DEPART_CENTRE"
    LIVRAISON_DEPOT = "LIVRAISON_DEPOT"
    RECEPTION_DEPOT = "RECEPTION_DEPOT"
    STOCKAGE = "STOCKAGE"
    RETOUR_DEPART = "RETOUR_DEPART"
    RETOUR_ARRIVEE = "RETOUR_ARRIVEE"
    CONTROLE_QUALITE = "CONTROLE_QUALITE"
    VALIDATION_RETOUR = "VALIDATION_RETOUR"
    MISE_HORS_SERVICE = "MISE_HORS_SERVICE"

class PaletteMovement(Base):
    """Historique des mouvements de palette"""
    __tablename__ = "palette_movements"
    
    id: UUID
    palette_id: UUID
    
    # Document associé
    bon_enlevement_id: UUID | None
    bon_reception_retour_id: UUID | None
    livraison_detail_id: UUID | None
    
    # Localisation
    centre_remplisseur_id: UUID | None
    depot_id: UUID | None
    partner_id: UUID | None
    
    action: MovementAction
    status_before: str
    status_after: str
    timestamp: datetime
    user_id: UUID
    
    # Géolocalisation
    latitude: float
    longitude: float
    location_address: str
    
    details: dict  # JSON
    notes: str
```

### 2. Services à Créer/Modifier

#### A. `centre_remplisseur_service.py`
- CRUD complet pour centres remplisseurs
- Gestion des stocks par centre
- Statistiques de production

#### B. `bon_enlevement_service.py`
- Création de bon d'enlèvement
- Validation par le centre
- Assignation des palettes
- Gestion du workflow (chargement → départ → livraison → terminé)
- Gestion des livraisons multi-dépôts
- Collecte des bouteilles vides
- Génération PDF du bon

#### C. `bon_reception_retour_service.py`
- Création de bon de réception retour
- Workflow (départ → arrivée → contrôle → validation)
- Contrôle qualité
- Gestion des manquants
- Génération PDF du bon

#### D. `livraison_service.py`
- Gestion des livraisons multi-dépôts
- Ordre de passage
- Scan à chaque dépôt
- Validation par signature

#### E. Modifier `palette_service.py`
- Adapter au nouveau workflow
- Suivi de localisation (centre/dépôt/partner)
- Historique complet

### 3. Routes API à Créer/Modifier

#### A. Routes Groupes
```
GET    /api/v1/groupes
POST   /api/v1/groupes
GET    /api/v1/groupes/{id}
PUT    /api/v1/groupes/{id}
DELETE /api/v1/groupes/{id}
```

#### B. Routes Grands Distributeurs
```
GET    /api/v1/grand-distributeurs
POST   /api/v1/grand-distributeurs
GET    /api/v1/grand-distributeurs/{id}
PUT    /api/v1/grand-distributeurs/{id}
DELETE /api/v1/grand-distributeurs/{id}
GET    /api/v1/grand-distributeurs/{id}/centres-remplisseurs
```

#### C. Routes Centres Remplisseurs
```
GET    /api/v1/centres-remplisseurs
POST   /api/v1/centres-remplisseurs
GET    /api/v1/centres-remplisseurs/{id}
PUT    /api/v1/centres-remplisseurs/{id}
DELETE /api/v1/centres-remplisseurs/{id}
GET    /api/v1/centres-remplisseurs/{id}/stock
GET    /api/v1/centres-remplisseurs/{id}/bons-enlevement
```

#### D. Routes Dépôts
```
GET    /api/v1/depots
POST   /api/v1/depots
GET    /api/v1/depots/{id}
PUT    /api/v1/depots/{id}
DELETE /api/v1/depots/{id}
GET    /api/v1/depots/{id}/stock
GET    /api/v1/partners/{partner_id}/depots
```

#### E. Routes Bons d'Enlèvement
```
GET    /api/v1/bons-enlevement
POST   /api/v1/bons-enlevement
GET    /api/v1/bons-enlevement/{id}
PUT    /api/v1/bons-enlevement/{id}
DELETE /api/v1/bons-enlevement/{id}

POST   /api/v1/bons-enlevement/{id}/valider
POST   /api/v1/bons-enlevement/{id}/charger
POST   /api/v1/bons-enlevement/{id}/depart
POST   /api/v1/bons-enlevement/{id}/livraison/{livraison_id}/scanner
POST   /api/v1/bons-enlevement/{id}/livraison/{livraison_id}/valider
POST   /api/v1/bons-enlevement/{id}/terminer

GET    /api/v1/bons-enlevement/{id}/pdf
```

#### F. Routes Bons de Réception Retour
```
GET    /api/v1/bons-reception-retour
POST   /api/v1/bons-reception-retour
GET    /api/v1/bons-reception-retour/{id}
PUT    /api/v1/bons-reception-retour/{id}
DELETE /api/v1/bons-reception-retour/{id}

POST   /api/v1/bons-reception-retour/{id}/depart
POST   /api/v1/bons-reception-retour/{id}/arrivee
POST   /api/v1/bons-reception-retour/{id}/controler
POST   /api/v1/bons-reception-retour/{id}/valider

GET    /api/v1/bons-reception-retour/{id}/pdf
```

### 4. Schémas Pydantic à Créer

Pour chaque nouveau modèle, créer:
- `{Model}Base` - Champs communs
- `{Model}Create` - Création
- `{Model}Update` - Mise à jour
- `{Model}InDB` - Lecture depuis DB
- `{Model}Response` - Réponse API

Exemples:
- `schemas/groupe.py`
- `schemas/grand_distributeur.py`
- `schemas/centre_remplisseur.py`
- `schemas/depot.py`
- `schemas/bon_enlevement.py`
- `schemas/bon_reception_retour.py`
- `schemas/livraison.py`
- `schemas/collecte_vide.py`

### 5. Migrations Alembic

Créer les migrations pour:
1. Créer table `groupes`
2. Créer table `grand_distributeurs`
3. Créer table `centres_remplisseurs`
4. Créer table `depots`
5. Modifier table `partners` (ajouter `parent_grossiste_id`, modifier enum)
6. Créer table `bons_enlevement`
7. Créer table `livraisons_details`
8. Créer table `collectes_vides`
9. Créer table `bons_reception_retour`
10. Créer table `details_retour`
11. Modifier table `palettes` (nouvelles FK et statuts)
12. Modifier table `palette_movements`
13. Supprimer/archiver table `expeditions` (ou renommer pour historique)

### 6. Rôles Utilisateurs à Ajuster

```python
class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    
    # Centre remplisseur
    RESPONSABLE_CENTRE = "RESPONSABLE_CENTRE"
    OPERATEUR_CENTRE = "OPERATEUR_CENTRE"
    MAGASINIER_CENTRE = "MAGASINIER_CENTRE"
    CONTROLEUR_QUALITE = "CONTROLEUR_QUALITE"
    
    # Transport
    CHAUFFEUR = "CHAUFFEUR"
    
    # Grossiste
    RESPONSABLE_GROSSISTE = "RESPONSABLE_GROSSISTE"
    OPERATEUR_GROSSISTE = "OPERATEUR_GROSSISTE"
    
    # Revendeur
    RESPONSABLE_REVENDEUR = "RESPONSABLE_REVENDEUR"
    OPERATEUR_REVENDEUR = "OPERATEUR_REVENDEUR"
```

### 7. Permissions RBAC à Définir

Exemples:
- `RESPONSABLE_CENTRE`: Créer/valider bons d'enlèvement
- `OPERATEUR_CENTRE`: Charger palettes
- `MAGASINIER_CENTRE`: Réceptionner retours
- `CONTROLEUR_QUALITE`: Contrôler qualité retours
- `CHAUFFEUR`: Scanner palettes, valider livraisons
- `RESPONSABLE_GROSSISTE`: Créer commandes, valider réceptions
- `OPERATEUR_GROSSISTE`: Réceptionner livraisons

### 8. Features Spécifiques

#### A. Tournée de Livraison (Multi-Dépôts)
- Créer un algorithme d'optimisation de tournée
- Calculer l'ordre optimal de livraison
- Permettre la modification manuelle de l'ordre
- Gérer les échecs de livraison partielle

#### B. Collecte des Vides
- Scanner les bouteilles vides collectées
- Comptage automatique ou manuel
- Association au bon d'enlèvement

#### C. Contrôle Qualité Retours
- Checklist de contrôle
- Photos des anomalies
- Validation/refus de palettes
- Gestion des écarts

#### D. Génération de Documents
- PDF des bons d'enlèvement (format officiel)
- PDF des bons de réception retour
- Bordereaux de livraison par dépôt
- Récapitulatifs

#### E. Traçabilité GPS
- Tracking en temps réel du camion
- Historique des positions
- Alertes de déviation
- Estimation temps d'arrivée

#### F. Notifications
- Bon créé → Chauffeur
- Départ → Grossiste/Revendeurs
- Arrivée dépôt → Récepteur
- Retour arrivé → Magasinier
- Anomalie détectée → Tous

### 9. Rapports et Statistiques

#### A. Dashboards
- Centre: Sorties/Retours par période
- Grossiste: Commandes, stocks, rotations
- Revendeur: Livraisons reçues, ventes

#### B. KPIs
- Temps moyen de tournée
- Taux de remplissage camions
- Taux de retour des palettes vides
- Délai moyen entre sortie et retour
- Palettes en circulation
- Palettes perdues/manquantes

### 10. Tests à Créer

#### Tests Unitaires
- Modèles (validation, relations)
- Services (logique métier)
- Utilitaires

#### Tests d'Intégration
- Workflow complet bon d'enlèvement
- Workflow complet bon de réception retour
- Tournée multi-dépôts
- Collecte vides + retour

#### Tests E2E
- Scénario complet: Centre → Grossiste → Revendeurs → Centre

---

## 📝 PLAN D'IMPLÉMENTATION RECOMMANDÉ

### Phase 1: Restructuration des Modèles (2-3 jours)
1. Créer nouveaux modèles (Groupe, GrandDistributeur, CentreRemplisseur, Depot)
2. Modifier Partner
3. Créer BonEnlevement, LivraisonDetail, CollecteVide
4. Créer BonReceptionRetour, DetailRetour
5. Modifier Palette et PaletteMovement
6. Créer migrations Alembic

### Phase 2: Services Basiques (3-4 jours)
1. CRUD Groupes
2. CRUD Grands Distributeurs
3. CRUD Centres Remplisseurs
4. CRUD Dépôts
5. Adapter service Partners

### Phase 3: Workflow Bon d'Enlèvement (4-5 jours)
1. Service BonEnlevement
2. Workflow statuts
3. Assignation palettes
4. Livraisons multi-dépôts
5. Collecte vides

### Phase 4: Workflow Bon de Réception Retour (3-4 jours)
1. Service BonReceptionRetour
2. Workflow retour
3. Contrôle qualité
4. Gestion manquants

### Phase 5: Frontend Backoffice (5-7 jours)
1. Pages gestion hiérarchie (Groupe → Centre)
2. Page création bon d'enlèvement
3. Page suivi tournée
4. Page bon de réception retour
5. Dashboards

### Phase 6: Application Mobile Chauffeur (5-7 jours)
1. Login
2. Liste des bons assignés
3. Scanner palettes
4. Tournée guidée
5. Validation livraisons
6. Collecte vides
7. Mode offline

### Phase 7: Génération Documents (2-3 jours)
1. Template PDF bon d'enlèvement
2. Template PDF bon de réception retour
3. Bordereau de livraison

### Phase 8: Notifications et Alertes (2-3 jours)
1. Système de notifications
2. Templates emails
3. SMS (Twilio)
4. Notifications push mobile

### Phase 9: Rapports et Statistiques (3-4 jours)
1. KPIs centres
2. KPIs grossistes
3. Rapports admin
4. Exports

### Phase 10: Tests et Déploiement (3-4 jours)
1. Tests complets
2. Documentation API
3. Documentation utilisateur
4. Formation
5. Déploiement production

**DURÉE TOTALE ESTIMÉE:** 32-44 jours (6-9 semaines)

---

## ⚠️ POINTS D'ATTENTION

### 1. Migration des Données Existantes
- Mapper les anciennes `expeditions` vers `bons_enlevement`
- Vérifier l'intégrité des relations
- Prévoir un script de migration

### 2. Rétrocompatibilité
- Si le système est déjà en production, prévoir une phase de transition
- Maintenir les anciennes routes en parallèle temporairement
- Documentation de migration pour les clients de l'API

### 3. Performance
- Indexer correctement les nouvelles tables
- Optimiser les requêtes avec joins multiples
- Prévoir pagination pour listes longues
- Cache Redis pour données fréquentes

### 4. Sécurité
- RBAC strict sur les nouveaux endpoints
- Validation des droits d'accès par hiérarchie
- Audit trail complet
- Signature électronique des documents

### 5. Formation
- Guide utilisateur pour chaque rôle
- Vidéos de démonstration
- FAQ
- Support pendant transition

---

## 🎯 OBJECTIFS MESURABLES

### Avant Correction (État Actuel)
- ❌ Structure hiérarchique incorrecte
- ❌ Workflow ne correspond pas au terrain
- ❌ Pas de gestion multi-dépôts
- ❌ Pas de collecte des vides
- ❌ Pas de bons officiels
- ❌ Pas de contrôle qualité retours

### Après Correction (État Cible)
- ✅ Structure hiérarchique complète (Groupe → Centre)
- ✅ Workflow conforme aux documents terrain
- ✅ Gestion complète tournées multi-dépôts
- ✅ Collecte vides intégrée
- ✅ Génération bons officiels (PDF)
- ✅ Contrôle qualité complet
- ✅ Traçabilité totale palette
- ✅ Application mobile chauffeur
- ✅ Rapports et statistiques détaillés

---

## 📞 SUPPORT ET DOCUMENTATION

### Documentation à Créer
1. **Architecture**: Diagrammes UML, schéma DB
2. **API**: Documentation OpenAPI/Swagger complète
3. **Utilisateur**: Guides par rôle
4. **Développeur**: Guide de contribution
5. **Déploiement**: Procédures production

### Formation
1. **Administrateurs**: Configuration système
2. **Centres**: Création bons, validation
3. **Chauffeurs**: Application mobile
4. **Grossistes/Revendeurs**: Réception, commandes
5. **Support**: Troubleshooting

---

**FIN DU PROMPT DE CORRECTION**

Ce document constitue la feuille de route complète pour aligner GazTracker avec la réalité opérationnelle du terrain.

