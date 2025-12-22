# Processus de Bon d'Enlèvement - Documentation Complète

## Vue d'ensemble

Le **Bon d'Enlèvement** est un document de livraison qui gère le transport de palettes pleines depuis un **Centre Remplisseur** vers un ou plusieurs **Dépôts** d'un **Grossiste**. Le processus suit un workflow séquentiel avec plusieurs statuts et implique différents acteurs à chaque étape.

---

## Statuts du Workflow

Le processus suit cette séquence de statuts :

1. **CREATION** → 2. **VALIDE** → 3. **EN_CHARGEMENT** → 4. **EN_ROUTE** → 5. **EN_LIVRAISON** → 6. **TERMINE**

**Statut spécial :** **ANNULE** (peut être appliqué depuis CREATION ou VALIDE uniquement)

---

## Acteurs du Système

### Rôles Utilisateurs

1. **ADMIN** : Administrateur système avec accès complet
2. **RESPONSABLE_LOGISTIQUE** : Responsable logistique au centre remplisseur
3. **OPERATEUR_USINE** : Opérateur au centre remplisseur
4. **CHAUFFEUR** : Chauffeur/livreur

---

## Processus Détaillé par Étape

### ÉTAPE 1 : CRÉATION (CREATION)

**Description :** Création initiale du bon d'enlèvement.

**Acteurs autorisés :**
- **ADMIN**
- **RESPONSABLE_LOGISTIQUE**
- **OPERATEUR_USINE**

**Actions :**
- Création du bon avec les informations suivantes :
  - Centre remplisseur (origine)
  - Grossiste (destinataire)
  - Dépôt principal (destination finale)
  - Informations transport (véhicule, chauffeur, téléphone)
  - Date/heure de livraison prévue
  - Palettes à inclure (optionnel à la création)
  - Observations et instructions de livraison

**Données enregistrées :**
- `numero_bon` : Numéro unique généré automatiquement (format: XXXXXXXX/MM)
- `date_creation` : Date de création
- `status` : `CREATION`
- `palette_count` : Nombre de palettes (0 initialement)

**Contraintes :**
- Le bon peut être modifié uniquement en statut `CREATION`
- Les palettes peuvent être ajoutées mais ne sont pas encore assignées

**Transition possible :**
- → **VALIDE** (validation par le centre)
- → **ANNULE** (annulation)

---

### ÉTAPE 2 : VALIDATION (VALIDE)

**Description :** Le centre remplisseur valide le bon d'enlèvement.

**Acteurs autorisés :**
- **RESPONSABLE_LOGISTIQUE** (validateur principal)
- **ADMIN**

**Actions :**
- Validation du bon par un responsable logistique
- Génération automatique d'un **OTP (One-Time Password)** pour la validation finale de livraison
- Envoi de notifications aux opérateurs et chauffeurs du centre

**Données enregistrées :**
- `date_validation` : Date de validation
- `validateur_centre_id` : ID de l'utilisateur qui a validé
- `status` : `VALIDE`
- `otp_code` : Code OTP généré (6 chiffres)
- `otp_expiry` : Date d'expiration de l'OTP (24h)

**Notifications envoyées :**
- Email/SMS aux utilisateurs **OPERATEUR_USINE** et **CHAUFFEUR** associés au centre remplisseur
- Message : "Le bon d'Enlèvement {numero_bon} a été validé. Vous pouvez maintenant démarrer le chargement des palettes."

**Contraintes :**
- Le bon ne peut être validé que depuis le statut `CREATION`
- Le validateur doit être un utilisateur actif

**Transition possible :**
- → **EN_CHARGEMENT** (début du chargement)
- → **ANNULE** (annulation)

---

### ÉTAPE 3 : CHARGEMENT (EN_CHARGEMENT)

**Description :** Chargement des palettes pleines sur le véhicule.

