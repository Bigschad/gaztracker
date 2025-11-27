import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { groupeService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button } from '../../components/common';
import { ArrowLeft, Edit } from 'lucide-react';
import { formatDate } from '../../utils/formatters';

const GroupeDetailsPage = () => {
  const { id } = useParams<{ id: string }>();

  const { data: groupe, isLoading } = useQuery({
    queryKey: ['groupe', id],
    queryFn: () => groupeService.getById(id!),
    enabled: !!id,
  });

  if (isLoading) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  if (!groupe) {
    return <div className="p-8 text-center text-red-600">Groupe introuvable</div>;
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link to="/groupes">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Retour
            </Button>
          </Link>
          <h1 className="text-3xl font-bold mt-4">{groupe.name}</h1>
        </div>
        <Link to={`/groupes/${id}/edit`}>
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
              <p className="text-sm text-muted-foreground">Code</p>
              <p className="font-semibold">{groupe.code}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Nom</p>
              <p className="font-semibold">{groupe.name}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Statut</p>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                groupe.is_active
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {groupe.is_active ? 'Actif' : 'Inactif'}
              </span>
            </div>
            {groupe.address && (
              <div>
                <p className="text-sm text-muted-foreground">Adresse</p>
                <p className="font-semibold">{groupe.address}</p>
              </div>
            )}
            {groupe.city && (
              <div>
                <p className="text-sm text-muted-foreground">Ville</p>
                <p className="font-semibold">{groupe.city}</p>
              </div>
            )}
            {groupe.phone && (
              <div>
                <p className="text-sm text-muted-foreground">Téléphone</p>
                <p className="font-semibold">{groupe.phone}</p>
              </div>
            )}
            {groupe.email && (
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="font-semibold">{groupe.email}</p>
              </div>
            )}
            {groupe.notes && (
              <div>
                <p className="text-sm text-muted-foreground">Notes</p>
                <p className="font-semibold">{groupe.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Statistiques</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">Grands distributeurs</p>
              <p className="text-2xl font-bold">{groupe.grand_distributeurs_count || 0}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Date de création</p>
              <p className="font-semibold">{formatDate(groupe.created_at)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Dernière modification</p>
              <p className="font-semibold">{formatDate(groupe.updated_at)}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default GroupeDetailsPage;

