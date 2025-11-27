import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent, Button } from '../../components/common';
import { bonReceptionRetourService } from '../../services/api';
import { BonReceptionRetourList, BonReceptionRetourStatus } from '../../types';
import { formatDate } from '../../utils/formatters';
import { Plus, Eye, Package, Truck, CheckCircle, XCircle } from 'lucide-react';

const BonsReceptionRetourHomePage = () => {
  // Fetch recent bons
  const { data: recentBons, isLoading } = useQuery({
    queryKey: ['bons-reception-retour-recent'],
    queryFn: () => bonReceptionRetourService.list({ skip: 0, limit: 10 }),
  });

  // Fetch statistics
  const { data: allBons } = useQuery({
    queryKey: ['bons-reception-retour-all'],
    queryFn: () => bonReceptionRetourService.list({ skip: 0, limit: 1000 }),
  });

  // Calculate stats
  const stats = {
    total: allBons?.length || 0,
    enCours: allBons?.filter((b: BonReceptionRetourList) => 
      [BonReceptionRetourStatus.EN_ROUTE, BonReceptionRetourStatus.ARRIVE, 
       BonReceptionRetourStatus.EN_CONTROLE].includes(b.status)
    ).length || 0,
    valides: allBons?.filter((b: BonReceptionRetourList) => 
      b.status === BonReceptionRetourStatus.VALIDE
    ).length || 0,
    refuses: allBons?.filter((b: BonReceptionRetourList) => 
      b.status === BonReceptionRetourStatus.REFUSE
    ).length || 0,
  };

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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Bons de Réception Retour</h1>
          <p className="text-muted-foreground">Gestion des retours de palettes vides</p>
        </div>
        <div className="flex gap-3">
          <Link to="/bons-reception-retour/list">
            <Button variant="secondary">Voir tout</Button>
          </Link>
          <Link to="/bons-reception-retour/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Nouveau bon retour
            </Button>
          </Link>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
              <Package className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">En cours</p>
                <p className="text-2xl font-bold">{stats.enCours}</p>
              </div>
              <Truck className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Validés</p>
                <p className="text-2xl font-bold">{stats.valides}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Refusés</p>
                <p className="text-2xl font-bold">{stats.refuses}</p>
              </div>
              <XCircle className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Bons */}
      <Card>
        <CardHeader>
          <CardTitle>Bons récents</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="p-8 text-center">Chargement...</div>
          ) : !recentBons || recentBons.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">Aucun bon trouvé</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-3 text-left text-sm font-medium">N° BL</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">N° Réception</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Statut</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Date création</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {recentBons.map((bon: BonReceptionRetourList) => (
                    <tr key={bon.id} className="border-b hover:bg-accent/50">
                      <td className="px-4 py-3 font-medium">{bon.numero_bl}</td>
                      <td className="px-4 py-3 text-sm">{bon.numero_reception}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getStatusColor(bon.status)}`}>
                          {getStatusLabel(bon.status)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">{formatDate(bon.date_creation)}</td>
                      <td className="px-4 py-3 text-right">
                        <Link to={`/bons-reception-retour/${bon.id}`}>
                          <Button variant="secondary" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
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

export default BonsReceptionRetourHomePage;

