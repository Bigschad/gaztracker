import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { expeditionService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { formatDate, getStatusColor, formatStatus } from '../../utils/formatters';

const ExpeditionDetailsPage = () => {
  const { id } = useParams<{ id: string }>();

  const { data: expedition, isLoading } = useQuery({
    queryKey: ['expedition', id],
    queryFn: () => expeditionService.getById(Number(id)),
    enabled: !!id,
  });

  if (isLoading) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  if (!expedition) {
    return <div className="p-8 text-center">Expédition non trouvée</div>;
  }

  return (
    <div>
      <div className="mb-6">
        <Link to="/expeditions">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
        </Link>
        <h1 className="text-3xl font-bold mt-4">Expédition {expedition.reference}</h1>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Informations générales</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">Référence</p>
              <p className="font-mono font-semibold">{expedition.reference}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Statut</p>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getStatusColor(expedition.status)}`}>
                {formatStatus(expedition.status)}
              </span>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Destination</p>
              <p className="font-semibold">{expedition.destination}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Contact</p>
              <p>{expedition.destination_contact}</p>
              <p className="text-sm text-muted-foreground">{expedition.destination_phone}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Nombre de palettes</p>
              <p className="font-semibold">{expedition.total_palettes}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Informations de suivi</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">Date de création</p>
              <p className="font-semibold">{formatDate(expedition.created_at)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Date de départ</p>
              <p className="font-semibold">{formatDate(expedition.departure_date)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Date de livraison prévue</p>
              <p className="font-semibold">{formatDate(expedition.expected_delivery_date)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Date de livraison réelle</p>
              <p className="font-semibold">{formatDate(expedition.actual_delivery_date)}</p>
            </div>
            {expedition.notes && (
              <div>
                <p className="text-sm text-muted-foreground">Notes</p>
                <p className="text-sm">{expedition.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ExpeditionDetailsPage;
