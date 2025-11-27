# 🔄 FLUX OPÉRATIONNEL - GazTracker

## 📊 SCHÉMA HIÉRARCHIQUE

```
┌─────────────────────────────────────────────────────────────────┐
│                           GROUPE                                 │
│         (Pétroci, SODIGAZ, Pétro Ivoire, Total)                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ├─── Grand Distributeur 1 (CEV3)
                            │    │
                            │    ├─── Centre Remplisseur A (Abidjan)
                            │    ├─── Centre Remplisseur B (San Pedro)
                            │    └─── Centre Remplisseur C (Bouaké)
                            │
                            └─── Grand Distributeur 2 (TDC WEST AFRICA)
                                 │
                                 ├─── Centre Remplisseur D (Yopougon)
                                 └─── Centre Remplisseur E (Cocody)
```

```
Centre Remplisseur
         │
         │ fournit
         ↓
    GROSSISTE (Client principal)
         │
         │ Dépôt Principal + Dépôts Secondaires
         │
         │ revend à
         ↓
    REVENDEUR 1
    ├─ Dépôt 1
    └─ Dépôt 2
    
    REVENDEUR 2
    └─ Dépôt 1
    
    REVENDEUR 3
    ├─ Dépôt 1
    ├─ Dépôt 2
    └─ Dépôt 3
```

---

## 🚚 FLUX 1 : BON D'ENLÈVEMENT (ALLER)

### Trajet: Centre Remplisseur → Dépôts → Dépôt Principal Grossiste

