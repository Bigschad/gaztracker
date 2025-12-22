# 🚀 GazTracker - Présentation du Système

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture du Système](#architecture-du-système)
3. [Modules Principaux](#modules-principaux)
4. [Workflows Clés](#workflows-clés)
5. [Rôles et Permissions](#rôles-et-permissions)
6. [Technologies Utilisées](#technologies-utilisées)
7. [Points Forts](#points-forts)

---

## 🎯 Vue d'Ensemble

**GazTracker** est un système complet de gestion et de traçabilité des palettes de gaz pour la chaîne logistique. Le système permet de suivre en temps réel le cycle de vie des palettes depuis leur remplissage jusqu'à leur retour, en passant par les livraisons et les collectes.

### Objectifs Principaux
- ✅ Traçabilité complète des palettes (RFID)
- ✅ Gestion des bons d'enlèvement et de retour
- ✅ Suivi des expéditions et livraisons
- ✅ Optimisation de la chaîne logistique
- ✅ Reporting et analytics
- ✅ Notifications automatiques

---

## 🏗️ Architecture du Système

### 1. Backend API (FastAPI - Python)
- **Framework** : FastAPI avec Python 3.11+
- **Base de données** : PostgreSQL avec SQLAlchemy ORM
- **Authentification** : JWT (JSON Web Tokens) avec refresh tokens
- **Cache** : Redis pour les tokens et sessions
- **API REST** : Endpoints structurés par modules
- **Audit** : Journalisation complète des actions utilisateurs

### 2. Frontend Web (React + TypeScript)
- **Framework** : React 18 avec TypeScript
- **State Management** : React Query (TanStack Query) + Zustand
- **UI** : Tailwind CSS avec composants réutilisables
- **Routing** : React Router v6
- **Cartographie** : Leaflet/React-Leaflet pour la visualisation des dépôts
- **Formulaires** : React Hook Form avec validation Zod

### 3. Application Mobile (React Native)
- **Framework** : React Native avec Expo
- **State Management** : Redux Toolkit + Redux Persist
- **Navigation** : React Navigation
- **Stockage Offline** : SQLite avec synchronisation automatique
- **RFID** : NFC Manager pour le scan des tags
- **Signature** : Signature électronique pour les bons de livraison
- **PDF** : Génération de documents PDF

---

## 📦 Modules Principaux

### 1. 🏢 Gestion Organisationnelle

#### Groupes
- Création et gestion des groupes (entreprises mères)
- Gestion des logos et informations
- Hiérarchie : Groupe → Grand Distributeur → Centre Remplisseur → Dépôt

#### Centres Remplisseurs
- Gestion des centres de remplissage
- Informations de contact et localisation
- Association aux groupes
- Gestion des logos

#### Dépôts
- Gestion des dépôts (destinations de livraison)
- Association aux partenaires (grossistes)
- Localisation géographique (coordonnées GPS)
- Visualisation sur carte interactive

#### Partenaires
- Gestion des partenaires (grossistes, transporteurs)
- Types : GROSSISTE, TRANSPORTEUR
- Informations complètes (contact, adresse, etc.)
- Gestion des logos

#### Contacts
- Gestion des contacts associés aux partenaires
- Informations de contact détaillées
- Rôles et responsabilités

---

### 2. 📦 Gestion des Palettes

#### Palettes
- **Types** : 45kg, 12kg, 6kg
- **Statuts** : 
  - CREATION, AU_CENTRE, EN_CHARGEMENT
  - EN_ROUTE_LIVRAISON, EN_ROUTE_RETOUR
  - AU_DEPOT, EN_COLLECTE
- **Traçabilité** : Suivi complet du cycle de vie
- **Assignation** : Association aux bons d'enlèvement
- **Mouvements** : Historique complet des déplacements

#### Tags RFID
- Gestion des tags RFID
- Statuts : NOT_ASSIGNED, ASSIGNED, LOST, DAMAGED
- Association aux palettes
- Scan NFC via application mobile
- Statistiques et suivi

---

### 3. 🚚 Workflow Bons d'Enlèvement

#### Processus Complet
1. **CREATION** → Création du bon
2. **VALIDE** → Validation par le centre
3. **EN_CHARGEMENT** → Chargement des palettes
4. **EN_ROUTE** → Départ du centre
5. **EN_LIVRAISON** → Livraisons aux dépôts
6. **TERMINE** → Réception finale

#### Fonctionnalités
- Création avec sélection de palettes
- Validation avec génération d'OTP
- Chargement des palettes
- Suivi en temps réel
- Multi-dépôts (plusieurs livraisons par bon)
- Collecte de bouteilles vides
- Validation OTP pour réception finale

#### Acteurs
- **ADMIN** : Accès complet
- **RESPONSABLE_LOGISTIQUE** : Validation et réception
- **OPERATEUR_USINE** : Chargement
- **CHAUFFEUR** : Transport et livraison

---

### 4. 🔄 Workflow Bons de Réception Retour

#### Processus
1. **CREATION** → Création du bon de retour
2. **VALIDE** → Validation
3. **REFUSE** → Refus si problème
4. **EN_ROUTE** → En transit vers le centre
5. **TERMINE** → Réception au centre

#### Fonctionnalités
- Gestion des retours de palettes vides
- Détails de retour par palette
- Types : RETOUR_NORMAL, RETOUR_AVARIE, RETOUR_MANQUANT
- États : EN_ATTENTE, VALIDE, REFUSE
- Suivi complet du processus

---

### 5. 👥 Gestion des Utilisateurs

#### Rôles
- **ADMIN** : Administrateur système (accès complet)
- **RESPONSABLE_LOGISTIQUE** : Responsable logistique au centre
- **OPERATEUR_USINE** : Opérateur au centre remplisseur
- **CHAUFFEUR** : Chauffeur/livreur

#### Fonctionnalités
- Création et gestion des utilisateurs
- Attribution de rôles et permissions
- Association aux entités (centre, groupe, etc.)
- Réinitialisation de mot de passe par admin
- Gestion des comptes (actif/inactif, vérifié/non vérifié)

---

### 6. 📊 Reporting et Analytics

#### Tableau de Bord
- Statistiques globales (palettes, expéditions, notifications)
- Taux d'utilisation des palettes
- Alertes (expéditions en retard, validations en attente)
- Carte interactive des dépôts avec compteurs de palettes
- Vue d'ensemble en temps réel

#### Rapports Disponibles
- Statistiques des palettes (distribution, utilisation, tendances)
- Statistiques des expéditions (performance, destinations)
- Rapports de performance utilisateurs
- Export de données (Excel, CSV)
- Rapports personnalisables

---

### 7. 🔔 Système de Notifications

#### Types de Notifications
- **VALIDATION_REQUISE** : Demande de validation
- **LIVRAISON_EN_ATTENTE** : Livraison en attente
- **ALERTE_DELAI** : Alerte de délai
- **ALERTE_VALIDATION** : Alerte de validation
- **SYSTEME** : Notifications système

#### Canaux
- **Email** : Notifications par email
- **SMS** : Notifications par SMS
- **In-App** : Notifications dans l'application

#### Fonctionnalités
- Envoi automatique selon les événements
- Gestion des retries en cas d'échec
- Statistiques de livraison
- Centre de notifications dans l'interface

---

### 8. 🗺️ Cartographie

#### Carte Interactive
- Visualisation des dépôts sur carte (Leaflet/OpenStreetMap)
- Centrage sur Abidjan
- Marqueurs personnalisés avec compteurs de palettes
- Légende et informations détaillées
- Intégration dans le tableau de bord

---

### 9. 📱 Application Mobile

#### Fonctionnalités Principales
- **Authentification** : Login avec JWT
- **Scan RFID** : Scan NFC des tags RFID
- **Chargement** : Enregistrement du chargement de palettes
- **Déchargement** : Enregistrement du déchargement
- **Bons de Livraison** : Visualisation et signature électronique
- **Mode Offline** : Fonctionnement hors ligne avec synchronisation
- **Génération PDF** : Export des bons de livraison

#### Stockage Offline
- SQLite pour le stockage local
- Synchronisation automatique avec le serveur
- Queue de synchronisation avec retry
- Indicateur de mode offline

---

### 10. 🔐 Sécurité et Audit

#### Authentification
- JWT avec refresh tokens
- Expiration automatique des sessions
- Blacklist des tokens déconnectés
- Stockage sécurisé (SecureStore sur mobile)

#### Audit
- Journalisation complète des actions
- Traçabilité des modifications
- Logs des authentifications
- Historique des mouvements de palettes

#### Permissions
- Contrôle d'accès basé sur les rôles (RBAC)
- Permissions granulaires par module
- Protection des routes API
- Validation côté serveur

---

## 🔄 Workflows Clés

### Workflow Bon d'Enlèvement

```
CREATION → VALIDE → EN_CHARGEMENT → EN_ROUTE → EN_LIVRAISON → TERMINE
   │         │
   └─────────┴→ ANNULE
```

**Acteurs :**
- Création : ADMIN, RESPONSABLE_LOGISTIQUE, OPERATEUR_USINE
- Validation : RESPONSABLE_LOGISTIQUE, ADMIN
- Chargement : OPERATEUR_USINE, CHAUFFEUR, ADMIN
- Transport : CHAUFFEUR, ADMIN
- Réception : RESPONSABLE_LOGISTIQUE, ADMIN

### Workflow Palette

```
CREATION → AU_CENTRE → EN_CHARGEMENT → EN_ROUTE_LIVRAISON → AU_DEPOT
                                                              ↓
                                                    EN_ROUTE_RETOUR → AU_CENTRE
```

### Workflow Bon de Retour

```
CREATION → VALIDE/REFUSE → EN_ROUTE → TERMINE
```

---

## 👤 Rôles et Permissions

### ADMIN
- ✅ Accès complet à toutes les fonctionnalités
- ✅ Gestion des utilisateurs
- ✅ Configuration système
- ✅ Tous les workflows

### RESPONSABLE_LOGISTIQUE
- ✅ Validation des bons d'enlèvement
- ✅ Réception finale des livraisons
- ✅ Gestion des palettes
- ✅ Consultation des rapports
- ✅ Gestion de son centre remplisseur

### OPERATEUR_USINE
- ✅ Chargement des palettes
- ✅ Création de bons d'enlèvement
- ✅ Scan RFID
- ✅ Consultation des informations

### CHAUFFEUR
- ✅ Départ du centre
- ✅ Livraisons
- ✅ Scan RFID
- ✅ Consultation des missions

---

## 🛠️ Technologies Utilisées

### Backend
- **Python 3.11+**
- **FastAPI** : Framework web moderne et performant
- **SQLAlchemy** : ORM pour PostgreSQL
- **PostgreSQL** : Base de données relationnelle
- **Redis** : Cache et gestion des sessions
- **Pydantic** : Validation des données
- **Alembic** : Migrations de base de données

### Frontend Web
- **React 18** : Bibliothèque UI
- **TypeScript** : Typage statique
- **Tailwind CSS** : Framework CSS utilitaire
- **React Query** : Gestion des données serveur
- **Zustand** : State management léger
- **React Router** : Navigation
- **React Hook Form** : Gestion des formulaires
- **Zod** : Validation des schémas
- **Leaflet** : Cartographie interactive

### Mobile
- **React Native** : Framework mobile
- **Expo** : Outils et services
- **Redux Toolkit** : State management
- **React Navigation** : Navigation
- **SQLite** : Base de données locale
- **NFC Manager** : Scan RFID
- **Expo SecureStore** : Stockage sécurisé

### Infrastructure
- **Docker** : Containerisation
- **Docker Compose** : Orchestration
- **Nginx** : Reverse proxy (si déployé)

---

## ✨ Points Forts

### 1. Traçabilité Complète
- Suivi en temps réel de chaque palette
- Historique complet des mouvements
- Traçabilité RFID avec scan NFC

### 2. Workflow Automatisé
- Transitions de statut contrôlées
- Notifications automatiques
- Validation OTP pour sécurité

### 3. Multi-Plateformes
- Interface web complète
- Application mobile native
- API REST pour intégrations

### 4. Mode Offline
- Application mobile fonctionnelle hors ligne
- Synchronisation automatique
- Queue de synchronisation robuste

### 5. Sécurité Renforcée
- Authentification JWT
- Contrôle d'accès basé sur les rôles
- Audit complet des actions
- Validation OTP pour livraisons

### 6. Reporting Avancé
- Tableau de bord interactif
- Rapports personnalisables
- Export de données
- Analytics en temps réel

### 7. Interface Moderne
- Design responsive
- Cartographie interactive
- Expérience utilisateur optimisée
- Composants réutilisables

### 8. Scalabilité
- Architecture modulaire
- API RESTful
- Base de données optimisée
- Cache Redis pour performance

---

## 📈 Statistiques et Métriques

### Données Suivies
- Nombre total de palettes
- Taux d'utilisation des palettes
- Expéditions en cours
- Notifications envoyées
- Expéditions en retard
- Validations en attente

### Visualisations
- Carte interactive des dépôts
- Graphiques de tendances
- Distribution des palettes
- Performance des utilisateurs

---

## 🎯 Cas d'Usage Principaux

### 1. Création et Validation d'un Bon d'Enlèvement
1. Un responsable logistique crée un bon d'enlèvement
2. Sélection du centre, grossiste, dépôt et palettes
3. Validation du bon (génération OTP)
4. Notification aux opérateurs et chauffeurs

### 2. Chargement et Transport
1. Opérateur charge les palettes (scan RFID)
2. Chauffeur enregistre le départ
3. Suivi en temps réel du transport
4. Livraisons aux différents dépôts

### 3. Réception et Validation
1. Réception au dépôt principal
2. Validation avec OTP
3. Mise à jour du statut des palettes
4. Clôture du bon d'enlèvement

### 4. Retour des Palettes Vides
1. Création d'un bon de retour
2. Validation et enregistrement
3. Transport vers le centre
4. Réception et traitement

---

## 🔮 Fonctionnalités Futures (Roadmap)

### Court Terme
- [ ] Notifications push sur mobile
- [ ] Géolocalisation en temps réel
- [ ] QR Code en complément du RFID
- [ ] Amélioration des rapports

### Moyen Terme
- [ ] Application web PWA
- [ ] Intégration avec systèmes externes
- [ ] API GraphQL
- [ ] Machine Learning pour prédictions

### Long Terme
- [ ] IoT pour suivi automatique
- [ ] Blockchain pour traçabilité immuable
- [ ] Analytics avancés avec IA
- [ ] Multi-tenant pour plusieurs organisations

---

## 📞 Support et Documentation

### Documentation Disponible
- Documentation API (Swagger/OpenAPI)
- Guide utilisateur
- Documentation technique
- Processus détaillés (bons d'enlèvement, retours)

### Support
- Système de notifications intégré
- Logs d'audit pour débogage
- Gestion des erreurs centralisée

---

## 🏆 Avantages Concurrentiels

1. **Traçabilité RFID** : Suivi précis avec technologie NFC
2. **Workflow Automatisé** : Processus optimisés et contrôlés
3. **Multi-Plateformes** : Web + Mobile pour couverture complète
4. **Mode Offline** : Fonctionnement même sans connexion
5. **Sécurité** : Authentification robuste et audit complet
6. **Reporting** : Analytics en temps réel
7. **Scalabilité** : Architecture prête pour la croissance
8. **Interface Moderne** : Expérience utilisateur optimale

---

*Document de présentation - GazTracker v1.0*  
*Dernière mise à jour : Décembre 2025*
