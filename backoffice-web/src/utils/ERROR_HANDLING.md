# Système de Gestion des Erreurs

Ce document explique comment fonctionne le système de gestion des erreurs dans l'application.

## Architecture

Le système se compose de trois parties principales :

### 1. Backend - Exceptions Structurées

Le backend renvoie des erreurs au format JSON structuré :

```json
{
  "error": "RESOURCE_ALREADY_EXISTS",
  "message": "CentreRemplisseur with code='CR-2025-00001' already exists",
  "details": {
    "resource_type": "CentreRemplisseur",
    "field": "code",
    "value": "CR-2025-00001"
  }
}
```

**Codes d'erreur disponibles :**
- `RESOURCE_ALREADY_EXISTS` : Ressource existe déjà (HTTP 409)
- `RESOURCE_NOT_FOUND` : Ressource non trouvée (HTTP 404)
- `VALIDATION_ERROR` : Erreur de validation (HTTP 422)
- `AUTHENTICATION_ERROR` : Erreur d'authentification (HTTP 401)
- `AUTHORIZATION_ERROR` : Accès refusé (HTTP 403)
- `DATABASE_ERROR` : Erreur de base de données (HTTP 500)
- `EXTERNAL_SERVICE_ERROR` : Erreur de service externe (HTTP 503)
- `INTERNAL_ERROR` : Erreur interne (HTTP 500)

### 2. Frontend - Formattage des Messages

**Fichier :** `utils/errorMessages.ts`

Ce module convertit les erreurs backend en messages français conviviaux :

```typescript
import { formatErrorMessage, getErrorDetails } from '../../utils/errorMessages';

// Obtenir un message formaté
const message = formatErrorMessage(error);
// "Le centre remplisseur avec code "CR-2025-00001" existe déjà."

// Obtenir les détails complets
const details = getErrorDetails(error);
// {
//   title: "Doublon détecté",
//   message: "Le centre remplisseur avec code "CR-2025-00001" existe déjà.",
//   field: "code",
//   value: "CR-2025-00001"
// }
```

### 3. Frontend - Affichage des Toasts

**Composant :** `components/common/Toast.tsx`
**Hook :** `hooks/useToast.tsx`

Le hook `useToast` permet d'afficher des notifications élégantes :

```typescript
import { useToast } from '../../hooks/useToast';

const { showToast, ToastContainer } = useToast();

// Afficher un toast de succès
showToast({
  type: 'success',
  title: 'Succès',
  message: 'Centre remplisseur créé avec succès',
  duration: 3000,
});

// Afficher un toast d'erreur
showToast({
  type: 'error',
  title: 'Erreur',
  message: errorMessage,
  duration: 7000,
});

// Dans le JSX
return (
  <div>
    <ToastContainer />
    {/* Votre contenu */}
  </div>
);
```

## Utilisation dans les Pages

### Exemple Complet

```typescript
import { useMutation } from '@tanstack/react-query';
import { useToast } from '../../hooks/useToast';
import { getErrorDetails } from '../../utils/errorMessages';

const MyPage = () => {
  const { showToast, ToastContainer } = useToast();

  const createMutation = useMutation({
    mutationFn: (data) => myService.create(data),
    onSuccess: (data) => {
      showToast({
        type: 'success',
        title: 'Succès',
        message: 'Élément créé avec succès',
        duration: 3000,
      });
      // Navigation après un court délai
      setTimeout(() => {
        navigate(`/items/${data.id}`);
      }, 500);
    },
    onError: (error) => {
      const errorDetails = getErrorDetails(error);
      showToast({
        type: 'error',
        title: errorDetails.title,
        message: errorDetails.message,
        duration: 7000,
      });
    },
  });

  return (
    <div>
      <ToastContainer />
      {/* Votre formulaire */}
    </div>
  );
};
```

## Types de Toast

- **success** : Notification de succès (vert)
- **error** : Notification d'erreur (rouge)
- **warning** : Avertissement (jaune)
- **info** : Information (bleu)

## Personnalisation

### Ajouter un Nouveau Type de Ressource

Dans `utils/errorMessages.ts`, ajoutez une entrée dans `RESOURCE_NAMES` :

```typescript
const RESOURCE_NAMES: Record<string, { singular: string; plural: string; gender: 'm' | 'f' }> = {
  // ...
  MyResource: { singular: 'Ma ressource', plural: 'Mes ressources', gender: 'f' },
};
```

### Ajouter un Nouveau Champ

Dans `utils/errorMessages.ts`, ajoutez une entrée dans `FIELD_LABELS` :

```typescript
const FIELD_LABELS: Record<string, string> = {
  // ...
  my_field: 'mon champ',
};
```

## Bonnes Pratiques

1. **Toujours utiliser `getErrorDetails`** pour extraire les informations d'erreur
2. **Durée des toasts :**
   - Succès : 3000ms (3 secondes)
   - Erreur : 7000ms (7 secondes)
3. **Navigation après succès :** Attendre 500ms avant de naviguer pour que l'utilisateur voie le message
4. **Toujours inclure `ToastContainer`** dans le composant qui utilise `useToast`

## Pages Déjà Implémentées

- ✅ `CreateCentreRemplisseurPage`
- ✅ `CreateDepotPage`
- ✅ `CreateGroupePage`

## TODO

- [ ] Implémenter dans toutes les pages Create*Page
- [ ] Implémenter dans toutes les pages Edit*Page
- [ ] Implémenter dans les pages de liste pour les actions de suppression
