# 🚀 Tag devfast - Déploiement Rapide

## 📌 Qu'est-ce que le tag `devfast` ?

Le tag `devfast` est un **tag Git** qui déclenche automatiquement un déploiement en production sur Lightsail via GitHub Actions.

## 🎯 Pourquoi un tag plutôt qu'une branche ?

- ✅ **Immuable** : Un tag pointe vers un commit spécifique et ne change jamais
- ✅ **Simple** : Pas besoin de gérer une branche séparée
- ✅ **Rapide** : Déployez en production en quelques secondes
- ✅ **Traçable** : Gardez l'historique des déploiements
- ✅ **Réversible** : Facile de revenir en arrière

## 🔄 Workflow de déploiement

### Développement local sur `develop`

```bash
# 1. Développer normalement sur develop
git checkout develop

# 2. Faire vos modifications
# ... coder ...

# 3. Tester localement
docker-compose up -d

# 4. Commiter
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push origin develop
```

### Déploiement rapide en production avec le tag

```bash
# 1. S'assurer que tout est commité sur develop
git status

# 2. Déplacer le tag devfast vers le commit actuel
git tag -f devfast

# 3. Forcer la mise à jour du tag sur GitHub
git push -f origin devfast
```

→ **GitHub Actions déploie automatiquement sur Lightsail** 🚀

## 📋 Commandes essentielles

### Créer le tag pour la première fois

```bash
git tag -a devfast -m "Déploiement production"
git push origin devfast
```

### Déplacer le tag vers un nouveau commit

```bash
# Option 1 : Déplacer vers le commit actuel
git tag -f devfast
git push -f origin devfast

# Option 2 : Déplacer vers un commit spécifique
git tag -f devfast <commit-hash>
git push -f origin devfast
```

### Voir où pointe le tag

```bash
# Localement
git show devfast

# Sur GitHub
git ls-remote --tags origin
```

### Supprimer le tag

```bash
# Localement
git tag -d devfast

# Sur GitHub
git push --delete origin devfast
```

## 🌊 Workflow complet

### Scénario 1 : Déploiement normal

```bash
# Sur develop
git add .
git commit -m "feat: amélioration X"
git push origin develop

# Test local OK → Déployer en prod
git tag -f devfast
git push -f origin devfast
```

### Scénario 2 : Hotfix urgent

```bash
# Sur develop
git add .
git commit -m "hotfix: correction urgente"
git push origin develop

# Déployer immédiatement
git tag -f devfast
git push -f origin devfast
```

### Scénario 3 : Rollback (revenir en arrière)

```bash
# Trouver le dernier bon commit
git log --oneline

# Déplacer le tag vers ce commit
git tag -f devfast abc1234
git push -f origin devfast
```

## 🔍 Vérifier le déploiement

### Sur GitHub Actions

1. Allez sur : https://github.com/Bigschad/gaztracker/actions
2. Cherchez le workflow "Deploy to Lightsail"
3. Vérifiez que le déploiement s'est bien passé

### Sur le serveur

```bash
ssh ubuntu@VOTRE_IP

# Vérifier les containers
docker-compose ps

# Voir les logs
docker-compose logs -f app
docker-compose logs -f frontend
```

### Accès à l'application

- **Frontend** : http://VOTRE_IP:3000
- **Backend** : http://VOTRE_IP:8000/docs
- **Login** : admin@gaztracker.com / votre_mot_de_passe

## 📊 Avantages de cette approche

| Aspect | Tag devfast | Branche dev |
|--------|-------------|-------------|
| **Simplicité** | ✅ Une seule commande | ❌ Merge + Push |
| **Rapidité** | ✅ Instantané | ⚠️ Plus lent |
| **Traçabilité** | ✅ Historique clair | ⚠️ Commits mélangés |
| **Rollback** | ✅ Facile | ❌ Difficile |
| **Configuration** | ✅ Garde develop intact | ⚠️ Configs séparées |

## 🛡️ Bonnes pratiques

### ✅ À faire

- Toujours tester en local avant de déplacer le tag
- Commiter tous les changements avant de tagger
- Vérifier le déploiement sur GitHub Actions après push
- Documenter les déploiements importants

### ❌ À éviter

- Ne pas tagger sans avoir testé localement
- Ne pas déplacer le tag trop fréquemment (attendre les tests)
- Ne pas oublier de pousser le tag (`-f` pour forcer)

## 🆘 Dépannage

### Le déploiement ne se déclenche pas

```bash
# Vérifier que le tag a bien été poussé
git ls-remote --tags origin

# Forcer la mise à jour
git push -f origin devfast
```

### Le déploiement échoue

1. Allez sur GitHub Actions
2. Vérifiez les logs du workflow
3. Vérifiez les secrets GitHub (SSH_KEY, HOST, USER)
4. Connectez-vous au serveur et vérifiez manuellement

### Revenir à une version antérieure

```bash
# Trouver le commit de la dernière version stable
git log --oneline

# Déplacer le tag
git tag -f devfast <commit-hash>
git push -f origin devfast
```

## 📖 Documentation complète

Pour plus d'informations sur le déploiement Lightsail, consultez :
- `docs/GITHUB_ACTIONS_SETUP.md`
- `docs/LIGHTSAIL_QUICK_START.md`

## 💡 Résumé en 3 commandes

```bash
# 1. Développer et commiter sur develop
git commit -m "feat: nouvelle fonctionnalité"

# 2. Déplacer le tag devfast
git tag -f devfast

# 3. Déployer en production
git push -f origin devfast
```

**C'est tout !** 🎉 Le déploiement se fait automatiquement via GitHub Actions.

---

**Note** : Gardez la branche `develop` propre et stable. Le tag `devfast` devrait toujours pointer vers un commit testé et fonctionnel.