```
┌─────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 1 : CRÉATION BON D'ENLÈVEMENT                                │
└─────────────────────────────────────────────────────────────────────┘

[Responsable Centre Remplisseur]
    │
    │ 1. Reçoit commande du Grossiste
    │ 2. Crée Bon d'Enlèvement
    │    - Numéro bon: BE-2025-001234
    │    - Grossiste: TDC WEST AFRICA
    │    - Véhicule: AA-513-BZ-01
    │    - Chauffeur: COULIBALY Larissa
    │
    ↓
[Bon d'Enlèvement - Status: CREATION]

┌─────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 2 : VALIDATION & ASSIGNATION PALETTES                        │
└─────────────────────────────────────────────────────────────────────┘

[Responsable Centre]
    │
    │ 1. Assigne palettes au bon:
    │    - Palette B28 N°: 44-127-78, 77-121-125, 89-240-234...
    │    - Type: Palettes B28
    │    - Quantité bouteilles: #24# par palette
    │
    │ 2. Définit tournée (si multi-dépôts):
    │    - Livraison 1: Dépôt Revendeur 1 (Yopougon)
    │    - Livraison 2: Dépôt Revendeur 2 (Cocody)
    │    - Livraison 3: Dépôt Principal Grossiste (Atelier TDC)
    │
    │ 3. Valide le bon
    │
    ↓
[Bon d'Enlèvement - Status: VALIDE]
[Palettes - Status: EN_STOCK_CENTRE → EN_CHARGEMENT]

┌─────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 3 : CHARGEMENT                                                │
└─────────────────────────────────────────────────────────────────────┘

[Opérateur Centre + Chauffeur]
    │
    │ 1. Scan chaque palette RFID lors du chargement
    │ 2. Vérification automatique:
    │    ✓ Palette correspond au bon
    │    ✓ Type correct
    │    ✓ État acceptable
    │
    │ 3. Signature chauffeur
    │ 4. Signature responsable chargement
    │
    ↓
[Bon d'Enlèvement - Status: EN_CHARGEMENT]
[Palettes - Status: EN_ROUTE_ALLER]
[PaletteMovement créé: CHARGEMENT_CENTRE]

┌─────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 4 : DÉPART                                                    │
└─────────────────────────────────────────────────────────────────────┘

[Chauffeur via App Mobile]
    │
    │ 1. Clique "Démarrer la tournée"
    │ 2. GPS activé (tracking en temps réel)
    │ 3. Itinéraire affiché
    │
    ↓
[Bon d'Enlèvement - Status: EN_ROUTE]
[PaletteMovement créé: DEPART_CENTRE]
Timestamp: 19/09/2025 09:00

┌─────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 5 : LIVRAISON 1 - Dépôt Revendeur 1 (Yopougon)               │
└─────────────────────────────────────────────────────────────────────┘

[Chauffeur via App Mobile]
    │
    │ 1. Arrive au dépôt
    │ 2. Scan palettes à livrer ici:
    │    - Palette 44-127-78 ✓
    │    - Palette 77-121-125 ✓
    │
    │ 3. COLLECTE BOUTEILLES VIDES:
    │    - Type: B28
    │    - Quantité: 15 bouteilles vides
    │    - Palettes vides: 2 structures
    │
    │ 4. Signature récepteur (écran tactile)
    │ 5. Photo optionnelle
    │
    ↓
[LivraisonDetail #1 - Status: LIVREE]
[Palettes 44-127-78, 77-121-125 - Status: LIVREE_REVENDEUR]
[PaletteMovement créé: LIVRAISON_DEPOT]
[CollecteVide créée: 15 bouteilles B28 vides]
Timestamp: 19/09/2025 10:30

┌─────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 6 : LIVRAISON 2 - Dépôt Revendeur 2 (Cocody)                 │
└─────────────────────────────────────────────────────────────────────┘

[Chauffeur via App Mobile]
    │
    │ [Même processus que Livraison 1]
    │
    │ Palettes livrées:
    │    - Palette 89-240-234 ✓
    │    - Palette 50-86-81 ✓
    │
    │ Collecte vides:
    │    - 20 bouteilles B28 vides
    │    - 3 palettes vides
    │
    ↓
[LivraisonDetail #2 - Status: LIVREE]
[Palettes 89-240-234, 50-86-81 - Status: LIVREE_REVENDEUR]
[CollecteVide créée: 20 bouteilles B28 vides]
Timestamp: 19/09/2025 12:00

┌─────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 7 : LIVRAISON FINALE - Dépôt Principal Grossiste             │
└─────────────────────────────────────────────────────────────────────┘

[Chauffeur + Récepteur Grossiste]
    │
    │ 1. Arrive au dépôt principal
    │ 2. Scan palettes restantes:
    │    - Palette 122-97-91 ✓
    │    - Palette 120-75-76 ✓
    │    - Palette 73-228-74 ✓
    │    - Palette 91-70-94 ✓
    │
    │ 3. Déchargement bouteilles vides collectées
    │
    │ 4. Validation OTP grossiste (sécurité)
    │    Code OTP: 123456
    │
    │ 5. Signatures croisées
    │
    ↓
[LivraisonDetail #3 - Status: LIVREE]
[Bon d'Enlèvement - Status: TERMINE]
[Palettes restantes - Status: LIVREE_GROSSISTE → EN_STOCK_GROSSISTE]
[PaletteMovement créé: RECEPTION_DEPOT + STOCKAGE]
[Toutes les CollecteVide liées au bon]
Timestamp: 19/09/2025 14:30

┌─────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 8 : FINALISATION                                              │
└─────────────────────────────────────────────────────────────────────┘

Système génère automatiquement:
    ✓ PDF Bon d'Enlèvement signé
    ✓ Bordereaux de livraison par dépôt
    ✓ Récapitulatif collecte vides
    ✓ Notifications envoyées:
        - Centre: Livraison terminée ✓
        - Grossiste: Stock mis à jour
        - Revendeurs: Confirmations

Statistiques mises à jour:
    - Grossiste: +X palettes en stock
    - Revendeurs: +Y palettes en stock
    - Centre: -Z palettes sorties, +W vides collectées
```

---

## 🔙 FLUX 2 : BON DE RÉCEPTION RETOUR (RETOUR)

### Trajet: Dépôt Grossiste → Centre Remplisseur

