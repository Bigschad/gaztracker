import { useState, useRef } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Dialog, Button } from '../common';
import { rfidTagService } from '../../services/api';
import { BulkImportResult } from '../../types';
import { Upload, FileText, AlertCircle, CheckCircle, Download } from 'lucide-react';

interface BulkImportDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

export const BulkImportDialog = ({ isOpen, onClose }: BulkImportDialogProps) => {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [importResult, setImportResult] = useState<BulkImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const importMutation = useMutation({
    mutationFn: (file: File) => rfidTagService.bulkImport(file),
    onSuccess: (result) => {
      setImportResult(result);
      queryClient.invalidateQueries({ queryKey: ['rfid-tags'] });
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Erreur lors de l\'import du fichier');
    },
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.name.endsWith('.csv')) {
        setError('Veuillez sélectionner un fichier CSV');
        return;
      }
      setSelectedFile(file);
      setError(null);
      setImportResult(null);
    }
  };

  const handleImport = () => {
    if (selectedFile) {
      setError(null);
      importMutation.mutate(selectedFile);
    }
  };

  const handleDownloadTemplate = () => {
    // Create CSV template
    const csvContent = 'tag_number,notes\nRFID-2024-001,Exemple de tag\nRFID-2024-002,';
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'template_rfid_tags.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleClose = () => {
    setSelectedFile(null);
    setImportResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    onClose();
  };

  return (
    <Dialog isOpen={isOpen} onClose={handleClose} title="Import en masse de tags RFID" size="lg">
      <div className="space-y-6">
        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-2">Instructions</h4>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>Le fichier doit être au format CSV</li>
            <li>Les colonnes requises : <code className="bg-blue-100 px-1 rounded">tag_number</code></li>
            <li>Colonne optionnelle : <code className="bg-blue-100 px-1 rounded">notes</code></li>
            <li>La première ligne doit contenir les en-têtes</li>
          </ul>
          <Button
            variant="outline"
            size="sm"
            onClick={handleDownloadTemplate}
            className="mt-3"
          >
            <Download className="h-4 w-4 mr-2" />
            Télécharger le modèle CSV
          </Button>
        </div>

        {/* File upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Fichier CSV
          </label>
          <div className="flex items-center space-x-3">
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-md file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100
                cursor-pointer"
            />
          </div>
          {selectedFile && (
            <div className="mt-2 flex items-center text-sm text-gray-600">
              <FileText className="h-4 w-4 mr-2" />
              {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
            </div>
          )}
        </div>

        {/* Error message */}
        {error && (
          <div className="flex items-start space-x-2 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg">
            <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Import result */}
        {importResult && (
          <div className="space-y-3">
            <div className="flex items-start space-x-2 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg">
              <CheckCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
              <div className="text-sm">
                <p className="font-semibold">Import terminé</p>
                <p>
                  {importResult.success} tag(s) importé(s) avec succès
                  {importResult.failed > 0 && `, ${importResult.failed} échec(s)`}
                </p>
              </div>
            </div>

            {/* Errors details */}
            {importResult.errors && importResult.errors.length > 0 && (
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                <h5 className="font-semibold text-orange-900 mb-2">
                  Erreurs rencontrées ({importResult.errors.length})
                </h5>
                <div className="max-h-48 overflow-y-auto space-y-2">
                  {importResult.errors.map((err, index) => (
                    <div key={index} className="text-sm text-orange-800 bg-orange-100 p-2 rounded">
                      <span className="font-medium">Ligne {err.row}:</span> {err.tag_number} - {err.error}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end space-x-3 pt-4 border-t">
          <Button variant="outline" onClick={handleClose}>
            {importResult ? 'Fermer' : 'Annuler'}
          </Button>
          {!importResult && (
            <Button
              onClick={handleImport}
              disabled={!selectedFile || importMutation.isPending}
            >
              {importMutation.isPending ? (
                <>
                  <Upload className="h-4 w-4 mr-2 animate-pulse" />
                  Import en cours...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-2" />
                  Importer
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </Dialog>
  );
};
