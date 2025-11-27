import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { bonEnlevementService } from '../../services/api';
import { Card, CardContent, Button } from '../../components/common';
import { Eye, Plus } from 'lucide-react';
import { formatDate } from '../../utils/formatters';
import { BonEnlevementList, BonEnlevementStatus } from '../../types';

const BonsEnlevementListPage = () => {
  const [skip, setSkip] = useState(0);
  const [limit] = useState(20);
  const [statusFilter, setStatusFilter] = useState<string>('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['bons-enlevement', skip, limit, statusFilter],
    queryFn: () => bonEnlevementService.list({
      skip,
      limit,
      status: statusFilter ? (statusFilter as BonEnlevementStatus) : undefined,
    }),
    retry: 1,
  });

  const getStatusLabel = (status: BonEnlevementStatus) => {
    const labels: Record<BonEnlevementStatus, string> = {
      CREATION: 'Création',
      VALIDE: 'Validé',
      EN_CHARGEMENT: 'En chargement',
      EN_ROUTE: 'En route',
      EN_LIVRAISON: 'En livraison',
      TERMINE: 'Terminé',
      ANNULE: 'Annulé',
    };
    return labels[status] || status;
  };

  const getStatusColor = (status: BonEnlevementStatus) => {
    const colors: Record<BonEnlevementStatus, string> = {
      CREATION: 'bg-gray-100 text-gray-800',
      VALIDE: 'bg-blue-100 text-blue-800',
      EN_CHARGEMENT: 'bg-yellow-100 text-yellow-800',
      EN_ROUTE: 'bg-purple-100 text-purple-800',
      EN_LIVRAISON: 'bg-orange-100 text-orange-800',
      TERMINE: 'bg-green-100 text-green-800',
      ANNULE: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Bons d'Enlèvement</h1>
          <p className="text-muted-foreground">Gérer les bons d'enlèvement</p>
        </div>
        <Link to="/bons-enlevement/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Nouveau bon d'enlèvement
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
          <option value="VALIDE">Validé</option>
          <option value="EN_CHARGEMENT">En chargement</option>
          <option value="EN_ROUTE">En route</option>
          <option value="EN_LIVRAISON">En livraison</option>
          <option value="TERMINE">Terminé</option>
          <option value="ANNULE">Annulé</option>
        </select>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-8 text-center">Chargement...</div>
          ) : error ? (
            <div className="p-8 text-center text-red-600">Erreur lors du chargement</div>
          ) : !data || data.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">Aucun bon trouvé</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-3 text-left text-sm font-medium">N° Bon</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Statut</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Date création</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Chauffeur</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((bon: BonEnlevementList) => (
                    <tr key={bon.id} className="border-b hover:bg-accent/50">
                      <td className="px-4 py-3 font-medium">{bon.numero_bon}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getStatusColor(bon.status)}`}>
                          {getStatusLabel(bon.status)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">{formatDate(bon.date_creation)}</td>
                      <td className="px-4 py-3 text-sm">{bon.chauffeur_nom || '-'}</td>
                      <td className="px-4 py-3 text-right">
                        <Link to={`/bons-enlevement/${bon.id}`}>
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

export default BonsEnlevementListPage;