```
┌─────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 1 : CRÉATION BON DE RÉCEPTION RETOUR                         │
└─────────────────────────────────────────────────────────────────────┘

[Responsable Grossiste ou Responsable Centre]
    │
    │ 1. Décide d'un retour de vides
    │ 2. Crée Bon de Réception Retour
    │    - Numéro BL: BL N°75 du 13.08.25
    │    - Numéro Réception: 0001320/08 MB
    │    - Grossiste: TDC WEST AFRICA
    │    - Véhicule: AA-807-GL-01
    │    - Transporteur: BAKAYOKO Mamfa
    │
    │ 3. Sélectionne palettes à retourner:
    │    - Palettes vides à remplir
    │    - Bouteilles vides en vrac
    │
    ↓
[Bon Réception Retour - Status: CREATION]

┌─────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 2 : CHARGEMENT AU DÉPÔT GROSSISTE                            │
└─────────────────────────────────────────────────────────────────────┘

[Opérateur Grossiste + Chauffeur]
    │
    │ 1. Prépare le chargement:
    │    - Palettes de BB N°: 35-53-55, 52-59-61, 62-63-64...
    │    - Bouteilles 12,5 Kg ord: nouvelles
    │    - Bouteilles 25 Kg ord: palettes de
    │    - Réchauds: #26#
    │
    │ 2. Scan chaque palette lors du chargement
    │ 3. Compte bouteilles vrac (si applicable)
    │
    │ 4. Signature client (grossiste)
    │
    ↓
[Bon Réception Retour - Status: EN_ROUTE]
[Palettes - Status: EN_ROUTE_RETOUR]
[PaletteMovement créé: RETOUR_DEPART]

┌─────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 3 : DÉPART                                                    │
└─────────────────────────────────────────────────────────────────────┘

[Chauffeur via App Mobile]
    │
    │ 1. Démarre trajet retour
    │ 2. GPS activé
    │
    ↓
Timestamp départ: 13/08/2025 08:00

┌─────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 4 : ARRIVÉE AU CENTRE REMPLISSEUR                             │
└─────────────────────────────────────────────────────────────────────┘

[Chauffeur + Magasinier Centre]
    │
    │ 1. Arrive au centre
    │ 2. Scan palettes à décharger
    │ 3. Déchargement
    │
    │ 4. Signature magasinier
    │
    ↓
[Bon Réception Retour - Status: ARRIVE]
[PaletteMovement créé: RETOUR_ARRIVEE]
Timestamp arrivée: 13/08/2025 10:30

┌─────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 5 : CONTRÔLE QUALITÉ                                          │
└─────────────────────────────────────────────────────────────────────┘

[Contrôleur Qualité]
    │
    │ 1. Inspecte chaque palette:
    │    - État structure ✓/✗
    │    - Bouteilles conformes ✓/✗
    │    - Quantité correcte ✓/✗
    │
    │ 2. Note anomalies:
    │    - Palette 73-79-80: Aliéner (à réparer)
    │    - Manquant: 2 bouteilles
    │
    │ 3. Photos des défauts
    │
    │ 4. Validation ou refus par palette
    │
    ↓
[Bon Réception Retour - Status: EN_CONTROLE]
[PaletteMovement créé: CONTROLE_QUALITE]

Pour chaque palette:
    - Acceptée → RETOURNEE_CENTRE
    - Refusée → HORS_SERVICE (si irréparable)
    - À réparer → RETOURNEE_CENTRE (note: réparation)

┌─────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 6 : VALIDATION FINALE                                         │
└─────────────────────────────────────────────────────────────────────┘

[Magasinier Centre]
    │
    │ 1. Examine rapport contrôle
    │ 2. Met à jour stock:
    │    - Palettes reçues: +20
    │    - Bouteilles vides: +460
    │    - Palettes à réparer: 3
    │    - Palettes HS: 1
    │
    │ 3. Valide le bon
    │ 4. Signature finale
    │
    ↓
[Bon Réception Retour - Status: VALIDE]
[Palettes acceptées - Status: EN_STOCK_CENTRE]
[PaletteMovement créé: VALIDATION_RETOUR + STOCKAGE]
Timestamp validation: 13/08/2025 15:00

┌─────────────────────────────────────────────────────────────────────┐
│  ÉTAPE 7 : FINALISATION                                              │
└─────────────────────────────────────────────────────────────────────┘

Système génère automatiquement:
    ✓ PDF Bon de Réception Retour signé
    ✓ Rapport contrôle qualité
    ✓ Récapitulatif des anomalies
    ✓ Notifications envoyées:
        - Grossiste: Retour validé, crédit compte
        - Centre: Stock mis à jour
        - Maintenance (si réparations): Liste palettes

Statistiques mises à jour:
    - Centre: +20 palettes en stock
    - Grossiste: -20 palettes, +crédit consigne
    - Palettes en circulation: -20
```

