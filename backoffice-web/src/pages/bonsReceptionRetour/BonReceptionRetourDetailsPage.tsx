import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { bonReceptionRetourService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { formatDate } from '../../utils/formatters';
import { BonReceptionRetourStatus } from '../../types';

const BonReceptionRetourDetailsPage = () => {
  const { id } = useParams<{ id: string }>();

  const { data: bon, isLoading } = useQuery({
    queryKey: ['bon-reception-retour', id],
    queryFn: () => bonReceptionRetourService.getById(id!),
    enabled: !!id,
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

  if (isLoading) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  if (!bon) {
    return <div className="p-8 text-center text-red-600">Bon retour introuvable</div>;
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link to="/bons-reception-retour">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Retour
            </Button>
          </Link>
          <h1 className="text-3xl font-bold mt-4">Bon de Réception Retour {bon.numero_bl}</h1>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Informations générales</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">N° BL</p>
              <p className="font-semibold">{bon.numero_bl}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">N° Réception</p>
              <p className="font-semibold">{bon.numero_reception}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Statut</p>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getStatusColor(bon.status)}`}>
                {getStatusLabel(bon.status)}
              </span>
            </div>
            {bon.grossiste_name && (
              <div>
                <p className="text-sm text-muted-foreground">Grossiste</p>
                <p className="font-semibold">{bon.grossiste_name}</p>
              </div>
            )}
            {bon.depot_depart_name && (
              <div>
                <p className="text-sm text-muted-foreground">Dépôt de départ</p>
                <p className="font-semibold">{bon.depot_depart_name}</p>
              </div>
            )}
            {bon.centre_remplisseur_name && (
              <div>
                <p className="text-sm text-muted-foreground">Centre Remplisseur</p>
                <p className="font-semibold">{bon.centre_remplisseur_name}</p>
              </div>
            )}
            {bon.vehicule_immatriculation && (
              <div>
                <p className="text-sm text-muted-foreground">Véhicule</p>
                <p className="font-semibold">{bon.vehicule_immatriculation}</p>
              </div>
            )}
            {bon.transporteur_nom && (
              <div>
                <p className="text-sm text-muted-foreground">Transporteur</p>
                <p className="font-semibold">{bon.transporteur_nom}</p>
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
            {bon.date_depart && (
              <div>
                <p className="text-sm text-muted-foreground">Date départ</p>
                <p className="font-semibold">{formatDate(bon.date_depart)}</p>
              </div>
            )}
            {bon.date_arrivee && (
              <div>
                <p className="text-sm text-muted-foreground">Date arrivée</p>
                <p className="font-semibold">{formatDate(bon.date_arrivee)}</p>
              </div>
            )}
            {bon.date_controle && (
              <div>
                <p className="text-sm text-muted-foreground">Date contrôle</p>
                <p className="font-semibold">{formatDate(bon.date_controle)}</p>
              </div>
            )}
            {bon.date_validation && (
              <div>
                <p className="text-sm text-muted-foreground">Date validation</p>
                <p className="font-semibold">{formatDate(bon.date_validation)}</p>
              </div>
            )}
            <div>
              <p className="text-sm text-muted-foreground">Palettes</p>
              <p className="text-2xl font-bold">{bon.palette_count}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Palettes acceptées</p>
              <p className="text-2xl font-bold text-green-600">{bon.palette_acceptees}</p>
            </div>
            {bon.palette_refusees > 0 && (
              <div>
                <p className="text-sm text-muted-foreground">Palettes refusées</p>
                <p className="text-2xl font-bold text-red-600">{bon.palette_refusees}</p>
              </div>
            )}
            {bon.taux_acceptation !== null && bon.taux_acceptation !== undefined && (
              <div>
                <p className="text-sm text-muted-foreground">Taux d'acceptation</p>
                <p className="text-2xl font-bold">{bon.taux_acceptation.toFixed(1)}%</p>
              </div>
            )}
            {bon.details_count !== null && (
              <div>
                <p className="text-sm text-muted-foreground">Lignes de détail</p>
                <p className="text-2xl font-bold">{bon.details_count}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {bon.observations && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Observations</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{bon.observations}</p>
          </CardContent>
        </Card>
      )}

      {bon.manquants && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Manquants</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-red-600">{bon.manquants}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default BonReceptionRetourDetailsPage;

