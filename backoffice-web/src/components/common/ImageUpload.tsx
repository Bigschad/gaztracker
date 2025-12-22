import { useState, useRef, useEffect } from 'react';
import { Upload, X, Loader2 } from 'lucide-react';
import { Button } from './Button';
import { uploadService } from '../../services/api/uploadService';

interface ImageUploadProps {
  /** Current image URL (if editing existing entity) */
  currentImageUrl?: string | null;
  /** Callback when image is uploaded successfully */
  onImageUploaded: (url: string) => void;
  /** Callback when image is removed */
  onImageRemoved?: () => void;
  /** Label for the upload field */
  label?: string;
  /** Helper text */
  helperText?: string;
  /** Maximum file size in MB (default: 5) */
  maxSizeMB?: number;
  /** Allowed file types (default: all image types) */
  allowedTypes?: string[];
  /** Preview size (default: 'medium') */
  previewSize?: 'small' | 'medium' | 'large';
  /** Whether upload is disabled */
  disabled?: boolean;
  /** Custom className for container */
  className?: string;
}

const DEFAULT_ALLOWED_TYPES = [
  'image/jpeg',
  'image/jpg',
  'image/png',
  'image/gif',
  'image/svg+xml',
  'image/webp',
];

const PREVIEW_SIZES = {
  small: 'w-16 h-16',
  medium: 'w-24 h-24',
  large: 'w-32 h-32',
};

export const ImageUpload: React.FC<ImageUploadProps> = ({
  currentImageUrl,
  onImageUploaded,
  onImageRemoved,
  label = 'Image',
  helperText,
  maxSizeMB = 5,
  allowedTypes = DEFAULT_ALLOWED_TYPES,
  previewSize = 'medium',
  disabled = false,
  className = '',
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Set preview from current image URL on mount
  useEffect(() => {
    if (currentImageUrl && !selectedFile) {
      setPreview(currentImageUrl);
    }
  }, [currentImageUrl, selectedFile]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setError(null);

    // Validate file type
    if (!allowedTypes.includes(file.type)) {
      setError(
        `Format non autorisé. Types autorisés: ${allowedTypes
          .map((t) => t.split('/')[1].toUpperCase())
          .join(', ')}`
      );
      return;
    }

    // Validate file size
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      setError(`Fichier trop volumineux. Taille maximale: ${maxSizeMB}MB`);
      return;
    }

    setSelectedFile(file);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      setUploading(true);
      setError(null);

      const result = await uploadService.uploadLogo(selectedFile);
      onImageUploaded(result.url);
      
      // Clear selected file after successful upload
      setSelectedFile(null);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Erreur lors de l\'upload de l\'image'
      );
    } finally {
      setUploading(false);
    }
  };

  const handleRemove = () => {
    setSelectedFile(null);
    setPreview(null);
    setError(null);
    
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }

    if (onImageRemoved) {
      onImageRemoved();
    }
  };

  const handleBrowse = () => {
    fileInputRef.current?.click();
  };

  // Determine display image (preview of new file or current image)
  const displayImage = preview;

  return (
    <div className={`space-y-3 ${className}`}>
      {label && (
        <label className="block text-sm font-medium">{label}</label>
      )}

      <div className="flex items-start gap-4">
        {/* Preview */}
        {displayImage ? (
          <div className="relative">
            <div
              className={`${PREVIEW_SIZES[previewSize]} border rounded-lg overflow-hidden bg-gray-50 flex items-center justify-center`}
            >
              <img
                src={displayImage}
                alt="Preview"
                className="w-full h-full object-contain p-2"
                onError={() => {
                  setPreview(null);
                  setError('Impossible de charger l\'image');
                }}
              />
            </div>
            {!disabled && (
              <button
                type="button"
                onClick={handleRemove}
                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors shadow-lg"
                title="Supprimer l'image"
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </div>
        ) : (
          <div
            className={`${PREVIEW_SIZES[previewSize]} border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center bg-gray-50`}
          >
            <Upload className="w-6 h-6 text-gray-400" />
          </div>
        )}

        {/* Upload Controls */}
        <div className="flex-1 space-y-2">
          <input
            ref={fileInputRef}
            type="file"
            accept={allowedTypes.join(',')}
            onChange={handleFileSelect}
            className="hidden"
            disabled={disabled || uploading}
          />

          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={handleBrowse}
              disabled={disabled || uploading}
            >
              <Upload className="w-4 h-4 mr-2" />
              {selectedFile ? 'Changer' : 'Sélectionner'}
            </Button>

            {selectedFile && (
              <Button
                type="button"
                onClick={handleUpload}
                disabled={disabled || uploading}
              >
                {uploading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Upload...
                  </>
                ) : (
                  'Uploader'
                )}
              </Button>
            )}
          </div>

          {error && (
            <p className="text-sm text-red-600">{error}</p>
          )}

          {helperText && !error && (
            <p className="text-xs text-muted-foreground">{helperText}</p>
          )}

          {selectedFile && (
            <p className="text-xs text-muted-foreground">
              Fichier sélectionné: {selectedFile.name} (
              {(selectedFile.size / 1024).toFixed(1)} KB)
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
