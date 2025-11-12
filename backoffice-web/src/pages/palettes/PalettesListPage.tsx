import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { paletteService } from '../../services/api';
import { Card, CardContent, Button } from '../../components/common';
import { AssignRFIDDialog } from '../../components/palettes';
import { Plus, Eye, Tag } from 'lucide-react';
import { formatDate, getStatusColor, formatStatus } from '../../utils/formatters';
import { Palette } from '../../types';

const PalettesListPage = () => {
  const [page, setPage] = useState(1);
  const [selectedPalette, setSelectedPalette] = useState<Palette | null>(null);
  const [isAssignDialogOpen, setIsAssignDialogOpen] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ['palettes', page],
    queryFn: () => paletteService.list({ page, page_size: 20 }),
    retry: 1,
  });

  const handleAssignRFID = (palette: Palette) => {
    setSelectedPalette(palette);
    setIsAssignDialogOpen(true);
  };

  const handleCloseAssignDialog = () => {
    setIsAssignDialogOpen(false);
    setSelectedPalette(null);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Palettes</h1>
          <p className="text-muted-foreground">Gérer vos palettes de bouteilles</p>
        </div>
        <Link to="/palettes/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Nouvelle palette
          </Button>
        </Link>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-8 text-center">Chargement...</div>
          ) : error ? (
            <div className="p-8 text-center">
              <div className="text-red-600 mb-2">Erreur lors du chargement des palettes</div>
              <div className="text-sm text-muted-foreground">
                {error instanceof Error ? error.message : 'Une erreur est survenue'}
              </div>
            </div>
          ) : !data || !data.items || data.items.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              Aucune palette trouvée
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-3 text-left text-sm font-medium">Tag RFID</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Type</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Statut</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Localisation</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Date création</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((palette) => (
                  <tr key={palette.id} className="border-b hover:bg-accent/50">
                    <td className="px-4 py-3">
                      {palette.rfid_tag ? (
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-sm">{String(palette.rfid_tag?.tag_number || '-')}</span>
                          <span className={`text-xs px-2 py-0.5 rounded ${
                            palette.rfid_tag?.status === 'ASSIGNED'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {String(palette.rfid_tag?.status || '')}
                          </span>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400 italic">Non assigné</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                        {String(palette.type || '')}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getStatusColor(String(palette.status || ''))}`}>
                        {formatStatus(String(palette.status || ''))}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {palette.location_address ||
                       (palette.location_latitude && palette.location_longitude
                         ? `${palette.location_latitude.toFixed(4)}, ${palette.location_longitude.toFixed(4)}`
                         : '-')}
                    </td>
                    <td className="px-4 py-3 text-sm">{formatDate(palette.created_at)}</td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end space-x-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleAssignRFID(palette)}
                          title={palette.rfid_tag ? "Réassigner un tag RFID" : "Attribuer un tag RFID"}
                        >
                          <Tag className={`h-4 w-4 ${palette.rfid_tag ? 'text-blue-600' : 'text-gray-400'}`} />
                        </Button>
                        <Link to={`/palettes/${palette.id}`}>
                          <Button variant="ghost" size="sm" title="Voir les détails">
                            <Eye className="h-4 w-4" />
                          </Button>
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {data && data.total_pages > 1 && (
              <div className="flex items-center justify-between px-4 py-3 border-t">
                <p className="text-sm text-muted-foreground">
                  Page {data.page} sur {data.total_pages} ({data.total} résultats)
                </p>
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    Précédent
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(p => p + 1)}
                    disabled={page >= data.total_pages}
                  >
                    Suivant
                  </Button>
                </div>
              </div>
            )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialogue d'attribution de tag RFID */}
      {selectedPalette && (
        <AssignRFIDDialog
          palette={selectedPalette}
          isOpen={isAssignDialogOpen}
          onClose={handleCloseAssignDialog}
        />
      )}
    </div>
  );
};

export default PalettesListPage;
