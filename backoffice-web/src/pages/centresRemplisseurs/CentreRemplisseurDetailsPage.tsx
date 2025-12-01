import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { centreRemplisseurService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button } from '../../components/common';
import { ArrowLeft, Edit } from 'lucide-react';
import { formatDate } from '../../utils/formatters';

const CentreRemplisseurDetailsPage = () => {
  const { id } = useParams<{ id: string }>();

  const { data: centre, isLoading } = useQuery({
    queryKey: ['centre-remplisseur', id],
    queryFn: () => centreRemplisseurService.getById(id!),
    enabled: !!id,
  });

  if (isLoading) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  if (!centre) {
    return <div className="p-8 text-center text-red-600">Centre introuvable</div>;
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link to="/centres-remplisseurs">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Retour
            </Button>
          </Link>
          <h1 className="text-3xl font-bold mt-4">{centre.name}</h1>
        </div>
        <Link to={`/centres-remplisseurs/${id}/edit`}>
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
              <p className="font-semibold">{centre.code}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Nom</p>
              <p className="font-semibold">{centre.name}</p>
            </div>
            {centre.partner_name && (
              <div>
                <p className="text-sm text-muted-foreground">Distributeur</p>
                <p className="font-semibold">{centre.partner_name}</p>
              </div>
            )}
            {centre.address && (
              <div>
                <p className="text-sm text-muted-foreground">Adresse</p>
                <p className="font-semibold">{centre.address}</p>
              </div>
            )}
            {centre.city && (
              <div>
                <p className="text-sm text-muted-foreground">Ville</p>
                <p className="font-semibold">{centre.city}</p>
              </div>
            )}
            {centre.contact_name && (
              <div>
                <p className="text-sm text-muted-foreground">Contact</p>
                <p className="font-semibold">{centre.contact_name}</p>
              </div>
            )}
            {centre.contact_phone && (
              <div>
                <p className="text-sm text-muted-foreground">Téléphone contact</p>
                <p className="font-semibold">{centre.contact_phone}</p>
              </div>
            )}
            <div>
              <p className="text-sm text-muted-foreground">Statut</p>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                centre.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {centre.is_active ? 'Actif' : 'Inactif'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Statistiques</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">Bons d'enlèvement</p>
              <p className="text-2xl font-bold">{centre.bons_enlevement_count || 0}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Bons de retour</p>
              <p className="text-2xl font-bold">{centre.bons_retour_count || 0}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Date de création</p>
              <p className="font-semibold">{formatDate(centre.created_at)}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default CentreRemplisseurDetailsPage;

