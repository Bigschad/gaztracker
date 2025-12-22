import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { paletteService, bonEnlevementService } from '../../services/api';
import { Dialog, Button } from '../common';
import { Palette, PaletteStatus } from '../../types';
import { BonEnlevementChargement } from '../../types/bonEnlevement';

interface StartChargementDialogProps {
  bonId: string;
  centreRemplisseurId: string;
  isOpen: boolean;
  onClose: () => void;
}

const StartChargementDialog = ({ bonId, centreRemplisseurId, isOpen, onClose }: StartChargementDialogProps) => {
  const [selectedPaletteIds, setSelectedPaletteIds] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  // Fetch available palettes at the centre remplisseur
  const { data: palettesData, isLoading: isLoadingPalettes } = useQuery({
    queryKey: ['palettes', 'available-for-chargement', centreRemplisseurId],
    queryFn: async () => {
      // Fetch palettes at the centre with status CREATION or AU_CENTRE
      const allPalettes: Palette[] = [];
      let page = 1;
      let hasMore = true;
      const maxPages = 10; // Limit to prevent infinite loops

      while (hasMore && page <= maxPages) {
        const response = await paletteService.list({
          page,
          page_size: 100,
        });

        if (response.items && response.items.length > 0) {
          allPalettes.push(...response.items);
          page++;
          hasMore = response.items.length === 100 && page <= (response.total_pages || maxPages);
        } else {
          hasMore = false;
        }
      }

      // Filter palettes:
      // - At the centre remplisseur
      // - Status CREATION or AU_CENTRE
      // - Not already assigned to another bon
      return allPalettes.filter((palette) => {
        const isAtCentre = palette.current_centre_remplisseur_id === centreRemplisseurId;
        const isAvailableStatus = palette.status === PaletteStatus.CREATION || palette.status === PaletteStatus.AU_CENTRE;
        const isNotAssigned = !palette.bon_enlevement_actuel_id;
        
        return isAtCentre && isAvailableStatus && isNotAssigned;
      });
    },
    enabled: isOpen && !!centreRemplisseurId,
  });

  const availablePalettes = palettesData || [];

  // Mutation to start chargement
  const startChargementMutation = useMutation({
    mutationFn: (data: BonEnlevementChargement) => {
      return bonEnlevementService.startChargement(bonId, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bon-enlevement', bonId] });
      queryClient.invalidateQueries({ queryKey: ['bons-enlevement'] });
      queryClient.invalidateQueries({ queryKey: ['palettes'] });
      onClose();
      setSelectedPaletteIds([]);
      setError(null);
    },
    onError: (error: any) => {
      setError(error?.response?.data?.detail || 'Erreur lors du démarrage du chargement');
    },
  });

  // Reset state when dialog closes
  useEffect(() => {
    if (!isOpen) {
      setSelectedPaletteIds([]);
      setError(null);
    }
  }, [isOpen]);

  const handleTogglePalette = (paletteId: string) => {
    setSelectedPaletteIds((prev) => {
      if (prev.includes(paletteId)) {
        return prev.filter((id) => id !== paletteId);
      } else {
        return [...prev, paletteId];
      }
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (selectedPaletteIds.length === 0) {
      setError('Veuillez sélectionner au moins une palette');
      return;
    }

    startChargementMutation.mutate({
      palette_ids: selectedPaletteIds,
      observations: undefined,
    });
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title="Démarrer le chargement"
      size="lg"
    >
      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <p className="text-sm text-muted-foreground mb-4">
              Sélectionnez les palettes à charger pour ce bon d'enlèvement. Les palettes sélectionnées verront leur statut changé automatiquement.
            </p>

            {isLoadingPalettes ? (
              <div className="p-8 text-center text-muted-foreground">
                Chargement des palettes disponibles...
              </div>
            ) : availablePalettes.length === 0 ? (
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                <p className="text-sm text-amber-800">
                  Aucune palette disponible au centre remplisseur pour le chargement.
                </p>
                <p className="text-xs text-amber-600 mt-2">
                  Les palettes doivent être au centre remplisseur avec le statut "Création" ou "Au centre" et ne pas être déjà assignées à un autre bon.
                </p>
              </div>
            ) : (
              <div className="border rounded-lg p-4 max-h-96 overflow-y-auto">
                <div className="space-y-2">
                  {availablePalettes.map((palette) => (
                    <label
                      key={palette.id}
                      className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-accent cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={selectedPaletteIds.includes(palette.id)}
                        onChange={() => handleTogglePalette(palette.id)}
                        className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">
                            {palette.reference_code || palette.serial_number || palette.id}
                          </span>
                          <span className="text-xs px-2 py-1 rounded bg-blue-100 text-blue-800">
                            {palette.type}
                          </span>
                        </div>
                        {palette.rfid_tag && (
                          <p className="text-xs text-muted-foreground mt-1">
                            RFID: {palette.rfid_tag.tag_number}
                          </p>
                        )}
                        <p className="text-xs text-muted-foreground mt-1">
                          Statut: {palette.status}
                        </p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {selectedPaletteIds.length > 0 && (
              <p className="mt-2 text-sm text-green-600 font-medium">
                {selectedPaletteIds.length} palette{selectedPaletteIds.length > 1 ? 's' : ''} sélectionnée{selectedPaletteIds.length > 1 ? 's' : ''}
              </p>
            )}
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={startChargementMutation.isPending}
            >
              Annuler
            </Button>
            <Button
              type="submit"
              disabled={startChargementMutation.isPending || selectedPaletteIds.length === 0}
              isLoading={startChargementMutation.isPending}
            >
              Démarrer le chargement
            </Button>
          </div>
        </div>
      </form>
    </Dialog>
  );
};

export default StartChargementDialog;
