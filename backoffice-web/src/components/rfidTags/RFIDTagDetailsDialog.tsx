import { Dialog, Button } from '../common';
import { RFIDTagDetail, RFIDTagStatus } from '../../types';
import { formatDate } from '../../utils/formatters';
import { Package, Calendar, MapPin, TrendingUp, Info } from 'lucide-react';

interface RFIDTagDetailsDialogProps {
  isOpen: boolean;
  onClose: () => void;
  tag: RFIDTagDetail | null;
  onEdit?: () => void;
}

const getStatusLabel = (status: RFIDTagStatus): string => {
  const statusLabels: Record<RFIDTagStatus, string> = {
    [RFIDTagStatus.NOT_ASSIGNED]: 'Non assigné',
    [RFIDTagStatus.ASSIGNED]: 'Assigné',
    [RFIDTagStatus.LOST]: 'Perdu',
    [RFIDTagStatus.DAMAGED]: 'Endommagé',
  };
  return statusLabels[status];
};

const getStatusColor = (status: RFIDTagStatus): string => {
  const statusColors: Record<RFIDTagStatus, string> = {
    [RFIDTagStatus.NOT_ASSIGNED]: 'bg-gray-100 text-gray-800',
    [RFIDTagStatus.ASSIGNED]: 'bg-green-100 text-green-800',
    [RFIDTagStatus.LOST]: 'bg-red-100 text-red-800',
    [RFIDTagStatus.DAMAGED]: 'bg-orange-100 text-orange-800',
  };
  return statusColors[status];
};

export const RFIDTagDetailsDialog = ({
  isOpen,
  onClose,
  tag,
  onEdit,
}: RFIDTagDetailsDialogProps) => {
  // Note: Palette details are temporarily disabled due to type mismatch between UUID and number
  // TODO: Update palette service to support UUID-based IDs
  const palette: any = null;
  const paletteLoading = false;
  const movements: any[] = [];
  const movementsLoading = false;

  if (!tag) return null;

  return (
    <Dialog isOpen={isOpen} onClose={onClose} title="Détails du tag RFID" size="xl">
      <div className="space-y-6">
        {/* Header avec numéro de tag et statut */}
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">
              {tag.label || tag.tag_number}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              {tag.label && (
                <>
                  Numéro: <span className="font-mono">{tag.tag_number}</span>
                  <br />
                </>
              )}
              ID: <span className="font-mono text-xs">{tag.id}</span>
            </p>
          </div>
          <div className="flex flex-col gap-2">
            <span
              className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${getStatusColor(
                tag.status
              )}`}
            >
              {getStatusLabel(tag.status)}
            </span>
            {tag.is_active ? (
              <span className="inline-flex px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                Actif
              </span>
            ) : (
              <span className="inline-flex px-3 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                Inactif
              </span>
            )}
          </div>
        </div>

        {/* Informations générales */}
        <div>
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Info className="h-5 w-5 mr-2" />
            Informations générales
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {tag.label && (
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">
                  Libellé
                </label>
                <p className="text-base text-gray-900">{tag.label}</p>
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Date de création
              </label>
              <p className="text-base text-gray-900">{formatDate(tag.created_at)}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Dernière modification
              </label>
              <p className="text-base text-gray-900">{formatDate(tag.updated_at)}</p>
            </div>
            {tag.assigned_at && (
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">
                  Date d'assignation
                </label>
                <p className="text-base text-gray-900">{formatDate(tag.assigned_at)}</p>
              </div>
            )}
            {tag.notes && (
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-500 mb-1">
                  Notes
                </label>
                <p className="text-base text-gray-900">{tag.notes}</p>
              </div>
            )}
          </div>
        </div>

        {/* Palette actuelle */}
        {tag.status === RFIDTagStatus.ASSIGNED && tag.palette_id && (
          <div>
            <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Package className="h-5 w-5 mr-2" />
              Palette actuelle
            </h4>
            {paletteLoading ? (
              <div className="text-center py-4">Chargement...</div>
            ) : palette ? (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-blue-700 mb-1">
                      Type
                    </label>
                    <p className="text-base text-blue-900 font-semibold">{palette.palette_type}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-blue-700 mb-1">
                      Statut
                    </label>
                    <p className="text-base text-blue-900">{palette.status}</p>
                  </div>
                  {palette.current_location && (
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-blue-700 mb-1 flex items-center">
                        <MapPin className="h-4 w-4 mr-1" />
                        Localisation
                      </label>
                      <p className="text-sm text-blue-900">{palette.current_location}</p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-4 text-gray-500">
                Impossible de charger les détails de la palette
              </div>
            )}
          </div>
        )}

        {/* Historique des mouvements */}
        {tag.status === RFIDTagStatus.ASSIGNED && tag.palette_id && (
          <div>
            <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              Historique des mouvements
            </h4>
            {movementsLoading ? (
              <div className="text-center py-4">Chargement...</div>
            ) : movements && movements.length > 0 ? (
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {movements.map((movement: any) => (
                  <div
                    key={movement.id}
                    className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{movement.action}</p>
                        {movement.location && (
                          <p className="text-sm text-gray-600 mt-1 flex items-center">
                            <MapPin className="h-3 w-3 mr-1" />
                            {movement.location}
                          </p>
                        )}
                        {movement.notes && (
                          <p className="text-sm text-gray-500 mt-1">{movement.notes}</p>
                        )}
                      </div>
                      <div className="text-right ml-4">
                        <p className="text-xs text-gray-500 flex items-center">
                          <Calendar className="h-3 w-3 mr-1" />
                          {formatDate(movement.timestamp)}
                        </p>
                        {movement.status_before && movement.status_after && (
                          <p className="text-xs text-gray-500 mt-1">
                            {movement.status_before} → {movement.status_after}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-4 text-gray-500">
                Aucun mouvement enregistré
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end space-x-3 pt-4 border-t">
          {onEdit && (
            <Button variant="outline" onClick={onEdit}>
              Modifier
            </Button>
          )}
          <Button variant="outline" onClick={onClose}>
            Fermer
          </Button>
        </div>
      </div>
    </Dialog>
  );
};