**Acteurs autorisés :**
- **OPERATEUR_USINE** (principal)
- **CHAUFFEUR**
- **ADMIN**

**Actions :**
- Sélection et assignation des palettes au bon
- Vérification que les palettes sont disponibles et pleines
- Mise à jour du statut des palettes à `EN_CHARGEMENT`
- Enregistrement des mouvements de palettes

**Données enregistrées :**
- `date_chargement` : Date de début du chargement
- `status` : `EN_CHARGEMENT`
- `palette_count` : Nombre de palettes chargées
- Chaque palette :
  - `status` : `EN_CHARGEMENT`
  - `bon_enlevement_actuel_id` : ID du bon
  - Création d'un `PaletteMovement` avec action `CHARGEMENT_CENTRE`

**Contraintes :**
- Le bon ne peut passer en chargement que depuis le statut `VALIDE`
- Les palettes doivent être :
  - En statut `CREATION` ou `AU_CENTRE`
  - Pleines (`is_full = True`)
  - Situées au centre remplisseur du bon

**Transition possible :**
- → **EN_ROUTE** (départ du centre)

---

### ÉTAPE 4 : DÉPART / EN ROUTE (EN_ROUTE)

**Description :** Le véhicule quitte le centre remplisseur en direction des dépôts.

**Acteurs autorisés :**
- **CHAUFFEUR** (principal)
- **OPERATEUR_USINE**
- **ADMIN**

**Actions :**
- Enregistrement de la date de départ
- Mise à jour du statut de toutes les palettes à `EN_ROUTE_LIVRAISON`
- Enregistrement des mouvements de palettes

**Données enregistrées :**
- `date_depart` : Date et heure de départ
- `status` : `EN_ROUTE`
- Chaque palette :
  - `status` : `EN_ROUTE_LIVRAISON`
  - Création d'un `PaletteMovement` avec action `DEPART_CENTRE`

**Contraintes :**
- Le bon ne peut partir que depuis le statut `EN_CHARGEMENT`
- Au moins une palette doit être chargée

**Transition possible :**
- → **EN_LIVRAISON** (début des livraisons multi-dépôts)

---

### ÉTAPE 5 : LIVRAISONS (EN_LIVRAISON)

**Description :** Le véhicule effectue les livraisons aux différents dépôts.

**Acteurs autorisés :**
- **CHAUFFEUR** (principal)
- **ADMIN**

**Actions :**
- Début des livraisons multi-dépôts
- Chaque livraison peut être enregistrée individuellement via `LivraisonDetail`
- Les palettes sont livrées aux différents dépôts selon l'ordre de livraison

**Données enregistrées :**
- `status` : `EN_LIVRAISON`
- `livraison_count` : Nombre de livraisons effectuées
- Chaque `LivraisonDetail` :
  - `depot_id` : Dépôt de livraison
  - `ordre_livraison` : Ordre de la livraison
  - `status` : Statut de la livraison (EN_ATTENTE, EN_COURS, LIVREE, ANNULEE)
  - `palettes_livrees` : Nombre de palettes livrées

**Contraintes :**
- Le bon ne peut passer en livraison que depuis le statut `EN_ROUTE`

**Transition possible :**
- → **TERMINE** (réception finale au dépôt principal)

---

### ÉTAPE 6 : TERMINÉ (TERMINE)

**Description :** Réception finale au dépôt principal et clôture du bon.

**Acteurs autorisés :**
- **RESPONSABLE_LOGISTIQUE** (récepteur principal)
- **ADMIN**

**Actions :**
- Réception finale au dépôt principal
- Validation avec OTP (optionnel mais recommandé)
- Mise à jour des palettes restantes au dépôt
- Clôture du bon

