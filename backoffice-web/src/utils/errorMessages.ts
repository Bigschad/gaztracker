/**
 * Error message formatting utilities
 * Converts backend error responses to user-friendly French messages
 */

interface ErrorDetail {
  resource_type?: string;
  field?: string;
  value?: string;
  resource_id?: string;
  [key: string]: any;
}

interface BackendError {
  error?: string;
  message?: string;
  details?: ErrorDetail;
}

// Mapping of resource types to French names
const RESOURCE_NAMES: Record<string, { singular: string; plural: string; gender: 'm' | 'f' }> = {
  Partner: { singular: 'Le partenaire', plural: 'Les partenaires', gender: 'm' },
  CentreRemplisseur: { singular: 'Le centre remplisseur', plural: 'Les centres remplisseurs', gender: 'm' },
  Depot: { singular: 'Le dépôt', plural: 'Les dépôts', gender: 'm' },
  Groupe: { singular: 'Le groupe', plural: 'Les groupes', gender: 'm' },
  GrandDistributeur: { singular: 'Le grand distributeur', plural: 'Les grands distributeurs', gender: 'm' },
  BonEnlevement: { singular: 'Le bon d\'enlèvement', plural: 'Les bons d\'enlèvement', gender: 'm' },
  BonReceptionRetour: { singular: 'Le bon de réception retour', plural: 'Les bons de réception retour', gender: 'm' },
  Palette: { singular: 'La palette', plural: 'Les palettes', gender: 'f' },
  User: { singular: 'L\'utilisateur', plural: 'Les utilisateurs', gender: 'm' },
};

// Mapping of field names to French labels
const FIELD_LABELS: Record<string, string> = {
  code: 'code',
  email: 'email',
  name: 'nom',
  phone: 'téléphone',
  address: 'adresse',
  city: 'ville',
  postal_code: 'code postal',
  partner_id: 'partenaire',
  groupe_id: 'groupe',
  centre_remplisseur_id: 'centre remplisseur',
  depot_id: 'dépôt',
};

/**
 * Get the French name for a resource type
 */
function getResourceName(resourceType: string, plural = false): string {
  const resource = RESOURCE_NAMES[resourceType];
  if (!resource) return resourceType;
  return plural ? resource.plural : resource.singular;
}

/**
 * Get the French label for a field
 */
function getFieldLabel(field: string): string {
  return FIELD_LABELS[field] || field;
}

/**
 * Format a RESOURCE_ALREADY_EXISTS error
 */
function formatDuplicateError(details?: ErrorDetail): string {
  if (!details) return 'Cette ressource existe déjà.';

  const resourceName = getResourceName(details.resource_type || '', false);
  const field = getFieldLabel(details.field || '');
  const value = details.value || '';

  return `${resourceName} avec ${field} "${value}" existe déjà.`;
}

/**
 * Format a RESOURCE_NOT_FOUND error
 */
function formatNotFoundError(details?: ErrorDetail, message?: string): string {
  if (!details) return 'Ressource non trouvée.';

  const resourceName = getResourceName(details.resource_type || '', false);
  
  // Check if it's a validation error (wrong type)
  if (message && message.includes('must be of type')) {
    return message;
  }

  if (details.resource_id) {
    return `${resourceName} introuvable.`;
  }

  return `${resourceName} non trouvé.`;
}

/**
 * Format a VALIDATION_ERROR
 */
function formatValidationError(details?: ErrorDetail, message?: string): string {
  if (message) return message;
  
  if (details?.field) {
    const field = getFieldLabel(details.field);
    return `Erreur de validation pour le champ "${field}".`;
  }

  return 'Erreur de validation des données.';
}

/**
 * Format an AUTHENTICATION_ERROR
 */
function formatAuthError(message?: string): string {
  if (message) return message;
  return 'Erreur d\'authentification. Veuillez vous reconnecter.';
}

/**
 * Format an AUTHORIZATION_ERROR
 */
function formatAuthorizationError(message?: string): string {
  if (message) return message;
  return 'Vous n\'avez pas les permissions nécessaires pour effectuer cette action.';
}

/**
 * Main function to format backend errors into user-friendly messages
 */
export function formatErrorMessage(error: any): string {
  // Handle axios error structure
  const backendError: BackendError = error?.response?.data || error?.data || error || {};
  
  const errorCode = backendError.error;
  const message = backendError.message;
  const details = backendError.details;

  // Handle different error codes
  switch (errorCode) {
    case 'RESOURCE_ALREADY_EXISTS':
      return formatDuplicateError(details);

    case 'RESOURCE_NOT_FOUND':
      return formatNotFoundError(details, message);

    case 'VALIDATION_ERROR':
      return formatValidationError(details, message);

    case 'AUTHENTICATION_ERROR':
      return formatAuthError(message);

    case 'AUTHORIZATION_ERROR':
      return formatAuthorizationError(message);

    case 'DATABASE_ERROR':
      return 'Erreur de base de données. Veuillez réessayer.';

    case 'EXTERNAL_SERVICE_ERROR':
      return 'Erreur de service externe. Veuillez réessayer plus tard.';

    case 'INTERNAL_ERROR':
      return 'Erreur interne du serveur. Veuillez réessayer.';

    default:
      // Fallback to the original message if available
      if (message) return message;
      if (error?.message) return error.message;
      return 'Une erreur est survenue. Veuillez réessayer.';
  }
}

/**
 * Extract error details for display
 */
export function getErrorDetails(error: any): {
  title: string;
  message: string;
  field?: string;
  value?: string;
} {
  const backendError: BackendError = error?.response?.data || error?.data || error || {};
  const errorCode = backendError.error;
  const details = backendError.details;

  let title = 'Erreur';

  switch (errorCode) {
    case 'RESOURCE_ALREADY_EXISTS':
      title = 'Doublon détecté';
      break;
    case 'RESOURCE_NOT_FOUND':
      title = 'Ressource introuvable';
      break;
    case 'VALIDATION_ERROR':
      title = 'Erreur de validation';
      break;
    case 'AUTHENTICATION_ERROR':
      title = 'Erreur d\'authentification';
      break;
    case 'AUTHORIZATION_ERROR':
      title = 'Accès refusé';
      break;
    default:
      title = 'Erreur';
  }

  return {
    title,
    message: formatErrorMessage(error),
    field: details?.field,
    value: details?.value,
  };
}
