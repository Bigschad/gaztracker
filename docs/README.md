# 🚀 GazTracker - Système de Gestion et Suivi des Palettes de Bouteilles de Gaz

**Version:** 1.0.0 (Phase 1 - Initialisation + Modèles de Données)
**Stack:** FastAPI + PostgreSQL + Redis + JWT + RBAC

## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Technologies](#technologies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Démarrage](#démarrage)
- [Structure du Projet](#structure-du-projet)
- [API Documentation](#api-documentation)
- [Tests](#tests)
- [Phases de Développement](#phases-de-développement)
- [Contribution](#contribution)

---

## 📖 Vue d'ensemble

GazTracker est un système complet de gestion et de traçabilité des palettes de bouteilles de gaz. Il assure le suivi complet depuis la sortie d'usine jusqu'au retour, en passant par le grossiste.

### Acteurs du Système

- **Opérateur Usine**: Création et gestion des palettes
- **Responsable Logistique Usine**: Validation des expéditions
- **Chauffeur/Livreur**: Scan et livraison des palettes
- **Grossiste**: Réception et validation OTP
- **Administrateur**: Gestion complète du système

### Types de Palettes

- **B6**: Bouteilles de 6kg
- **B12**: Bouteilles de 12kg
- **B28**: Bouteilles de 28kg

---

## ✨ Fonctionnalités

### Phase 1 (Actuelle) ✅
- ✅ Architecture complète du backend
- ✅ Modèles de données SQLAlchemy
- ✅ Schémas de validation Pydantic
- ✅ Configuration et gestion des environnements
- ✅ Structure prête pour les phases suivantes

### Phase 2 (Prochaine)
- 🔜 Authentification JWT complète
- 🔜 Gestion des utilisateurs et rôles (RBAC)
- 🔜 Middleware d'authentification

### Phase 3
- 🔜 CRUD complet pour les palettes
- 🔜 Attribution automatique des tags RFID
- 🔜 Scan de palettes

### Phase 4
- 🔜 Gestion des expéditions
- 🔜 Suivi des livraisons
- 🔜 Système OTP pour validation

### Phase 5
- 🔜 Notifications Email/SMS
- 🔜 Alertes automatiques
- 🔜 Rapports et statistiques

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Phase Future)                 │
│                   (React/Vue + Mobile App)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (API REST)                │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │    Auth     │  │   Palettes   │  │  Expéditions │       │
│  │   Service   │  │   Service    │  │   Service    │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Middleware (Auth, RBAC, Audit)              │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────┐
        │                                       │
        ▼                                       ▼
┌───────────────┐                     ┌────────────────┐
│  PostgreSQL   │                     │     Redis      │
│   (Données)   │                     │    (Cache)     │
└───────────────┘                     └────────────────┘
```

---

## 🛠️ Technologies

### Backend
- **FastAPI** (0.115.5): Framework web moderne et rapide
- **Python** (3.10+): Langage de programmation
- **Uvicorn**: Serveur ASGI haute performance

### Base de Données
- **PostgreSQL** (16): Base de données relationnelle
- **SQLAlchemy** (2.0.36): ORM Python
- **Alembic** (1.14.0): Migrations de base de données

### Cache & Sessions
- **Redis** (7): Cache en mémoire et gestion des sessions

### Sécurité & Auth
- **JWT** (python-jose): Tokens d'authentification
- **Bcrypt** (passlib): Hachage des mots de passe
- **RBAC**: Contrôle d'accès basé sur les rôles

### Validation
- **Pydantic** (2.10.3): Validation des données
- **Email-validator**: Validation des emails

### Tests
- **Pytest** (8.3.4): Framework de tests
- **Pytest-asyncio**: Tests asynchrones
- **HTTPX**: Client HTTP pour les tests

### Notifications (Phase 5)
- **Twilio**: SMS
- **SMTP**: Emails

---

## 💻 Installation

### Prérequis

- Python 3.10 ou supérieur
- Docker & Docker Compose (pour PostgreSQL et Redis)
- Git

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone <repository-url>
cd gaztracker
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Copier le fichier d'environnement**
```bash
cp .env.example .env
```

5. **Éditer le fichier .env**
Ouvrez `.env` et configurez vos variables d'environnement:
- Mots de passe de base de données
- Clé secrète JWT (générer avec `openssl rand -hex 32`)
- Configurations SMTP/Twilio (Phase 5)

---

## ⚙️ Configuration

### Variables d'environnement essentielles

```env
# Application
APP_NAME=GazTracker
APP_ENVIRONMENT=development
DEBUG=True

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=gaztracker_db
POSTGRES_USER=gaztracker_user
POSTGRES_PASSWORD=your_secure_password_here

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
SECRET_KEY=your_super_secret_key_min_32_chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080
```

Voir `.env.example` pour la configuration complète.

---

## 🚀 Démarrage

### 1. Démarrer PostgreSQL et Redis avec Docker

```bash
docker-compose up -d
```

Cela démarre:
- PostgreSQL sur le port 5432
- Redis sur le port 6379
- PgAdmin sur le port 5050 (optionnel)
- Redis Commander sur le port 8081 (optionnel)

### 2. Vérifier que les services sont démarrés

```bash
docker-compose ps
```

### 3. Créer les tables de base de données (Phase 1)

```bash
# Option 1: Utiliser Alembic (recommandé pour la production)
alembic upgrade head

# Option 2: Créer les tables directement (dev/test uniquement)
python -c "from app.database import db_manager; import asyncio; asyncio.run(db_manager.init_db()); asyncio.run(db_manager.create_tables())"
```

### 4. Lancer le serveur FastAPI

```bash
# Mode développement avec rechargement automatique
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ou utiliser le script principal
python -m app.main
```

### 5. Accéder à l'application

- **API**: http://localhost:8000
- **Documentation Swagger**: http://localhost:8000/docs
- **Documentation ReDoc**: http://localhost:8000/redoc
- **PgAdmin**: http://localhost:5050 (admin@gaztracker.com / admin)
- **Redis Commander**: http://localhost:8081

---

## 📁 Structure du Projet

```
gaztracker/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Point d'entrée FastAPI
│   ├── config.py                  # Configuration
│   ├── database.py                # PostgreSQL + Redis
│   │
│   ├── models/                    # Modèles SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py               # Utilisateurs + RBAC
│   │   ├── palette.py            # Palettes
│   │   ├── expedition.py         # Expéditions
│   │   ├── palette_movement.py   # Historique
│   │   ├── notification.py       # Notifications
│   │   ├── audit.py              # Audit trail
│   │   └── mixins.py             # Mixins communs
│   │
│   ├── schemas/                   # Schémas Pydantic
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── palette.py
│   │   └── expedition.py
│   │
│   ├── routes/                    # Routes API (Phase 2+)
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── palettes.py
│   │   ├── expeditions.py
│   │   ├── users.py
│   │   └── health.py
│   │
│   ├── services/                  # Logique métier (Phase 2+)
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── palette_service.py
│   │   ├── expedition_service.py
│   │   └── notification_service.py
│   │
│   ├── middleware/                # Middleware (Phase 2+)
│   │   ├── __init__.py
│   │   ├── auth_middleware.py
│   │   ├── rbac.py
│   │   └── audit_middleware.py
│   │
│   ├── utils/                     # Utilitaires
│   │   ├── __init__.py
│   │   ├── security.py           # JWT, hashing, OTP
│   │   ├── exceptions.py         # Exceptions personnalisées
│   │   └── constants.py          # Constantes
│   │
│   └── tests/                     # Tests
│       ├── __init__.py
│       ├── conftest.py
│       └── test_auth.py
│
├── .env.example                   # Variables d'environnement
├── requirements.txt               # Dépendances Python
├── docker-compose.yml             # PostgreSQL + Redis
├── README.md                      # Ce fichier
└── alembic/                       # Migrations (à créer)
    ├── env.py
    └── versions/
```

---

## 📚 API Documentation

### Endpoints disponibles (Phase 1)

#### Health Check
- `GET /` - Information sur l'API
- `GET /health` - Status de santé

### Endpoints à venir (Phases 2-5)

#### Authentication (Phase 2)
- `POST /api/v1/auth/login` - Connexion
- `POST /api/v1/auth/logout` - Déconnexion
- `POST /api/v1/auth/refresh` - Rafraîchir le token
- `GET /api/v1/auth/me` - Profil utilisateur

#### Users (Phase 2)
- `GET /api/v1/users` - Liste des utilisateurs
- `POST /api/v1/users` - Créer un utilisateur
- `GET /api/v1/users/{id}` - Détails d'un utilisateur
- `PUT /api/v1/users/{id}` - Modifier un utilisateur
- `DELETE /api/v1/users/{id}` - Supprimer un utilisateur

#### Palettes (Phase 3)
- `GET /api/v1/palettes` - Liste des palettes
- `POST /api/v1/palettes` - Créer une palette
- `GET /api/v1/palettes/{id}` - Détails d'une palette
- `PUT /api/v1/palettes/{id}` - Modifier une palette
- `POST /api/v1/palettes/scan` - Scanner une palette
- `GET /api/v1/palettes/statistics` - Statistiques

#### Expéditions (Phase 4)
- `GET /api/v1/expeditions` - Liste des expéditions
- `POST /api/v1/expeditions` - Créer une expédition
- `GET /api/v1/expeditions/{id}` - Détails d'une expédition
- `PUT /api/v1/expeditions/{id}` - Modifier une expédition
- `POST /api/v1/expeditions/{id}/depart` - Marquer comme partie
- `POST /api/v1/expeditions/{id}/validate` - Valider avec OTP

---

## 🧪 Tests

### Exécuter les tests

```bash
# Tous les tests
pytest

# Avec coverage
pytest --cov=app --cov-report=html

# Tests spécifiques
pytest app/tests/test_auth.py

# Mode verbose
pytest -v
```

### Tests à implémenter (Phases 2+)

- Tests d'authentification
- Tests CRUD palettes
- Tests CRUD expéditions
- Tests de validation OTP
- Tests de notifications
- Tests d'intégration

---

## 📅 Phases de Développement

### ✅ Phase 1 - Initialisation + Modèles (Actuelle)
- Structure complète du projet
- Modèles de données
- Configuration
- Docker setup

### 🔜 Phase 2 - Authentification JWT
- Service JWT complet
- Endpoints auth (/login, /refresh, /logout)
- Middleware d'authentification
- RBAC
- Tests d'authentification

### 🔜 Phase 3 - CRUD Palettes
- Endpoints palettes
- Attribution RFID automatique
- Historique palettes
- Scan RFID
- Validation conformité

### 🔜 Phase 4 - Suivi Livraisons
- CRUD Expéditions
- Liaison palettes ↔ expéditions
- Gestion statuts workflow
- OTP pour validation
- Clôture expédition

### 🔜 Phase 5 - Notifications & Alertes
- Service notifications (SMS/Email)
- Alertes automatiques (retards, anomalies)
- Gestion OTP grossiste
- Templates de notifications

### 🔜 Phase 6 - Rapports
- Endpoints statistiques
- Rapports de performance
- Classement distribution
- Tableaux de bord

---

## 🔧 Commandes Utiles

### Docker

```bash
# Démarrer les services
docker-compose up -d

# Arrêter les services
docker-compose down

# Voir les logs
docker-compose logs -f

# Redémarrer un service
docker-compose restart postgres
```

### Base de données

```bash
# Accéder à PostgreSQL
docker exec -it gaztracker_postgres psql -U gaztracker_user -d gaztracker_db

# Créer une migration Alembic
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head

# Revenir en arrière
alembic downgrade -1
```

### Développement

```bash
# Formater le code
black app/

# Vérifier le style
flake8 app/

# Type checking
mypy app/

# Trier les imports
isort app/
```

---

## 🤝 Contribution

### Workflow de contribution

1. Créer une branche pour votre fonctionnalité
2. Implémenter les changements
3. Écrire des tests
4. Vérifier que tous les tests passent
5. Créer une Pull Request

### Standards de code

- Suivre PEP 8
- Docstrings Google style
- Type hints obligatoires
- Tests pour toute nouvelle fonctionnalité
- Coverage minimum 80%

---

## 📝 Notes

### Sécurité

- **NE JAMAIS** commiter le fichier `.env`
- Utiliser des mots de passe forts en production
- Changer la clé secrète JWT en production
- Activer HTTPS en production
- Configurer un firewall pour PostgreSQL/Redis

### Production

- Utiliser Gunicorn avec Uvicorn workers
- Configurer Nginx comme reverse proxy
- Activer les logs structurés
- Configurer des backups automatiques
- Monitorer avec Prometheus/Grafana

### Support

Pour toute question ou problème:
- Créer une issue sur GitHub
- Contacter l'équipe de développement

---

## 📄 Licence

Ce projet est propriétaire. Tous droits réservés.

---

## 👥 Équipe

- **Lead Developer**: Schad YEYE
- **Backend Developer**: Schad YEYE
- **DevOps**: Schad YEYE

---

**Version**: 1.0.0 - Phase 1
**Dernière mise à jour**: 2025-11-05
