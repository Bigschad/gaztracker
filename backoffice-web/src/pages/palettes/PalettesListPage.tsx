import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { paletteService } from '../../services/api';
import { Card, Button } from '../../components/common';
import { Plus, Eye } from 'lucide-react';
import { formatDate, getStatusColor, formatStatus } from '../../utils/formatters';

const PalettesListPage = () => {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['palettes', page],
    queryFn: () => paletteService.list({ page, page_size: 20 }),
  });

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
        {isLoading ? (
          <div className="p-8 text-center">Chargement...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="px-4 py-3 text-left text-sm font-medium">Tag RFID</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Type</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Quantité</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Statut</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Localisation</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Date création</th>
                  <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map((palette) => (
                  <tr key={palette.id} className="border-b hover:bg-accent/50">
                    <td className="px-4 py-3 font-mono text-sm">{palette.rfid_tag}</td>
                    <td className="px-4 py-3">
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                        {palette.palette_type}
                      </span>
                    </td>
                    <td className="px-4 py-3">{palette.bottle_quantity}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getStatusColor(palette.status)}`}>
                        {formatStatus(palette.status)}
                      </span>
                    </td>
                    <td className="px-4 py-3">{palette.current_location || '-'}</td>
                    <td className="px-4 py-3 text-sm">{formatDate(palette.created_at)}</td>
                    <td className="px-4 py-3 text-right">
                      <Link to={`/palettes/${palette.id}`}>
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </Link>
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
      </Card>
    </div>
  );
};

export default PalettesListPage;
