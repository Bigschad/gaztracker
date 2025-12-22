import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { paletteService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button } from '../../components/common';
import { ArrowLeft, Edit, Package, Factory, Truck, Warehouse, CheckCircle, XCircle, AlertCircle, Loader2 } from 'lucide-react';
import { formatDate, getStatusColor, formatStatus } from '../../utils/formatters';
import { PaletteCondition, PaletteStatus } from '../../types';

const PaletteDetailsPage = () => {
  const { id } = useParams<{ id: string }>();

  const { data: palette, isLoading } = useQuery({
    queryKey: ['palette', id],
    queryFn: () => paletteService.getById(id!),
    enabled: !!id,
  });

  // Définir l'ordre des statuts dans le workflow
  const statusWorkflow: PaletteStatus[] = [
    PaletteStatus.CREATION,
    PaletteStatus.AU_CENTRE,
    PaletteStatus.EN_CHARGEMENT,
    PaletteStatus.EN_ROUTE_LIVRAISON,
    PaletteStatus.AU_DEPOT,
    PaletteStatus.EN_ROUTE_RETOUR,
    PaletteStatus.EN_CONTROLE,
    PaletteStatus.VALIDEE,
    PaletteStatus.OUT,
  ];

  // Obtenir l'index du statut actuel dans le workflow
  const getCurrentStatusIndex = () => {
    if (!palette?.status) return -1;
    return statusWorkflow.indexOf(palette.status as PaletteStatus);
  };

  // Obtenir l'icône pour chaque statut
  const getStatusIcon = (status: PaletteStatus) => {
    const icons: Record<PaletteStatus, typeof Package> = {
      [PaletteStatus.CREATION]: Package,
      [PaletteStatus.AU_CENTRE]: Factory,
      [PaletteStatus.EN_CHARGEMENT]: Loader2,
      [PaletteStatus.EN_ROUTE_LIVRAISON]: Truck,
      [PaletteStatus.AU_DEPOT]: Warehouse,
      [PaletteStatus.EN_ROUTE_RETOUR]: Truck,
      [PaletteStatus.EN_CONTROLE]: AlertCircle,
      [PaletteStatus.VALIDEE]: CheckCircle,
      [PaletteStatus.OUT]: XCircle,
    };
    return icons[status] || Package;
  };

  // Obtenir le label pour chaque statut
  const getStatusLabel = (status: PaletteStatus) => {
    const labels: Record<PaletteStatus, string> = {
      [PaletteStatus.CREATION]: 'Création',
      [PaletteStatus.AU_CENTRE]: 'Au centre',
      [PaletteStatus.EN_CHARGEMENT]: 'En chargement',
      [PaletteStatus.EN_ROUTE_LIVRAISON]: 'En route livraison',
      [PaletteStatus.AU_DEPOT]: 'Au dépôt',
      [PaletteStatus.EN_ROUTE_RETOUR]: 'En route retour',
      [PaletteStatus.EN_CONTROLE]: 'En contrôle',
      [PaletteStatus.VALIDEE]: 'Validée',
      [PaletteStatus.OUT]: 'Hors service',
    };
    return labels[status] || status;
  };

  if (isLoading) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  if (!palette) {
    return <div className="p-8 text-center">Palette non trouvée</div>;
  }

  const currentStatusIndex = getCurrentStatusIndex();

  return (
    <div>
      {/* Fil d'Ariane de navigation */}
      <div className="mb-4 flex items-center space-x-2 text-sm text-muted-foreground">
        <Link to="/palettes" className="hover:text-foreground transition-colors">
          Palettes
        </Link>
        <span>/</span>
        <span className="text-foreground font-medium">
          {palette.reference_code || palette.serial_number || 'Détails'}
        </span>
      </div>

      {/* En-tête avec boutons */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/palettes">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Retour
            </Button>
          </Link>
          <h1 className="text-3xl font-bold">
            Palette {palette.reference_code || palette.serial_number || palette.rfid_tag?.tag_number || palette.id}
          </h1>
        </div>
        <Link to={`/palettes/${id}/edit`}>
          <Button>
            <Edit className="h-4 w-4 mr-2" />
            Modifier
          </Button>
        </Link>
      </div>

      {/* Fil d'Ariane du statut avec illustration */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="mb-4">
            <h3 className="text-sm font-medium text-muted-foreground mb-2">Statut actuel</h3>
            <div className="flex items-center space-x-2">
              {palette.status && (() => {
                const Icon = getStatusIcon(palette.status as PaletteStatus);
                return (
                  <>
                    <Icon className={`h-5 w-5 ${getStatusColor(String(palette.status)).split(' ')[0]}`} />
                    <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded ${getStatusColor(String(palette.status))}`}>
                      {getStatusLabel(palette.status as PaletteStatus)}
                    </span>
                  </>
                );
              })()}
            </div>
          </div>
          
          {/* Workflow visuel */}
          <div className="mt-6">
            <h3 className="text-sm font-medium text-muted-foreground mb-4">Cycle de vie de la palette</h3>
            <div className="flex items-start w-full">
              {statusWorkflow.map((status, index) => {
                const Icon = getStatusIcon(status);
                const isCompleted = currentStatusIndex > index;
                const isCurrent = currentStatusIndex === index;
                const isPending = currentStatusIndex < index;
                
                return (
                  <div key={status} className="flex items-center flex-1 min-w-0">
                    <div className="flex flex-col items-center w-full">
                      <div
                        className={`
                          w-9 h-9 rounded-full flex items-center justify-center border-2 transition-all shadow-sm
                          ${isCompleted ? 'bg-green-50 border-green-500 text-green-700 shadow-green-100' : ''}
                          ${isCurrent ? 'bg-blue-50 border-blue-500 text-blue-700 ring-2 ring-blue-200 shadow-lg' : ''}
                          ${isPending ? 'bg-gray-50 border-gray-300 text-gray-400' : ''}
                        `}
                      >
                        <Icon className={`h-4 w-4 ${isCurrent ? 'animate-pulse' : ''}`} />
                      </div>
                      <span className={`mt-1.5 text-[10px] text-center font-medium leading-tight px-0.5 ${isCurrent ? 'font-bold text-blue-700' : isCompleted ? 'text-green-700' : 'text-gray-500'}`}>
                        {getStatusLabel(status)}
                      </span>
                    </div>
                    {index < statusWorkflow.length - 1 && (
                      <div className={`flex-1 h-0.5 mx-0.5 mt-4 rounded-full transition-colors ${isCompleted ? 'bg-green-400' : 'bg-gray-300'}`} />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Informations générales</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm text-muted-foreground">Code de référence</p>
              <p className="font-mono font-semibold">
                {palette.reference_code || palette.serial_number || '-'}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Numéro de série</p>
              <p className="font-mono font-semibold">{palette.serial_number || '-'}</p>
            </div>
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
              <p className="text-sm text-muted-foreground">Condition</p>
              {palette.condition ? (
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                  palette.condition === PaletteCondition.NEUVE
                    ? 'bg-green-100 text-green-800'
                    : 'bg-orange-100 text-orange-800'
                }`}>
                  {palette.condition === PaletteCondition.NEUVE ? 'Neuve' : 'Reconditionnée'}
                </span>
              ) : (
                <p className="text-sm text-gray-400 italic">Non spécifiée</p>
              )}
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Statut</p>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getStatusColor(String(palette.status || ''))}`}>
                {formatStatus(String(palette.status || ''))}
              </span>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Localisation actuelle</p>
              {palette.current_centre_remplisseur ? (
                <div>
                  <p className="font-semibold">{palette.current_centre_remplisseur.name}</p>
                  {palette.current_centre_remplisseur.code && (
                    <p className="text-sm text-muted-foreground">
                      Code: {palette.current_centre_remplisseur.code}
                    </p>
                  )}
                  {palette.current_centre_remplisseur.city && (
                    <p className="text-sm text-muted-foreground">
                      {palette.current_centre_remplisseur.city}
                      {palette.current_centre_remplisseur.postal_code && ` (${palette.current_centre_remplisseur.postal_code})`}
                    </p>
                  )}
                </div>
              ) : palette.location_address ? (
                <p className="font-semibold">{palette.location_address}</p>
              ) : palette.location_latitude && palette.location_longitude ? (
                <p className="font-semibold">
                  {palette.location_latitude.toFixed(4)}, {palette.location_longitude.toFixed(4)}
                </p>
              ) : (
                <p className="text-sm text-gray-400 italic">Non spécifiée</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Informations de suivi</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {palette.capacity && (
              <div>
                <p className="text-sm text-muted-foreground">Capacité</p>
                <p className="font-semibold">{palette.capacity} bouteilles</p>
              </div>
            )}
            {palette.manufacturing_date && (
              <div>
                <p className="text-sm text-muted-foreground">Date de fabrication</p>
                <p className="font-semibold">{formatDate(palette.manufacturing_date)}</p>
              </div>
            )}
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
