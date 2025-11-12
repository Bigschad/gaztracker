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
    queryFn: () => paletteService.getById(id!),
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
        <h1 className="text-3xl font-bold mt-4">
          Palette {palette.rfid_tag?.tag_number || palette.id}
        </h1>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Informations générales</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">Tag RFID</p>
              {palette.rfid_tag ? (
                <div>
                  <p className="font-mono font-semibold">{String(palette.rfid_tag?.tag_number || '-')}</p>
                  <span className={`inline-flex mt-1 px-2 py-0.5 text-xs font-semibold rounded ${
                    palette.rfid_tag.status === 'ASSIGNED'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {String(palette.rfid_tag?.status || '')}
                  </span>
                </div>
              ) : (
                <p className="text-sm text-gray-400 italic">Non assigné</p>
              )}
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Type</p>
              <span className="inline-flex px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                {String(palette.type || '')}
              </span>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Statut</p>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getStatusColor(String(palette.status || ''))}`}>
                {formatStatus(String(palette.status || ''))}
              </span>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Localisation actuelle</p>
              <p className="font-semibold">
                {palette.location_address ||
                 (palette.location_latitude && palette.location_longitude
                   ? `${palette.location_latitude.toFixed(4)}, ${palette.location_longitude.toFixed(4)}`
                   : '-')}
              </p>
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
              <p className="font-semibold">{palette.current_expedition_id || '-'}</p>
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