**Données enregistrées :**
- `date_arrivee_finale` : Date d'arrivée au dépôt principal
- `recepteur_final_id` : ID de l'utilisateur qui a reçu
- `status` : `TERMINE`
- Chaque palette restante :
  - `status` : `AU_DEPOT`
  - `bon_enlevement_actuel_id` : `NULL` (désassignée)
  - `current_depot_id` : ID du dépôt principal
  - `current_centre_remplisseur_id` : `NULL`
  - Création d'un `PaletteMovement` avec action `ARRIVEE_DEPOT`

**Validation OTP :**
- Si un OTP est fourni, il est validé :
  - Le code doit correspondre à `otp_code`
  - Le code ne doit pas être expiré (`otp_expiry`)

**Contraintes :**
- Le bon ne peut être terminé que depuis le statut `EN_LIVRAISON`
- Le récepteur doit être un utilisateur actif

**Transition possible :**
- Aucune (statut final)

---

## ANNULATION (ANNULE)

**Description :** Annulation du bon d'enlèvement.

**Acteurs autorisés :**
- **ADMIN**
- **RESPONSABLE_LOGISTIQUE**

**Conditions :**
- Le bon ne peut être annulé que depuis les statuts :
  - `CREATION`
  - `VALIDE`

**Actions :**
- Si des palettes étaient assignées (statut `VALIDE`), elles sont :
  - Désassignées (`bon_enlevement_actuel_id = NULL`)
  - Remises au statut `AU_CENTRE`
- Le statut du bon passe à `ANNULE`
- Une raison d'annulation est enregistrée dans `observations`

**Données enregistrées :**
- `status` : `ANNULE`
- `observations` : "ANNULÉ: {raison}"

---

## Récapitulatif des Transitions

| Statut Actuel | Statut Suivant | Acteur Principal | Action Requise |
|---------------|----------------|------------------|----------------|
| CREATION | VALIDE | RESPONSABLE_LOGISTIQUE | Validation du bon |
| CREATION | ANNULE | ADMIN / RESPONSABLE_LOGISTIQUE | Annulation |
| VALIDE | EN_CHARGEMENT | OPERATEUR_USINE | Début du chargement |
| VALIDE | ANNULE | ADMIN / RESPONSABLE_LOGISTIQUE | Annulation |
| EN_CHARGEMENT | EN_ROUTE | CHAUFFEUR | Départ du centre |
| EN_ROUTE | EN_LIVRAISON | CHAUFFEUR | Début des livraisons |
| EN_LIVRAISON | TERMINE | RESPONSABLE_LOGISTIQUE | Réception finale |

---

## Données Clés du Bon d'Enlèvement

### Informations Principales
- **numero_bon** : Numéro unique (format: XXXXXXXX/MM)
- **reference** : Référence interne (optionnel)
- **status** : Statut actuel dans le workflow

### Origine et Destination
- **centre_remplisseur_id** : Centre remplisseur (origine)
- **grossiste_id** : Grossiste commanditaire
- **depot_principal_id** : Dépôt principal (destination finale)

### Transport
- **vehicule_immatriculation** : Immatriculation du véhicule
- **chauffeur_nom** : Nom du chauffeur
- **chauffeur_societe** : Société du chauffeur
- **chauffeur_phone** : Téléphone du chauffeur

### Dates
- **date_creation** : Date de création
- **date_validation** : Date de validation
- **date_chargement** : Date de début du chargement
- **date_depart** : Date de départ du centre
- **date_arrivee_finale** : Date d'arrivée au dépôt principal
- **date_heure_livraison** : Date/heure prévue de livraison

### Sécurité
- **otp_code** : Code OTP pour validation finale (6 chiffres)
- **otp_expiry** : Date d'expiration de l'OTP (24h)

### Validation et Réception
- **validateur_centre_id** : Utilisateur qui a validé le bon
- **recepteur_final_id** : Utilisateur qui a reçu au dépôt principal

### Compteurs
- **palette_count** : Nombre de palettes dans le bon
- **livraison_count** : Nombre de livraisons effectuées

