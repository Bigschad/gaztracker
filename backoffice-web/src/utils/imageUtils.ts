/**
 * Utility functions for image handling
 */

/**
 * Get the full URL for an image/logo
 * Handles both absolute URLs (external) and relative URLs (uploaded files)
 */
export const getImageUrl = (imageUrl: string | null | undefined): string | null => {
  if (!imageUrl) return null;
  
  // If it's already an absolute URL (http/https), return as is
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl;
  }
  
  // If it's a relative URL (starts with /), it will be handled by the API proxy
  // Return as is - the browser will resolve it relative to the current origin
  return imageUrl;
};

/**
 * Extract filename from a logo URL
 */
export const extractFilenameFromUrl = (url: string): string | null => {
  if (!url) return null;
  
  try {
    // Handle both absolute and relative URLs
    const urlObj = url.startsWith('http') ? new URL(url) : { pathname: url };
    const pathParts = urlObj.pathname.split('/');
    return pathParts[pathParts.length - 1] || null;
  } catch {
    // If URL parsing fails, try to extract from path
    const parts = url.split('/');
    return parts[parts.length - 1] || null;
  }
};

/**
 * Validate image file
 */
export const validateImageFile = (
  file: File,
  maxSizeMB: number = 5,
  allowedTypes: string[] = [
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/gif',
    'image/svg+xml',
    'image/webp',
  ]
): { valid: boolean; error?: string } => {
  // Check file type
  if (!allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: `Format non autorisé. Types autorisés: ${allowedTypes
        .map((t) => t.split('/')[1].toUpperCase())
        .join(', ')}`,
    };
  }

  // Check file size
  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  if (file.size > maxSizeBytes) {
    return {
      valid: false,
      error: `Fichier trop volumineux. Taille maximale: ${maxSizeMB}MB`,
    };
  }

  return { valid: true };
};

/**
 * Create a preview URL from a File object
 */
export const createImagePreview = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

/**
 * Format file size for display
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};
