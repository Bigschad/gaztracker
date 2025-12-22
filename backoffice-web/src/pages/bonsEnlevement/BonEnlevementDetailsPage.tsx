import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { bonEnlevementService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button, ConfirmDialog } from '../../components/common';
import { StartChargementDialog } from '../../components/bonsEnlevement';
import { ArrowLeft, FileText, CheckCircle, Loader2, Truck, PackageCheck, XCircle, Trash2, Package } from 'lucide-react';
import { formatDate } from '../../utils/formatters';
import { BonEnlevementStatus } from '../../types';
import { useAuth } from '../../hooks/useAuth';
import { UserRole } from '../../types/user';

const BonEnlevementDetailsPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showValidateDialog, setShowValidateDialog] = useState(false);
  const [showChargementDialog, setShowChargementDialog] = useState(false);
  
  const canValidate = user?.role === UserRole.RESPONSABLE_LOGISTIQUE || user?.role === UserRole.ADMIN;
  const canStartChargement = (user?.role === UserRole.OPERATEUR_USINE || user?.role === UserRole.CHAUFFEUR || user?.role === UserRole.ADMIN);

  const { data: bon, isLoading } = useQuery({
    queryKey: ['bon-enlevement', id],
    queryFn: () => bonEnlevementService.getById(id!),
    enabled: !!id,
  });

  const deleteMutation = useMutation({
    mutationFn: () => {
      return bonEnlevementService.annuler(id!, 'Suppression par l\'utilisateur');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bons-enlevement'] });
      queryClient.invalidateQueries({ queryKey: ['bon-enlevement', id] });
      navigate('/bons-enlevement/list');
    },
    onError: (error: any) => {
      console.error('Error deleting bon:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur lors de la suppression';
      alert(errorMessage);
    },
  });

  const handleConfirmDelete = () => {
    deleteMutation.mutate();
  };

  const validateMutation = useMutation({
    mutationFn: () => {
      if (!user?.id) {
        throw new Error('Utilisateur non connecté');
      }
      return bonEnlevementService.valider(id!, {
        validateur_centre_id: user.id,
        observations: undefined,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bon-enlevement', id] });
      queryClient.invalidateQueries({ queryKey: ['bons-enlevement'] });
      setShowValidateDialog(false);
    },
    onError: (error: any) => {
      console.error('Error validating bon:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur lors de la validation';
      alert(errorMessage);
    },
  });

  const handleConfirmValidate = () => {
    validateMutation.mutate();
  };

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

  // Définir l'ordre des statuts dans le workflow normal (sans ANNULE)
  const statusWorkflow: BonEnlevementStatus[] = [
    BonEnlevementStatus.CREATION,
    BonEnlevementStatus.VALIDE,
    BonEnlevementStatus.EN_CHARGEMENT,
    BonEnlevementStatus.EN_ROUTE,
    BonEnlevementStatus.EN_LIVRAISON,
    BonEnlevementStatus.TERMINE,
  ];

  // Obtenir l'index du statut actuel dans le workflow
  const getCurrentStatusIndex = () => {
    if (!bon?.status) return -1;
    if (bon.status === BonEnlevementStatus.ANNULE) return -1; // ANNULE n'est pas dans le workflow normal
    return statusWorkflow.indexOf(bon.status);
  };

  // Obtenir l'icône pour chaque statut
  const getStatusIcon = (status: BonEnlevementStatus) => {
    const icons: Record<BonEnlevementStatus, typeof FileText> = {
      [BonEnlevementStatus.CREATION]: FileText,
      [BonEnlevementStatus.VALIDE]: CheckCircle,
      [BonEnlevementStatus.EN_CHARGEMENT]: Loader2,
      [BonEnlevementStatus.EN_ROUTE]: Truck,
      [BonEnlevementStatus.EN_LIVRAISON]: PackageCheck,
      [BonEnlevementStatus.TERMINE]: CheckCircle,
      [BonEnlevementStatus.ANNULE]: XCircle,
    };
    return icons[status] || FileText;
  };

  if (isLoading) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  if (!bon) {
    return <div className="p-8 text-center text-red-600">Bon introuvable</div>;
  }

  const currentStatusIndex = getCurrentStatusIndex();
  const isAnnule = bon.status === BonEnlevementStatus.ANNULE;

  return (
    <div>
      {/* Fil d'Ariane de navigation */}
      <div className="mb-4 flex items-center space-x-2 text-sm text-muted-foreground">
        <Link to="/bons-enlevement/list" className="hover:text-foreground transition-colors">
          Bons d'Enlèvement
        </Link>
        <span>/</span>
        <span className="text-foreground font-medium">
          {bon.numero_bon}
        </span>
      </div>

      {/* En-tête avec boutons */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/bons-enlevement/list">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Retour
            </Button>
          </Link>
          <h1 className="text-3xl font-bold">
            Bon d'Enlèvement {bon.numero_bon}
          </h1>
        </div>
        {bon.status === BonEnlevementStatus.CREATION && (
          <div className="flex items-center space-x-2">
            <Link to={`/bons-enlevement/${id}/edit`}>
              <Button>
                Modifier
              </Button>
            </Link>
            {canValidate && (
              <Button
                variant="outline"
                onClick={() => setShowValidateDialog(true)}
                className="text-green-600 hover:text-green-700 border-green-300 hover:border-green-400"
              >
                <CheckCircle className="h-4 w-4 mr-2" />
                Valider
              </Button>
            )}
            <Button
              variant="outline"
              onClick={() => setShowDeleteDialog(true)}
              className="text-red-600 hover:text-red-700 border-red-300 hover:border-red-400"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Supprimer
            </Button>
          </div>
        )}
        {bon.status === BonEnlevementStatus.VALIDE && canStartChargement && (
          <Button
            onClick={() => setShowChargementDialog(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            <Package className="h-4 w-4 mr-2" />
            Démarrer le chargement
          </Button>
        )}
      </div>

      {/* Fil d'Ariane du statut avec illustration */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="mb-4">
            <h3 className="text-sm font-medium text-muted-foreground mb-2">Statut actuel</h3>
            <div className="flex items-center space-x-2">
              {bon.status && (() => {
                const Icon = getStatusIcon(bon.status);
                return (
                  <>
                    <Icon className={`h-5 w-5 ${getStatusColor(bon.status).split(' ')[0]}`} />
                    <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded ${getStatusColor(bon.status)}`}>
                      {getStatusLabel(bon.status)}
                    </span>
                  </>
                );
              })()}
            </div>
          </div>
          
          {/* Workflow visuel - seulement si le bon n'est pas annulé */}
          {!isAnnule && (
            <div className="mt-6">
              <h3 className="text-sm font-medium text-muted-foreground mb-4">Cycle de vie du bon d'enlèvement</h3>
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
          )}

          {/* Message spécial si le bon est annulé */}
          {isAnnule && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <XCircle className="h-5 w-5 text-red-600" />
                <p className="text-sm font-medium text-red-800">
                  Ce bon d'enlèvement a été annulé
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

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

      <ConfirmDialog
        isOpen={showDeleteDialog}
        onClose={() => setShowDeleteDialog(false)}
        onConfirm={handleConfirmDelete}
        title="Supprimer le bon d'enlèvement"
        message={`Êtes-vous sûr de vouloir supprimer le bon d'enlèvement "${bon.numero_bon}" ? Cette action est irréversible.`}
        confirmText="Supprimer"
        cancelText="Annuler"
        variant="danger"
        isLoading={deleteMutation.isPending}
      />

      <ConfirmDialog
        isOpen={showValidateDialog}
        onClose={() => setShowValidateDialog(false)}
        onConfirm={handleConfirmValidate}
        title="Valider le bon d'enlèvement"
        message={`Êtes-vous sûr de vouloir valider le bon d'enlèvement "${bon.numero_bon}" ? Cette action changera le statut à "Validé".`}
        confirmText="Valider"
        cancelText="Annuler"
        variant="info"
        isLoading={validateMutation.isPending}
      />

      {bon.centre_remplisseur_id && (
        <StartChargementDialog
          bonId={id!}
          centreRemplisseurId={bon.centre_remplisseur_id}
          isOpen={showChargementDialog}
          onClose={() => setShowChargementDialog(false)}
        />
      )}
    </div>
  );
};

export default BonEnlevementDetailsPage;

