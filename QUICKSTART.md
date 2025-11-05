# 🚀 GazTracker - Quick Start Guide

Guide de démarrage rapide pour GazTracker Phase 1

---

## ⚡ Démarrage en 5 Minutes

### Étape 1: Installer les dépendances
```bash
# Créer et activer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Étape 2: Configuration
```bash
# Copier le fichier d'environnement
cp .env.example .env

# Éditer .env (minimum requis)
# - POSTGRES_PASSWORD=votre_mot_de_passe
# - SECRET_KEY=$(openssl rand -hex 32)
```

### Étape 3: Démarrer PostgreSQL et Redis
```bash
docker-compose up -d
```

### Étape 4: Lancer l'application
```bash
uvicorn app.main:app --reload
```

### Étape 5: Tester
Ouvrez votre navigateur sur: http://localhost:8000/docs

---

## 📦 Ce qui est inclus dans Phase 1

### ✅ Infrastructure Complète
- FastAPI application configurée
- PostgreSQL + Redis avec Docker
- Structure de projet professionnelle
- Configuration centralisée

### ✅ Modèles de Données (7 modèles)
1. **User** - Utilisateurs avec RBAC
2. **Palette** - Palettes de gaz avec RFID
3. **Expedition** - Expéditions et livraisons
4. **PaletteMovement** - Historique des mouvements
5. **Notification** - Système de notifications
6. **AuditLog** - Audit trail
7. **Mixins** - Timestamps et soft delete

### ✅ Schémas Pydantic (24 schémas)
- Validation complète des entrées
- Sérialisation des réponses
- Exemples JSON intégrés

### ✅ Utilitaires
- **Security**: JWT, hashing, OTP, RFID generation
- **Exceptions**: Gestion des erreurs structurée
- **Constants**: Constantes et configurations

### ✅ Documentation
- README complet (600+ lignes)
- Documentation API (Swagger/ReDoc)
- Guide de démarrage rapide

---

## 🔌 Endpoints Disponibles

### Phase 1 (Actuels)
```
GET  /           - Informations API
GET  /health     - Health check
GET  /docs       - Documentation Swagger
GET  /redoc      - Documentation ReDoc
```

### Phases Futures
Les endpoints suivants seront implémentés dans les phases 2-5:
- `/api/v1/auth/*` - Authentification (Phase 2)
- `/api/v1/users/*` - Gestion utilisateurs (Phase 2)
- `/api/v1/palettes/*` - Gestion palettes (Phase 3)1
- `/api/v1/expeditions/*` - Gestion expéditions (Phase 4)

---

## 🛠️ Commandes Utiles

### Docker
```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Logs
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Base de Données
```bash
# Accéder à PostgreSQL
docker exec -it gaztracker_postgres psql -U gaztracker_user -d gaztracker_db

# Lister les tables (une fois les migrations appliquées)
\dt

# Quitter
\q
```

### Interface Web
```bash
# PgAdmin (gestion PostgreSQL)
http://localhost:5050
# Email: admin@gaztracker.com
# Password: admin

# Redis Commander (gestion Redis)
http://localhost:8081
```

### Tests
```bash
# Lancer les tests (Phase 2+)
pytest

# Avec coverage
pytest --cov=app
```

---

## 📂 Structure du Projet

```
gaztracker/
├── app/
│   ├── models/          # Modèles SQLAlchemy ✅
│   ├── schemas/         # Schémas Pydantic ✅
│   ├── routes/          # API routes (Phase 2+)
│   ├── services/        # Logique métier (Phase 2+)
│   ├── middleware/      # Middleware (Phase 2+)
│   ├── utils/           # Utilitaires ✅
│   ├── tests/           # Tests ✅
│   ├── main.py          # FastAPI app ✅
│   ├── config.py        # Configuration ✅
│   └── database.py      # DB managers ✅
│
├── .env.example         # Variables d'env ✅
├── requirements.txt     # Dépendances ✅
├── docker-compose.yml   # Docker setup ✅
├── README.md            # Documentation ✅
└── QUICKSTART.md        # Ce fichier ✅
```

---

## 🎯 Prochaines Étapes

### Phase 2 - Authentification
1. Implémenter le service d'authentification
2. Créer les endpoints `/auth/login`, `/auth/logout`, `/auth/refresh`
3. Ajouter le middleware JWT
4. Implémenter RBAC
5. Écrire les tests d'authentification

**Estimation**: 1-2 jours

### Phase 3 - Gestion Palettes
1. CRUD complet pour les palettes
2. Attribution RFID automatique
3. Scan de palettes
4. Historique des mouvements

**Estimation**: 2-3 jours

---

## 🔍 Vérification de l'Installation

### 1. Vérifier Python
```bash
python --version  # Devrait être 3.10+
```

### 2. Vérifier Docker
```bash
docker --version
docker-compose --version
```

### 3. Vérifier les services
```bash
docker-compose ps
# Tous les services devraient être "Up" et "healthy"
```

### 4. Tester l'API
```bash
curl http://localhost:8000/
# Devrait retourner du JSON avec name, version, etc.

curl http://localhost:8000/health
# Devrait retourner { "status": "healthy", ... }
```

---

## ❓ Résolution de Problèmes

### Erreur: Port déjà utilisé
```bash
# Trouver le processus utilisant le port
# Linux/Mac
lsof -i :8000

# Windows
netstat -ano | findstr :8000

# Changer le port dans .env
PORT=8001
```

### Erreur: Base de données non accessible
```bash
# Vérifier que PostgreSQL est démarré
docker-compose ps

# Voir les logs
docker-compose logs postgres

# Redémarrer
docker-compose restart postgres
```

### Erreur: Module introuvable
```bash
# Réinstaller les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### Erreur: Permission denied (Docker)
```bash
# Linux: Ajouter votre utilisateur au groupe docker
sudo usermod -aG docker $USER
# Puis se déconnecter et se reconnecter
```

---

## 💡 Conseils

### Développement
1. **Toujours utiliser l'environnement virtuel**
   ```bash
   source venv/bin/activate
   ```

2. **Utiliser le mode reload pour FastAPI**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Consulter la documentation Swagger**
   http://localhost:8000/docs

### Production
1. **Ne jamais commiter le fichier .env**
2. **Changer le SECRET_KEY en production**
3. **Utiliser des mots de passe forts**
4. **Activer HTTPS**
5. **Configurer les backups**

---

## 📞 Support

### Documentation
- **README.md**: Documentation complète
- **PHASE_1_SUMMARY.md**: Résumé de la phase 1
- **Swagger**: http://localhost:8000/docs

### Ressources
- **FastAPI**: https://fastapi.tiangolo.com
- **SQLAlchemy**: https://www.sqlalchemy.org
- **Pydantic**: https://docs.pydantic.dev
- **PostgreSQL**: https://www.postgresql.org/docs
- **Redis**: https://redis.io/docs

---

## ✅ Checklist de Démarrage

- [ ] Python 3.10+ installé
- [ ] Docker et Docker Compose installés
- [ ] Repository cloné
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées
- [ ] Fichier .env configuré
- [ ] PostgreSQL et Redis démarrés
- [ ] Application FastAPI lancée
- [ ] Documentation Swagger accessible
- [ ] Endpoints de base testés

---

**🎉 Félicitations ! Vous êtes prêt à développer avec GazTracker !**

Pour continuer vers la Phase 2, consultez `README.md` section "Phases de Développement".

---

**Version**: 1.0.0 - Phase 1
**Date**: 2024-01-15
