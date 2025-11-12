import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Dialog, Button, Select } from '../common';
import { rfidTagService, paletteService } from '../../services/api';
import { RFIDTagStatus } from '../../types/rfidTag';
import { Palette } from '../../types/palette';
import { AlertCircle } from 'lucide-react';

interface AssignRFIDDialogProps {
  palette: Palette;
  isOpen: boolean;
  onClose: () => void;
}

const AssignRFIDDialog = ({ palette, isOpen, onClose }: AssignRFIDDialogProps) => {
  const [selectedTagId, setSelectedTagId] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  // Récupérer les tags RFID disponibles (non assignés)
  const { data: tagsData, isLoading: isLoadingTags } = useQuery({
    queryKey: ['rfid-tags', 'available'],
    queryFn: () => rfidTagService.list({
      status: RFIDTagStatus.NOT_ASSIGNED,
      is_active: true,
      page: 1,
      page_size: 100, // Récupérer les tags disponibles (max 100)
    }),
    enabled: isOpen,
  });

  // Mutation pour assigner le tag
  const assignMutation = useMutation({
    mutationFn: async (tagId: string) => {
      return paletteService.update(palette.id, {
        rfid_tag_id: tagId,
      });
    },
    onSuccess: () => {
      // Invalider les caches pour rafraîchir les données
      queryClient.invalidateQueries({ queryKey: ['palettes'] });
      queryClient.invalidateQueries({ queryKey: ['rfid-tags'] });
      onClose();
      setError(null);
    },
    onError: (error: any) => {
      setError(error?.response?.data?.detail || 'Erreur lors de l\'attribution du tag RFID');
    },
  });

  // Réinitialiser l'état quand le dialogue se ferme
  useEffect(() => {
    if (!isOpen) {
      setSelectedTagId('');
      setError(null);
    }
  }, [isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!selectedTagId) {
      setError('Veuillez sélectionner un tag RFID');
      return;
    }

    assignMutation.mutate(selectedTagId);
  };

  const availableTags = tagsData?.items || [];

  // Préparer les options pour le Select
  const tagOptions = [
    { value: '', label: 'Sélectionner un tag RFID...' },
    ...availableTags.map((tag) => ({
      value: tag.id,
      label: `${tag.tag_number}${tag.notes ? ` - ${tag.notes}` : ''}`,
    })),
  ];

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title={palette.rfid_tag ? 'Réassigner un tag RFID' : 'Attribuer un tag RFID'}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Information sur la palette */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium mb-2">Palette</h4>
          <div className="text-sm space-y-1 text-gray-600">
            <p><span className="font-medium">Type:</span> {String(palette.type || '')}</p>
            <p><span className="font-medium">Statut:</span> {String(palette.status || '')}</p>
            {palette.rfid_tag && (
              <p className="text-orange-600">
                <span className="font-medium">Tag actuel:</span> {String(palette.rfid_tag?.tag_number || '-')}
              </p>
            )}
          </div>
        </div>

        {/* Sélection du tag RFID */}
        <div>
          {isLoadingTags ? (
            <div className="text-sm text-gray-500">Chargement des tags disponibles...</div>
          ) : availableTags.length === 0 ? (
            <div className="text-sm text-amber-600 bg-amber-50 p-3 rounded border border-amber-200">
              <AlertCircle className="h-4 w-4 inline mr-2" />
              Aucun tag RFID disponible. Veuillez créer des tags RFID avant d'attribuer.
            </div>
          ) : (
            <Select
              label={`Tag RFID ${palette.rfid_tag ? '(nouveau)' : ''}`}
              id="rfid-tag"
              value={selectedTagId}
              onChange={(e) => setSelectedTagId(e.target.value)}
              options={tagOptions}
              required
            />
          )}
        </div>

        {/* Message d'avertissement pour la réassignation */}
        {palette.rfid_tag && (
          <div className="bg-orange-50 p-3 rounded border border-orange-200 text-sm text-orange-800">
            <AlertCircle className="h-4 w-4 inline mr-2" />
            Attention: Cette palette est déjà associée au tag <strong>{palette.rfid_tag?.tag_number || '-'}</strong>.
            Le remplacer par un nouveau tag libérera l'ancien tag.
          </div>
        )}

        {/* Message d'erreur */}
        {error && (
          <div className="bg-red-50 p-3 rounded border border-red-200 text-sm text-red-800">
            <AlertCircle className="h-4 w-4 inline mr-2" />
            {error}
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end space-x-3 pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={assignMutation.isPending}
          >
            Annuler
          </Button>
          <Button
            type="submit"
            disabled={assignMutation.isPending || !selectedTagId || availableTags.length === 0}
          >
            {assignMutation.isPending ? 'Attribution...' : palette.rfid_tag ? 'Réassigner' : 'Attribuer'}
          </Button>
        </div>
      </form>
    </Dialog>
  );
};

export default AssignRFIDDialog;
