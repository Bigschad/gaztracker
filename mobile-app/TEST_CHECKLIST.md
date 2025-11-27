# ✅ Checklist de Test - GazTracker Mobile

## 🔐 Authentification

### Login
- [ ] Login avec identifiants valides → Redirection Dashboard
- [ ] Login avec email invalide → Message d'erreur
- [ ] Login avec mot de passe invalide → Message d'erreur
- [ ] Champ email vide → Validation
- [ ] Champ mot de passe vide → Validation

### Session
- [ ] Fermer app → Rouvrir → Reste connecté
- [ ] Attendre 15 min → Timeout → Redirection login
- [ ] Logout → Retour login

## 📱 Dashboard

- [ ] Liste des expéditions s'affiche
- [ ] Badge de notifications (si non lues)
- [ ] Pull to refresh fonctionne
- [ ] Cliquer sur expédition → Navigation vers détails
- [ ] Filtres par statut (si implémentés)

## 🔍 Scan RFID

### Prérequis
- [ ] NFC activé sur l'appareil
- [ ] Tag RFID disponible

### Tests
- [ ] Scan tag existant → Palette trouvée
- [ ] Scan tag inexistant → Message d'erreur
- [ ] NFC désactivé → Message d'activation
- [ ] Timeout de scan (10s) → Message approprié
- [ ] Scan multiple tags → Tous détectés

## 📦 Chargement de Palettes

### Workflow
- [ ] Sélectionner expédition
- [ ] Aller sur écran Chargement
- [ ] Scanner palette 1 → Ajoutée à la liste
- [ ] Scanner palette 2 → Ajoutée à la liste
- [ ] Scanner palette déjà scannée → Message "déjà scannée"
- [ ] Scanner palette non assignée → Message d'erreur
- [ ] Confirmer chargement → Succès
- [ ] Retour Dashboard → Expédition mise à jour

### Validations
- [ ] Palette doit être assignée à l'expédition
- [ ] Pas de doublons
- [ ] Statut palette correct

## 🚚 Déchargement de Palettes

### Workflow
- [ ] Sélectionner expédition en transit
- [ ] Aller sur écran Déchargement
- [ ] Scanner palette 1 → Ajoutée
- [ ] Scanner palette 2 → Ajoutée
- [ ] Barre de progression mise à jour
- [ ] Confirmer déchargement → Succès
- [ ] Redirection vers Bon de Livraison

### Validations
- [ ] Palette doit être en transit
- [ ] Palette doit appartenir à l'expédition
- [ ] Pas de doublons

## ✍️ Signature Électronique

- [ ] Cliquer "Signer" → Canvas s'affiche
- [ ] Dessiner signature → Visible sur canvas
- [ ] Cliquer "Effacer" → Canvas vidé
- [ ] Confirmer signature → Sauvegardée
- [ ] Signature affichée sur BL

## 📄 Bon de Livraison

### Contenu
- [ ] N° BL affiché
- [ ] Date correcte
- [ ] Informations expédition
- [ ] Liste des palettes
- [ ] Totaux (palettes, bouteilles)
- [ ] Signature affichée (si signé)

### Génération PDF
- [ ] Cliquer "Générer PDF" → PDF créé
- [ ] Partager PDF → Options de partage
- [ ] PDF contient toutes les informations

## 📴 Mode Offline

### Stockage Local
- [ ] Activer mode avion
- [ ] Données restent accessibles
- [ ] Indicateur "Mode hors ligne" affiché

### Queue de Sync
- [ ] Scanner palettes en offline
- [ ] Actions mises en queue
- [ ] Désactiver mode avion
- [ ] Sync automatique démarre
- [ ] Données synchronisées

### Sync Manuelle
- [ ] Bouton sync manuel (si implémenté)
- [ ] Sync réussie → Queue vidée
- [ ] Sync échouée → Retry automatique

## 🔔 Notifications

- [ ] Notification nouvelle expédition
- [ ] Notification changement statut
- [ ] Badge de notifications
- [ ] Marquer comme lu
- [ ] Centre de notifications

## 🗄️ Base de Données SQLite

- [ ] Tables créées au démarrage
- [ ] Données sauvegardées localement
- [ ] Données récupérées après redémarrage
- [ ] Sync queue fonctionne

## 🎨 Interface Utilisateur

### Navigation
- [ ] Navigation entre écrans fluide
- [ ] Bouton retour fonctionne
- [ ] Header correct sur chaque écran

### Responsive
- [ ] Affichage correct sur petit écran
- [ ] Affichage correct sur grand écran
- [ ] Scroll fonctionne partout

### Performance
- [ ] Chargement < 2 secondes
- [ ] Pas de lag lors du scroll
- [ ] Animations fluides

## 🐛 Gestion d'Erreurs

- [ ] Erreur réseau → Message clair
- [ ] Erreur API → Message clair
- [ ] Erreur scan → Message clair
- [ ] Pas de crash de l'app

## 🔒 Sécurité

- [ ] Tokens stockés de manière sécurisée
- [ ] Refresh token automatique
- [ ] Déconnexion si token expiré
- [ ] Pas de données sensibles dans les logs

## 📊 Tests de Performance

- [ ] App démarre en < 3 secondes
- [ ] Scan RFID < 2 secondes
- [ ] Génération PDF < 5 secondes
- [ ] Pas de fuites mémoire après 30 min d'utilisation

## 📱 Tests Multi-Appareils

### Android
- [ ] Android 10
- [ ] Android 11
- [ ] Android 12+
- [ ] Différentes tailles d'écran

### Fonctionnalités Spécifiques
- [ ] NFC fonctionne
- [ ] Camera fonctionne (si utilisée)
- [ ] GPS fonctionne (si utilisé)

## ✅ Critères de Validation Finale

L'application est prête si :
- [ ] Tous les tests critiques passent (✅)
- [ ] Pas d'erreurs bloquantes
- [ ] Performance acceptable
- [ ] UX intuitive
- [ ] Mode offline fonctionne
- [ ] Documentation à jour

---

**Date de test :** _______________
**Testeur :** _______________
**Version testée :** _______________

