import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { bonReceptionRetourService } from '../../services/api';
import { Card, CardContent, Button } from '../../components/common';
import { Plus, Eye } from 'lucide-react';
import { formatDate } from '../../utils/formatters';
import { BonReceptionRetourList, BonReceptionRetourStatus } from '../../types';

const BonsReceptionRetourListPage = () => {
  const [skip, setSkip] = useState(0);
  const [limit] = useState(20);
  const [statusFilter, setStatusFilter] = useState<string>('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['bons-reception-retour', skip, limit, statusFilter],
    queryFn: () => bonReceptionRetourService.list({
      skip,
      limit,
      status: statusFilter ? (statusFilter as BonReceptionRetourStatus) : undefined,
    }),
    retry: 1,
  });

  const getStatusLabel = (status: BonReceptionRetourStatus) => {
    const labels: Record<BonReceptionRetourStatus, string> = {
      CREATION: 'Création',
      EN_ROUTE: 'En route',
      ARRIVE: 'Arrivé',
      EN_CONTROLE: 'En contrôle',
      VALIDE: 'Validé',
      REFUSE: 'Refusé',
    };
    return labels[status] || status;
  };

  const getStatusColor = (status: BonReceptionRetourStatus) => {
    const colors: Record<BonReceptionRetourStatus, string> = {
      CREATION: 'bg-gray-100 text-gray-800',
      EN_ROUTE: 'bg-blue-100 text-blue-800',
      ARRIVE: 'bg-yellow-100 text-yellow-800',
      EN_CONTROLE: 'bg-orange-100 text-orange-800',
      VALIDE: 'bg-green-100 text-green-800',
      REFUSE: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Bons de Réception Retour</h1>
          <p className="text-muted-foreground">Gérer les retours de palettes vides</p>
        </div>
        <Link to="/bons-reception-retour/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Nouveau bon retour
          </Button>
        </Link>
      </div>

      <div className="mb-4 flex gap-4">
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setSkip(0);
          }}
          className="px-3 py-2 border rounded-lg"
        >
          <option value="">Tous les statuts</option>
          <option value="CREATION">Création</option>
          <option value="EN_ROUTE">En route</option>
          <option value="ARRIVE">Arrivé</option>
          <option value="EN_CONTROLE">En contrôle</option>
          <option value="VALIDE">Validé</option>
          <option value="REFUSE">Refusé</option>
        </select>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-8 text-center">Chargement...</div>
          ) : error ? (
            <div className="p-8 text-center text-red-600">Erreur lors du chargement</div>
          ) : !data || data.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">Aucun bon retour trouvé</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-3 text-left text-sm font-medium">N° BL</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">N° Réception</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Statut</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Date création</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Date arrivée</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Palettes</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((bon: BonReceptionRetourList) => (
                    <tr key={bon.id} className="border-b hover:bg-accent/50">
                      <td className="px-4 py-3 font-medium">{bon.numero_bl}</td>
                      <td className="px-4 py-3">{bon.numero_reception}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getStatusColor(bon.status)}`}>
                          {getStatusLabel(bon.status)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">{formatDate(bon.date_creation)}</td>
                      <td className="px-4 py-3 text-sm">{bon.date_arrivee ? formatDate(bon.date_arrivee) : '-'}</td>
                      <td className="px-4 py-3 text-sm">{bon.palette_count}</td>
                      <td className="px-4 py-3 text-right">
                        <Link to={`/bons-reception-retour/${bon.id}`}>
                          <Button variant="ghost" size="sm"><Eye className="h-4 w-4" /></Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default BonsReceptionRetourListPage;

