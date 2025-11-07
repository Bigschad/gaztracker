import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { expeditionService } from '../../services/api';
import { Card, Button } from '../../components/common';
import { Plus, Eye } from 'lucide-react';
import { formatDate, getStatusColor, formatStatus } from '../../utils/formatters';

const ExpeditionsListPage = () => {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ['expeditions', page],
    queryFn: () => expeditionService.list({ page, page_size: 20 }),
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Expéditions</h1>
          <p className="text-muted-foreground">Gérer vos expéditions</p>
        </div>
        <Link to="/expeditions/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Nouvelle expédition
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
                  <th className="px-4 py-3 text-left text-sm font-medium">Référence</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Destination</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Statut</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Palettes</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Date création</th>
                  <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map((expedition) => (
                  <tr key={expedition.id} className="border-b hover:bg-accent/50">
                    <td className="px-4 py-3 font-mono text-sm">{expedition.reference}</td>
                    <td className="px-4 py-3">{expedition.destination}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getStatusColor(expedition.status)}`}>
                        {formatStatus(expedition.status)}
                      </span>
                    </td>
                    <td className="px-4 py-3">{expedition.total_palettes}</td>
                    <td className="px-4 py-3 text-sm">{formatDate(expedition.created_at)}</td>
                    <td className="px-4 py-3 text-right">
                      <Link to={`/expeditions/${expedition.id}`}>
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
                  Page {data.page} sur {data.total_pages}
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

export default ExpeditionsListPage;