---

## 📊 EXEMPLE CONCRET COMPLET

### Scénario: Livraison 1 camion, 3 arrêts

**Contexte:**
- Groupe: Pétroci Holding
- Grand Distributeur: CEV3 (PETROCI)
- Centre Remplisseur: Atelier TDC WEST AFRICA Sarl (Yopougon)
- Grossiste: TDC WEST AFRICA Sarl
- Revendeurs du grossiste:
  - Revendeur A: Kouassi Jean (Dépôt Cocody)
  - Revendeur B: Seka Rose (Dépôt Marcory)

**Bon d'Enlèvement BE-2025-00201/08**

| Info | Valeur |
|------|--------|
| **Date création** | 19/09/2025 08:30 |
| **Centre départ** | Atelier TDC WEST AFRICA Sarl |
| **Grossiste** | TDC WEST AFRICA Sarl |
| **Véhicule** | AA-513-BZ-01 |
| **Chauffeur** | COULIBALY Larissa |
| **Type palettes** | Palettes B28 (28kg) |
| **Quantité palettes** | 7 palettes |
| **Bouteilles par palette** | 24 |
| **Total bouteilles** | 168 bouteilles pleines |

**Palettes:**
- 44-127-78
- 77-121-125
- 89-240-234
- 50-86-81
- 122-97-91
- 120-75-76
- 73-228-74

**Tournée prévue:**
1. **Arrêt 1** - Dépôt Revendeur A (Cocody)
   - Livraison: 2 palettes (44-127-78, 77-121-125)
   - Distance depuis centre: 12 km
   - ETA: 10:00

2. **Arrêt 2** - Dépôt Revendeur B (Marcory)
   - Livraison: 2 palettes (89-240-234, 50-86-81)
   - Distance depuis arrêt 1: 8 km
   - ETA: 11:30

3. **Arrêt 3** - Dépôt Principal Grossiste (Atelier TDC)
   - Livraison: 3 palettes (122-97-91, 120-75-76, 73-228-74)
   - Distance depuis arrêt 2: 15 km
   - ETA: 13:30

**Collecte vides (tout au long de la tournée):**
- Arrêt 1: 15 bouteilles B28 vides + 2 palettes vides
- Arrêt 2: 20 bouteilles B28 vides + 3 palettes vides
- Arrêt 3: 30 bouteilles B28 vides + 4 palettes vides

**Total collecte:** 65 bouteilles vides + 9 palettes vides

**Timeline réelle:**

| Heure | Action | Status | Localisation |
|-------|--------|--------|--------------|
| 08:30 | Création bon | CREATION | Centre |
| 08:45 | Validation bon | VALIDE | Centre |
| 09:00 | Début chargement | EN_CHARGEMENT | Centre |
| 09:25 | Fin chargement, départ | EN_ROUTE | Centre |
| 10:15 | Arrivée arrêt 1 | EN_LIVRAISON | Cocody |
| 10:35 | Livraison 1 OK, collecte | EN_ROUTE | Cocody |
| 11:40 | Arrivée arrêt 2 | EN_LIVRAISON | Marcory |
| 12:05 | Livraison 2 OK, collecte | EN_ROUTE | Marcory |
| 13:45 | Arrivée arrêt 3 (final) | EN_LIVRAISON | Atelier TDC |
| 14:15 | Livraison finale, validation OTP | TERMINE | Atelier TDC |

**État final palettes:**
- 44-127-78, 77-121-125: EN_STOCK_REVENDEUR (Kouassi Jean)
- 89-240-234, 50-86-81: EN_STOCK_REVENDEUR (Seka Rose)
- 122-97-91, 120-75-76, 73-228-74: EN_STOCK_GROSSISTE (TDC WEST AFRICA)

**Bouteilles vides collectées:**
- Stockées temporairement au dépôt principal du grossiste
- Feront l'objet d'un Bon de Réception Retour ultérieur

---

## 📱 INTERFACES APPLICATIVES

