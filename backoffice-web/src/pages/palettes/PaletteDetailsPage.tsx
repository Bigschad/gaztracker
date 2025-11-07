import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { paletteService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button } from '../../components/common';
import { ArrowLeft } from 'lucide-react';
import { formatDate, getStatusColor, formatStatus } from '../../utils/formatters';

const PaletteDetailsPage = () => {
  const { id } = useParams<{ id: string }>();

  const { data: palette, isLoading } = useQuery({
    queryKey: ['palette', id],
    queryFn: () => paletteService.getById(Number(id)),
    enabled: !!id,
  });

  if (isLoading) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  if (!palette) {
    return <div className="p-8 text-center">Palette non trouvée</div>;
  }

  return (
    <div>
      <div className="mb-6">
        <Link to="/palettes">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
        </Link>
        <h1 className="text-3xl font-bold mt-4">Palette {palette.rfid_tag}</h1>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Informations générales</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">Tag RFID</p>
              <p className="font-mono font-semibold">{palette.rfid_tag}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Type</p>
              <span className="inline-flex px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                {palette.palette_type}
              </span>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Quantité de bouteilles</p>
              <p className="font-semibold">{palette.bottle_quantity}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Statut</p>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getStatusColor(palette.status)}`}>
                {formatStatus(palette.status)}
              </span>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Localisation actuelle</p>
              <p className="font-semibold">{palette.current_location || '-'}</p>
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
              <p className="font-semibold">{formatDate(palette.created_at)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Dernière mise à jour</p>
              <p className="font-semibold">{formatDate(palette.updated_at)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">ID Expédition</p>
              <p className="font-semibold">{palette.expedition_id || '-'}</p>
            </div>
            {palette.notes && (
              <div>
                <p className="text-sm text-muted-foreground">Notes</p>
                <p className="text-sm">{palette.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PaletteDetailsPage;
