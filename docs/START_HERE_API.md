# 🚀 DÉMARRER L'API EN 30 SECONDES

## ⚡ 3 COMMANDES

```bash
# 1. Base de données (si pas déjà fait)
alembic upgrade head && python scripts/seed_test_data.py

# 2. Démarrer API
uvicorn app.main:app --reload

# 3. Ouvrir navigateur
start http://localhost:8000/docs
```

## ✅ C'EST TOUT !

Vous avez maintenant :
- ✅ API en cours d'exécution sur http://localhost:8000
- ✅ Interface Swagger interactive sur http://localhost:8000/docs
- ✅ 37 endpoints prêts à tester
- ✅ Données de test (3 groupes, 3 centres, 3 grossistes, etc.)

## 🧪 PREMIER TEST

1. Dans Swagger, cliquer sur **"Groupes"**
2. Cliquer sur **"GET /api/v1/groupes"**
3. Cliquer sur **"Try it out"**
4. Cliquer sur **"Execute"**

**Résultat** : Liste de 3 groupes (Pétroci, SODIGAZ, Pétro Ivoire)

## 📖 POUR ALLER PLUS LOIN

- **Guide complet** : `POSTMAN_GUIDE.md`
- **Vue d'ensemble** : `RECAP_PHASE_API.md`
- **Checklist** : `API_READY_CHECKLIST.md`

---

**C'est aussi simple que ça ! 🎉**

