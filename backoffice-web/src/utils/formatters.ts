import { format, formatDistance, parseISO } from 'date-fns';
import { fr } from 'date-fns/locale';

/**
 * Format a date string to a readable format
 */
export const formatDate = (dateString: string | undefined): string => {
  if (!dateString) return '-';
  try {
    return format(parseISO(dateString), 'dd/MM/yyyy HH:mm', { locale: fr });
  } catch {
    return dateString;
  }
};

/**
 * Format a date to short format (without time)
 */
export const formatDateShort = (dateString: string | undefined): string => {
  if (!dateString) return '-';
  try {
    return format(parseISO(dateString), 'dd/MM/yyyy', { locale: fr });
  } catch {
    return dateString;
  }
};

/**
 * Format relative time (e.g., "il y a 2 heures")
 */
export const formatRelativeTime = (dateString: string | undefined): string => {
  if (!dateString) return '-';
  try {
    return formatDistance(parseISO(dateString), new Date(), {
      addSuffix: true,
      locale: fr,
    });
  } catch {
    return dateString;
  }
};

/**
 * Format number with thousands separator
 */
export const formatNumber = (value: number | undefined): string => {
  if (value === undefined || value === null) return '-';
  return new Intl.NumberFormat('fr-FR').format(value);
};

/**
 * Format percentage
 */
export const formatPercentage = (value: number | undefined): string => {
  if (value === undefined || value === null) return '-';
  return `${value.toFixed(1)}%`;
};

/**
 * Format status for display
 */
export const formatStatus = (status: string): string => {
  return status.replace(/_/g, ' ').toLowerCase();
};

/**
 * Get status color class
 */
export const getStatusColor = (status: string): string => {
  const statusUpper = status.toUpperCase();

  const colorMap: Record<string, string> = {
    // Palette statuses
    CREATED: 'text-blue-600 bg-blue-100',
    IN_STOCK: 'text-green-600 bg-green-100',
    ASSIGNED: 'text-yellow-600 bg-yellow-100',
    IN_TRANSIT: 'text-purple-600 bg-purple-100',
    DELIVERED: 'text-green-600 bg-green-100',
    RETURNED: 'text-gray-600 bg-gray-100',
    MAINTENANCE: 'text-orange-600 bg-orange-100',
    LOST: 'text-red-600 bg-red-100',

    // Expedition statuses
    VALIDATED: 'text-blue-600 bg-blue-100',
    IN_PREPARATION: 'text-yellow-600 bg-yellow-100',
    READY: 'text-green-600 bg-green-100',
    DEPARTED: 'text-purple-600 bg-purple-100',
    COMPLETED: 'text-green-600 bg-green-100',

    // Notification statuses
    PENDING: 'text-yellow-600 bg-yellow-100',
    SENT: 'text-green-600 bg-green-100',
    FAILED: 'text-red-600 bg-red-100',
    RETRYING: 'text-orange-600 bg-orange-100',
  };

  return colorMap[statusUpper] || 'text-gray-600 bg-gray-100';
};

/**
 * Download file from blob
 */
export const downloadFile = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};