### Application Mobile Chauffeur

**Écran 1: Liste des bons**
```
╔═══════════════════════════════════════╗
║  Mes Bons d'Enlèvement                ║
╠═══════════════════════════════════════╣
║                                       ║
║  🚚 BE-2025-00201/08                  ║
║     Status: EN_ROUTE                  ║
║     Prochaine livraison: Cocody       ║
║     Distance: 2.3 km                  ║
║     [VOIR DÉTAILS]                    ║
║                                       ║
║  ─────────────────────────────────    ║
║                                       ║
║  📦 BE-2025-00198/08                  ║
║     Status: TERMINE                   ║
║     Terminé le: 18/09/2025            ║
║     [VOIR]                            ║
║                                       ║
╚═══════════════════════════════════════╝
```

**Écran 2: Détail tournée**
```
╔═══════════════════════════════════════╗
║  ← BE-2025-00201/08                   ║
╠═══════════════════════════════════════╣
║  Tournée: 3 livraisons                ║
║                                       ║
║  ✅ 1. Cocody (Kouassi Jean)          ║
║      2 palettes - LIVRÉ 10:35        ║
║                                       ║
║  🚚 2. Marcory (Seka Rose)            ║
║      2 palettes - EN COURS           ║
║      📍 Distance: 2.3 km              ║
║      [COMMENCER LIVRAISON]           ║
║                                       ║
║  ⏳ 3. Atelier TDC (Dépôt principal) ║
║      3 palettes                      ║
║                                       ║
║  ─────────────────────────────────    ║
║  Vides collectés: 15 bouteilles      ║
║  Palettes vides: 2                   ║
╚═══════════════════════════════════════╝
```

**Écran 3: Scanner palettes**
```
╔═══════════════════════════════════════╗
║  📷 Scanner Palettes                  ║
╠═══════════════════════════════════════╣
║                                       ║
║  Livraison: Marcory (Seka Rose)       ║
║  Palettes à livrer: 2                 ║
║                                       ║
║  ┌─────────────────────────────────┐  ║
║  │                                 │  ║
║  │     [CAMERA RFID SCANNER]       │  ║
║  │                                 │  ║
║  │      Approchez la palette       │  ║
║  │                                 │  ║
║  └─────────────────────────────────┘  ║
║                                       ║
║  Scannées:                            ║
║  ✅ 89-240-234                        ║
║  ⏳ 50-86-81 (en attente)             ║
║                                       ║
║  [ANNULER]        [VALIDER]          ║
╚═══════════════════════════════════════╝
```

**Écran 4: Collecte vides**
```
╔═══════════════════════════════════════╗
║  ♻️ Collecte Bouteilles Vides         ║
╠═══════════════════════════════════════╣
║                                       ║
║  Lieu: Marcory (Seka Rose)            ║
║                                       ║
║  Type de bouteilles:                  ║
║  ● B28 (28kg)                         ║
║  ○ B12 (12kg)                         ║
║  ○ B6 (6kg)                           ║
║                                       ║
║  Quantité bouteilles vides:           ║
║  ┌─────────────────────────┐          ║
║  │        20         [+][-]│          ║
║  └─────────────────────────┘          ║
║                                       ║
║  Palettes vides (structures):         ║
║  ┌─────────────────────────┐          ║
║  │         3         [+][-]│          ║
║  └─────────────────────────┘          ║
║                                       ║
║  Observations:                        ║
║  ┌─────────────────────────────────┐  ║
║  │ [Texte optionnel]               │  ║
║  └─────────────────────────────────┘  ║
║                                       ║
║  [ANNULER]        [ENREGISTRER]      ║
╚═══════════════════════════════════════╝
```

