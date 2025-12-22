import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { depotService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button } from '../../components/common';
import { ArrowLeft, Edit } from 'lucide-react';
import { formatDate } from '../../utils/formatters';

const DepotDetailsPage = () => {
  const { id } = useParams<{ id: string }>();

  const { data: depot, isLoading } = useQuery({
    queryKey: ['depot', id],
    queryFn: () => depotService.getById(id!),
    enabled: !!id,
  });

  if (isLoading) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  if (!depot) {
    return <div className="p-8 text-center text-red-600">Dépôt introuvable</div>;
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link to="/depots">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Retour
            </Button>
          </Link>
          <h1 className="text-3xl font-bold mt-4">{depot.name}</h1>
        </div>
        <Link to={`/depots/${id}/edit`}>
          <Button>
            <Edit className="h-4 w-4 mr-2" />
            Modifier
          </Button>
        </Link>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Informations générales</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">Nom</p>
              <p className="font-semibold">{depot.name}</p>
            </div>
            {depot.code && (
              <div>
                <p className="text-sm text-muted-foreground">Code</p>
                <p className="font-semibold">{depot.code}</p>
              </div>
            )}
            {depot.partner_name && (
              <div>
                <p className="text-sm text-muted-foreground">Partenaire</p>
                <p className="font-semibold">{depot.partner_name}</p>
              </div>
            )}
            {depot.address && (
              <div>
                <p className="text-sm text-muted-foreground">Adresse</p>
                <p className="font-semibold">{depot.address}</p>
              </div>
            )}
            {depot.city && (
              <div>
                <p className="text-sm text-muted-foreground">Ville</p>
                <p className="font-semibold">{depot.city}</p>
              </div>
            )}
            {depot.contact_name && (
              <div>
                <p className="text-sm text-muted-foreground">Contact</p>
                <p className="font-semibold">{depot.contact_name}</p>
              </div>
            )}
            <div>
              <p className="text-sm text-muted-foreground">Statut</p>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                depot.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {depot.is_active ? 'Actif' : 'Inactif'}
              </span>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Dépôt principal</p>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                depot.is_main_depot ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {depot.is_main_depot ? 'Oui' : 'Non'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Capacités et Statistiques</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">Palettes</p>
              <p className="text-2xl font-bold">{depot.palettes_count || 0}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Date de création</p>
              <p className="font-semibold">{formatDate(depot.created_at)}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DepotDetailsPage;