### Informations Complémentaires
- **observations** : Observations générales
- **instructions_livraison** : Instructions spéciales de livraison

---

## Relations avec Autres Entités

### Palettes
- Les palettes sont assignées au bon via `bon_enlevement_actuel_id`
- Leur statut change selon l'étape du bon :
  - `AU_CENTRE` → `EN_CHARGEMENT` → `EN_ROUTE_LIVRAISON` → `AU_DEPOT`

### Livraisons (LivraisonDetail)
- Un bon peut avoir plusieurs livraisons (multi-dépôts)
- Chaque livraison a un ordre et un statut propre

### Collectes Vides (CollecteVide)
- Un bon peut inclure des collectes de bouteilles vides
- Enregistrées via `CollecteVide` lié au bon

### Mouvements de Palettes (PaletteMovement)
- Tous les changements de statut des palettes sont enregistrés
- Actions : `CHARGEMENT_CENTRE`, `DEPART_CENTRE`, `ARRIVEE_DEPOT`

---

## Notifications

### Validation (CREATION → VALIDE)
- **Destinataires** : OPERATEUR_USINE et CHAUFFEUR du centre remplisseur
- **Canal** : Email ou SMS selon disponibilité
- **Message** : Notification que le bon est validé et prêt pour chargement

---

## Contrôles et Validations

### Validation des Palettes
- Les palettes doivent être :
  - Pleines (`is_full = True`)
  - En statut `CREATION` ou `AU_CENTRE`
  - Situées au centre remplisseur du bon

### Validation OTP
- L'OTP est généré lors de la validation (statut `VALIDE`)
- Valide pendant 24 heures
- Utilisé pour la réception finale (optionnel)

### Contrôles de Transition
- Chaque transition vérifie que le statut actuel est correct
- Les transitions non autorisées génèrent une `BusinessRuleException`

---

## Points d'Attention

1. **Modification** : Un bon ne peut être modifié qu'en statut `CREATION`
2. **Annulation** : Un bon ne peut être annulé qu'en statut `CREATION` ou `VALIDE`
3. **Palettes** : Les palettes doivent être disponibles et au bon endroit avant assignation
4. **OTP** : L'OTP expire après 24h, il faut revalider le bon si nécessaire
5. **Multi-dépôts** : Un bon peut livrer à plusieurs dépôts via `LivraisonDetail`

---

## Endpoints API Principaux

- `POST /api/v1/bons-enlevement` : Créer un bon
- `GET /api/v1/bons-enlevement` : Lister les bons
- `GET /api/v1/bons-enlevement/{id}` : Obtenir un bon
- `PATCH /api/v1/bons-enlevement/{id}` : Modifier un bon (CREATION uniquement)
- `POST /api/v1/bons-enlevement/{id}/valider` : Valider un bon
- `POST /api/v1/bons-enlevement/{id}/start-chargement` : Démarrer le chargement
- `POST /api/v1/bons-enlevement/{id}/depart` : Enregistrer le départ
- `POST /api/v1/bons-enlevement/{id}/start-livraison` : Démarrer les livraisons
- `POST /api/v1/bons-enlevement/{id}/terminer` : Terminer le bon
- `POST /api/v1/bons-enlevement/{id}/annuler` : Annuler le bon

---

## Diagramme de Workflow

```
CREATION
   │
   ├─→ [VALIDATION] → VALIDE
   │      │
   │      ├─→ [CHARGEMENT] → EN_CHARGEMENT
   │      │      │
   │      │      └─→ [DÉPART] → EN_ROUTE
   │      │             │
   │      │             └─→ [LIVRAISONS] → EN_LIVRAISON
   │      │                    │
   │      │                    └─→ [RÉCEPTION FINALE] → TERMINE
   │      │
   │      └─→ [ANNULATION] → ANNULE
   │
   └─→ [ANNULATION] → ANNULE
```

---

*Document généré le 4 décembre 2025*