**Écran 5: Signature récepteur**
```
╔═══════════════════════════════════════╗
║  ✍️ Signature Récepteur                ║
╠═══════════════════════════════════════╣
║                                       ║
║  Livraison: Marcory (Seka Rose)       ║
║                                       ║
║  Palettes livrées: 2                  ║
║  Bouteilles: 48                       ║
║  Vides collectés: 20 bouteilles       ║
║                                       ║
║  Nom récepteur:                       ║
║  ┌─────────────────────────────────┐  ║
║  │ Seka Rose                       │  ║
║  └─────────────────────────────────┘  ║
║                                       ║
║  Signature:                           ║
║  ┌─────────────────────────────────┐  ║
║  │                                 │  ║
║  │   [Zone de signature tactile]   │  ║
║  │                                 │  ║
║  └─────────────────────────────────┘  ║
║         [EFFACER]                     ║
║                                       ║
║  [RETOUR]         [CONFIRMER]        ║
╚═══════════════════════════════════════╝
```

### Backoffice Web - Création Bon d'Enlèvement

```
╔════════════════════════════════════════════════════════════════════╗
║  Nouveau Bon d'Enlèvement                              [X] Fermer  ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Étape 1: Informations Générales                                  ║
║  ─────────────────────────────────────────────────────────────    ║
║                                                                    ║
║  Centre Remplisseur: [Atelier TDC WEST AFRICA ▼]                 ║
║  Grossiste:          [TDC WEST AFRICA Sarl ▼]                    ║
║  Dépôt final:        [Atelier TDC (principal) ▼]                 ║
║                                                                    ║
║  Véhicule:           [AA-513-BZ-01          ]                     ║
║  Chauffeur:          [COULIBALY Larissa     ]                     ║
║  Téléphone:          [+225 07 12 34 56 78   ]                     ║
║                                                                    ║
║  ─────────────────────────────────────────────────────────────    ║
║                                                                    ║
║  Étape 2: Sélection des Palettes                                  ║
║  ─────────────────────────────────────────────────────────────    ║
║                                                                    ║
║  Type: ● B28  ○ B12  ○ B6                                        ║
║                                                                    ║
║  Stock disponible B28: 45 palettes                                ║
║                                                                    ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ □ 44-127-78  │ B28 │ 24 btl │ Stock │ [DÉTAILS]            │ ║
║  │ □ 77-121-125 │ B28 │ 24 btl │ Stock │ [DÉTAILS]            │ ║
║  │ □ 89-240-234 │ B28 │ 24 btl │ Stock │ [DÉTAILS]            │ ║
║  │ ...                                                          │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                                                    ║
║  Sélectionnées: 7 palettes (168 bouteilles)                       ║
║                                                                    ║
║  ─────────────────────────────────────────────────────────────    ║
║                                                                    ║
║  Étape 3: Définir la Tournée (optionnel)                          ║
║  ─────────────────────────────────────────────────────────────    ║
║                                                                    ║
║  ☑ Livraisons multiples                                           ║
║                                                                    ║
║  1. [Dépôt Revendeur Kouassi Jean (Cocody) ▼]                    ║
║     Palettes: 44-127-78, 77-121-125 (2) [MODIFIER]               ║
║                                                                    ║
║  2. [Dépôt Revendeur Seka Rose (Marcory) ▼]                      ║
║     Palettes: 89-240-234, 50-86-81 (2) [MODIFIER]                ║
║                                                                    ║
║  [+ AJOUTER UN ARRÊT]                                             ║
║                                                                    ║
║  Livraison finale: Atelier TDC (3 palettes restantes)             ║
║                                                                    ║
║  ─────────────────────────────────────────────────────────────    ║
║                                                                    ║
║  Observations:                                                     ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ Palettes de B28 envoyées à l'atelier de TDC WEST AFRICA     │ ║
║  │ Sarl pour revêtement d'autre nouvelle                        │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                                                    ║
║  [ANNULER]  [ENREGISTRER BROUILLON]  [CRÉER ET VALIDER]          ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## 📈 RAPPORTS ET KPIs

### Dashboard Centre Remplisseur

```
╔════════════════════════════════════════════════════════════════════╗
║  Dashboard - Atelier TDC WEST AFRICA                    📅 Mois   ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Sorties (Bons d'Enlèvement)                                       ║
║  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────┐ ║
║  │  Palettes sorties  │  │  Bouteilles livrées│  │ Bons émis    │ ║
║  │       342          │  │      8,208          │  │     28       │ ║
║  │  📈 +15% vs mois   │  │  📈 +12% vs mois    │  │ 📊 Moy/jour  │ ║
║  └────────────────────┘  └────────────────────┘  └──────────────┘ ║
║                                                                    ║
║  Retours (Bons de Réception Retour)                                ║
║  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────┐ ║
║  │  Palettes retournées│  │  Bouteilles vides │  │ Taux retour  │ ║
║  │       298          │  │      7,152          │  │    87.1%     │ ║
║  │  📊 87% du total   │  │  ♻️ 87.1%           │  │ 🎯 Objectif  │ ║
║  └────────────────────┘  └────────────────────┘  └──────────────┘ ║
║                                                                    ║
║  Stock Actuel                                                      ║
║  ┌────────────────────────────────────────────────────────────┐   ║
║  │ B28: 125 palettes (3,000 btl) ████████░░ 80% capacité     │   ║
║  │ B12: 87 palettes  (2,175 btl) ██████░░░░ 60% capacité     │   ║
║  │ B6:  45 palettes  (1,350 btl) ████░░░░░░ 40% capacité     │   ║
║  └────────────────────────────────────────────────────────────┘   ║
║                                                                    ║
║  Palettes en Circulation (hors centre)                             ║
║  ┌────────────────────┐  ┌────────────────────┐                   ║
║  │  En transit        │  │  Chez grossistes   │                   ║
║  │       44           │  │       186          │                   ║
║  │  🚚 En livraison   │  │  📦 En stock       │                   ║
║  └────────────────────┘  └────────────────────┘                   ║
║                                                                    ║
║  Anomalies / Alertes                                               ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ ⚠️ 5 palettes non retournées >30 jours                       │ ║
║  │ 🔧 3 palettes en réparation                                  │ ║
║  │ ❌ 2 palettes hors service ce mois                           │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

### Dashboard Grossiste

```
╔════════════════════════════════════════════════════════════════════╗
║  Dashboard - TDC WEST AFRICA Sarl                       📅 Semaine ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Réceptions (Livraisons reçues)                                    ║
║  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────┐ ║
║  │  Palettes reçues   │  │  Bouteilles reçues │  │ Bons reçus   │ ║
║  │        78          │  │      1,872          │  │      6       │ ║
║  │  📦 Cette semaine  │  │  📈 +8% vs semaine  │  │ 📊 Moy/jour  │ ║
║  └────────────────────┘  └────────────────────┘  └──────────────┘ ║
║                                                                    ║
║  Stock par Dépôt                                                   ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ Dépôt Principal (Atelier TDC):                               │ ║
║  │   B28: 45 palettes (1,080 btl) ████████░░                   │ ║
║  │   B12: 32 palettes (800 btl)   ██████░░░░                   │ ║
║  │                                                              │ ║
║  │ Dépôt Secondaire (Cocody):                                   │ ║
║  │   B28: 12 palettes (288 btl)   ███░░░░░░░                   │ ║
║  │   B6:  8 palettes  (240 btl)   ██░░░░░░░░                   │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                                                    ║
║  Ventes aux Revendeurs                                             ║
║  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────┐ ║
║  │  Palettes vendues  │  │  CA cette semaine  │  │ Rotation     │ ║
║  │        64          │  │   24,500,000 FCFA  │  │   4.2 jours  │ ║
║  │  🔄 Revendeurs: 8  │  │  💰 Moy/palette    │  │ ⚡ Rapide     │ ║
║  └────────────────────┘  └────────────────────┘  └──────────────┘ ║
║                                                                    ║
║  Retours à Faire au Centre                                         ║
║  ┌────────────────────┐  ┌────────────────────┐                   ║
║  │  Bouteilles vides  │  │  Palettes à retourner│                 ║
║  │       1,248        │  │        52          │                   ║
║  │  ♻️ Prêt à retourner│  │  📅 Plannifié     │                   ║
║  └────────────────────┘  └────────────────────┘                   ║
║                                                                    ║
║  Top Revendeurs (par volume)                                       ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │ 1. Kouassi Jean (Cocody)     - 18 palettes                   │ ║
║  │ 2. Seka Rose (Marcory)       - 15 palettes                   │ ║
║  │ 3. Jules Konan (Yopougon)    - 12 palettes                   │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

---

**FIN DU DOCUMENT FLUX OPÉRATIONNEL**

