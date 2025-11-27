import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { bonEnlevementService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { formatDate } from '../../utils/formatters';
import { BonEnlevementStatus } from '../../types';

const BonEnlevementDetailsPage = () => {
  const { id } = useParams<{ id: string }>();

  const { data: bon, isLoading } = useQuery({
    queryKey: ['bon-enlevement', id],
    queryFn: () => bonEnlevementService.getById(id!),
    enabled: !!id,
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

  if (isLoading) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  if (!bon) {
    return <div className="p-8 text-center text-red-600">Bon introuvable</div>;
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link to="/bons-enlevement">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Retour
            </Button>
          </Link>
          <h1 className="text-3xl font-bold mt-4">Bon d'Enlèvement {bon.numero_bon}</h1>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Informations générales</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">N° Bon</p>
              <p className="font-semibold">{bon.numero_bon}</p>
            </div>
            {bon.reference && (
              <div>
                <p className="text-sm text-muted-foreground">Référence</p>
                <p className="font-semibold">{bon.reference}</p>
              </div>
            )}
            <div>
              <p className="text-sm text-muted-foreground">Statut</p>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getStatusColor(bon.status)}`}>
                {getStatusLabel(bon.status)}
              </span>
            </div>
            {bon.centre_remplisseur_name && (
              <div>
                <p className="text-sm text-muted-foreground">Centre Remplisseur</p>
                <p className="font-semibold">{bon.centre_remplisseur_name}</p>
              </div>
            )}
            {bon.grossiste_name && (
              <div>
                <p className="text-sm text-muted-foreground">Grossiste</p>
                <p className="font-semibold">{bon.grossiste_name}</p>
              </div>
            )}
            {bon.depot_principal_name && (
              <div>
                <p className="text-sm text-muted-foreground">Dépôt principal</p>
                <p className="font-semibold">{bon.depot_principal_name}</p>
              </div>
            )}
            {bon.chauffeur_nom && (
              <div>
                <p className="text-sm text-muted-foreground">Chauffeur</p>
                <p className="font-semibold">{bon.chauffeur_nom}</p>
              </div>
            )}
            {bon.vehicule_immatriculation && (
              <div>
                <p className="text-sm text-muted-foreground">Véhicule</p>
                <p className="font-semibold">{bon.vehicule_immatriculation}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Dates et Statistiques</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">Date création</p>
              <p className="font-semibold">{formatDate(bon.date_creation)}</p>
            </div>
            {bon.date_validation && (
              <div>
                <p className="text-sm text-muted-foreground">Date validation</p>
                <p className="font-semibold">{formatDate(bon.date_validation)}</p>
              </div>
            )}
            {bon.date_chargement && (
              <div>
                <p className="text-sm text-muted-foreground">Date chargement</p>
                <p className="font-semibold">{formatDate(bon.date_chargement)}</p>
              </div>
            )}
            {bon.date_depart && (
              <div>
                <p className="text-sm text-muted-foreground">Date départ</p>
                <p className="font-semibold">{formatDate(bon.date_depart)}</p>
              </div>
            )}
            {bon.date_arrivee_finale && (
              <div>
                <p className="text-sm text-muted-foreground">Date arrivée finale</p>
                <p className="font-semibold">{formatDate(bon.date_arrivee_finale)}</p>
              </div>
            )}
            <div>
              <p className="text-sm text-muted-foreground">Palettes</p>
              <p className="text-2xl font-bold">{bon.palettes_count || 0}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Livraisons</p>
              <p className="text-2xl font-bold">{bon.livraisons_count || 0}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Collectes</p>
              <p className="text-2xl font-bold">{bon.collectes_count || 0}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default BonEnlevementDetailsPage;

