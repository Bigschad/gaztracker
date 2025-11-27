# 🔧 Guide de Dépannage - Expo Go

## Problème : Impossible d'utiliser l'écran du téléphone avec Expo Go

### ✅ Solutions à vérifier dans l'ordre

## 1. Vérifier que le backend est accessible depuis le réseau local

### Démarrer le backend avec l'option `--host 0.0.0.0`

```bash
# Dans le dossier racine du projet (pas mobile-app)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

⚠️ **Important** : Utiliser `--host 0.0.0.0` permet d'accepter les connexions depuis n'importe quelle interface réseau (pas seulement localhost).

### Tester l'accessibilité depuis votre téléphone

1. Sur votre téléphone, ouvrez un navigateur
2. Allez à : `http://192.168.1.4:8000/docs` (remplacez par votre IP si différente)
3. Vous devriez voir la documentation Swagger de l'API

Si ça ne fonctionne pas, passez à l'étape 2.

## 2. Vérifier le pare-feu Windows

Le pare-feu Windows peut bloquer les connexions entrantes sur le port 8000.

### Solution automatique (recommandée)

Exécutez le script de configuration du pare-feu en tant qu'administrateur :

```bash
# Clic droit sur le fichier → Exécuter en tant qu'administrateur
scripts\configure-firewall.bat
```

### Solution manuelle

1. Ouvrez **Pare-feu Windows Defender**
2. Cliquez sur **Paramètres avancés**
3. Cliquez sur **Règles de trafic entrant** → **Nouvelle règle**
4. Choisissez **Port** → **TCP** → **Ports spécifiques** : `8000`
5. Autorisez la connexion
6. Appliquez à tous les profils (Domaine, Privé, Public)

### Vérifier que la règle est active

```bash
netsh advfirewall firewall show rule name="GazTracker Backend Port 8000"
```

### Alternative : Désactiver temporairement le pare-feu (⚠️ uniquement pour le développement)

## 3. Vérifier que le téléphone et l'ordinateur sont sur le même réseau WiFi

- ✅ Votre téléphone et votre ordinateur doivent être connectés au **même réseau WiFi**
- ❌ Ne pas utiliser le partage de connexion mobile
- ❌ Ne pas utiliser un réseau WiFi différent

## 4. Vérifier l'IP locale de votre ordinateur

Si votre IP change, mettez à jour `app.json` :

```bash
# Windows PowerShell
ipconfig | findstr /i "IPv4"

# Vous devriez voir quelque chose comme :
# Adresse IPv4. . . . . . . . . . . . . .: 192.168.1.4
```

Puis mettez à jour `app.json` :
```json
"extra": {
  "apiUrl": "http://VOTRE_IP:8000"
}
```

## 5. Redémarrer Expo après modification de app.json

Après avoir modifié `app.json`, vous devez **redémarrer Expo** :

```bash
# Arrêter Expo (Ctrl+C)
# Puis redémarrer
cd mobile-app
npm start
```

## 6. Utiliser le mode tunnel si le réseau local ne fonctionne pas ⭐ RECOMMANDÉ

Si vous avez toujours des problèmes avec le réseau local, utilisez le mode tunnel d'Expo. C'est la solution la plus simple et la plus fiable :

```bash
cd mobile-app
npx expo start --tunnel
```

**Avantages du mode tunnel :**
- ✅ Fonctionne même si le pare-feu bloque les connexions
- ✅ Fonctionne même si vous êtes sur des réseaux WiFi différents
- ✅ Pas besoin de configurer le pare-feu
- ✅ Plus simple à utiliser

**Inconvénients :**
- ⚠️ Un peu plus lent que le mode LAN
- ⚠️ Nécessite une connexion Internet

**Note** : Le mode tunnel crée une connexion sécurisée via les serveurs d'Expo, donc votre téléphone peut se connecter même si le réseau local ne fonctionne pas.

## 7. Vérifier les logs dans Expo Go

Dans Expo Go, appuyez sur `j` pour ouvrir le menu de développement et voir les erreurs.

## 8. Vérifier la console du navigateur (si vous testez sur web)

Si l'app fonctionne sur web mais pas sur téléphone, le problème est probablement lié au réseau.

## 9. Tester la connexion API directement

Dans l'application Expo Go, ouvrez la console de développement et vérifiez les erreurs réseau. Vous devriez voir des erreurs comme :
- `Network request failed`
- `Connection refused`
- `Timeout`

## 10. Vérifier que le backend répond bien

Testez depuis votre ordinateur :
```bash
curl http://192.168.1.4:8000/api/v1/health
```

Si ça fonctionne sur l'ordinateur mais pas sur le téléphone, c'est un problème de réseau/pare-feu.

## 📱 Commandes utiles

```bash
# Démarrer Expo
cd mobile-app
npm start

# Démarrer Expo en mode tunnel
npx expo start --tunnel

# Démarrer Expo et ouvrir directement sur Android
npm run android

# Voir l'IP locale (Windows)
ipconfig | findstr /i "IPv4"

# Tester l'API depuis le téléphone (ouvrir dans le navigateur)
http://192.168.1.4:8000/docs
```

## 🔍 Checklist de vérification

### Mode LAN (réseau local)
- [ ] Backend démarré avec `--host 0.0.0.0`
- [ ] Pare-feu Windows configuré pour autoriser le port 8000
- [ ] Téléphone et ordinateur sur le même WiFi
- [ ] IP locale correcte dans `app.json`
- [ ] Expo redémarré après modification de `app.json`
- [ ] Backend accessible depuis le navigateur du téléphone (`http://VOTRE_IP:8000/docs`)

### Mode Tunnel (si le mode LAN ne fonctionne pas) ⭐
- [ ] Backend démarré avec `--host 0.0.0.0`
- [ ] Expo démarré avec `npx expo start --tunnel`
- [ ] Connexion Internet active
- [ ] Scanner le QR code avec Expo Go

## 💡 Solution rapide : Utiliser le mode tunnel

Si vous avez des problèmes avec le réseau local, la solution la plus simple est d'utiliser le mode tunnel :

```bash
cd mobile-app
npx expo start --tunnel
```

Cela contourne tous les problèmes de pare-feu et de réseau local !

## 💡 Solution alternative : Utiliser un build de développement

Si Expo Go continue de poser problème, vous pouvez créer un build de développement :

```bash
cd mobile-app
npx expo run:android
```

Cela créera une version de développement installable directement sur votre téléphone.

