import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent, Button, ConfirmDialog } from '../../components/common';
import { bonEnlevementService } from '../../services/api';
import { BonEnlevementList, BonEnlevementStatus } from '../../types';
import { formatDate } from '../../utils/formatters';
import { Plus, Eye, Edit, Trash2, TrendingUp, Package, Truck, CheckCircle } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { UserRole } from '../../types/user';

const BonsEnlevementHomePage = () => {
  const [bonToDelete, setBonToDelete] = useState<BonEnlevementList | null>(null);
  const [bonToValidate, setBonToValidate] = useState<BonEnlevementList | null>(null);
  const queryClient = useQueryClient();
  const { user } = useAuth();
  
  const canValidate = user?.role === UserRole.RESPONSABLE_LOGISTIQUE || user?.role === UserRole.ADMIN;

  // Fetch recent bons
  const { data: recentBons, isLoading } = useQuery({
    queryKey: ['bons-enlevement-recent'],
    queryFn: () => bonEnlevementService.list({ skip: 0, limit: 10 }),
  });

  // Fetch statistics
  const { data: allBons } = useQuery({
    queryKey: ['bons-enlevement-all'],
    queryFn: () => bonEnlevementService.list({ skip: 0, limit: 1000 }),
  });

  // Calculate stats
  const stats = {
    total: allBons?.length || 0,
    enCours: allBons?.filter((b: BonEnlevementList) => 
      [BonEnlevementStatus.VALIDE, BonEnlevementStatus.EN_CHARGEMENT, 
       BonEnlevementStatus.EN_ROUTE, BonEnlevementStatus.EN_LIVRAISON].includes(b.status)
    ).length || 0,
    termines: allBons?.filter((b: BonEnlevementList) => 
      b.status === BonEnlevementStatus.TERMINE
    ).length || 0,
    creation: allBons?.filter((b: BonEnlevementList) => 
      b.status === BonEnlevementStatus.CREATION
    ).length || 0,
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

  const deleteMutation = useMutation({
    mutationFn: (bon: BonEnlevementList) => {
      return bonEnlevementService.annuler(bon.id, 'Suppression par l\'utilisateur');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bons-enlevement'] });
      setBonToDelete(null);
    },
    onError: (error: any) => {
      console.error('Error deleting bon:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur lors de la suppression';
      alert(errorMessage);
    },
  });

  const handleConfirmDelete = () => {
    if (bonToDelete) {
      deleteMutation.mutate(bonToDelete);
    }
  };

  const validateMutation = useMutation({
    mutationFn: (bon: BonEnlevementList) => {
      if (!user?.id) {
        throw new Error('Utilisateur non connecté');
      }
      return bonEnlevementService.valider(bon.id, {
        validateur_centre_id: user.id,
        observations: undefined,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bons-enlevement'] });
      setBonToValidate(null);
    },
    onError: (error: any) => {
      console.error('Error validating bon:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur lors de la validation';
      alert(errorMessage);
    },
  });

  const handleConfirmValidate = () => {
    if (bonToValidate) {
      validateMutation.mutate(bonToValidate);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Bons d'Enlèvement</h1>
          <p className="text-muted-foreground">Gestion des livraisons de palettes pleines</p>
        </div>
        <div className="flex gap-3">
          <Link to="/bons-enlevement/list">
            <Button variant="secondary">Voir tout</Button>
          </Link>
          <Link to="/bons-enlevement/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Nouveau bon
            </Button>
          </Link>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
              <Package className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">En attente</p>
                <p className="text-2xl font-bold">{stats.creation}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-gray-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">En cours</p>
                <p className="text-2xl font-bold">{stats.enCours}</p>
              </div>
              <Truck className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Terminés</p>
                <p className="text-2xl font-bold">{stats.termines}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Bons */}
      <Card>
        <CardHeader>
          <CardTitle>Bons récents</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="p-8 text-center">Chargement...</div>
          ) : !recentBons || recentBons.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">Aucun bon trouvé</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-3 text-left text-sm font-medium">N° Bon</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Statut</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Date création</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Chauffeur</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {recentBons.map((bon: BonEnlevementList) => (
                    <tr key={bon.id} className="border-b hover:bg-accent/50">
                      <td className="px-4 py-3 font-medium">{bon.numero_bon}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getStatusColor(bon.status)}`}>
                          {getStatusLabel(bon.status)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">{formatDate(bon.date_creation)}</td>
                      <td className="px-4 py-3 text-sm">{bon.chauffeur_nom || '-'}</td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end space-x-1">
                          {bon.status === BonEnlevementStatus.CREATION && (
                            <>
                              <Link to={`/bons-enlevement/${bon.id}/edit`}>
                                <Button variant="ghost" size="sm" title="Modifier">
                                  <Edit className="h-4 w-4" />
                                </Button>
                              </Link>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setBonToDelete(bon)}
                                className="text-red-600 hover:text-red-700"
                                title="Supprimer"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </>
                          )}
                          {bon.status === BonEnlevementStatus.CREATION && canValidate && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setBonToValidate(bon)}
                              className="text-green-600 hover:text-green-700"
                              title="Valider"
                            >
                              <CheckCircle className="h-4 w-4" />
                            </Button>
                          )}
                          <Link to={`/bons-enlevement/${bon.id}`}>
                            <Button variant="ghost" size="sm" title="Voir les détails">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <ConfirmDialog
        isOpen={!!bonToDelete}
        onClose={() => setBonToDelete(null)}
        onConfirm={handleConfirmDelete}
        title="Supprimer le bon d'enlèvement"
        message={`Êtes-vous sûr de vouloir supprimer le bon d'enlèvement "${bonToDelete?.numero_bon}" ? Cette action est irréversible.`}
        confirmText="Supprimer"
        cancelText="Annuler"
        variant="danger"
        isLoading={deleteMutation.isPending}
      />

      <ConfirmDialog
        isOpen={!!bonToValidate}
        onClose={() => setBonToValidate(null)}
        onConfirm={handleConfirmValidate}
        title="Valider le bon d'enlèvement"
        message={`Êtes-vous sûr de vouloir valider le bon d'enlèvement "${bonToValidate?.numero_bon}" ? Cette action changera le statut à "Validé".`}
        confirmText="Valider"
        cancelText="Annuler"
        variant="info"
        isLoading={validateMutation.isPending}
      />
    </div>
  );
};

export default BonsEnlevementHomePage;

