import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { partnerService } from '../../services/api';
import { Card, CardContent, Button, ConfirmDialog } from '../../components/common';
import { Plus, Eye, Edit, Trash2 } from 'lucide-react';
import { formatDate } from '../../utils/formatters';
import { Partner, PartnerType } from '../../types';

const PartnersListPage = () => {
  const [page, setPage] = useState(1);
  const [deletePartnerId, setDeletePartnerId] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [activeFilter, setActiveFilter] = useState<string>('');
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['partners', page, typeFilter, activeFilter],
    queryFn: () => partnerService.list({
      page,
      page_size: 20,
      type: typeFilter || undefined,
      is_active: activeFilter === 'true' ? true : activeFilter === 'false' ? false : undefined,
    }),
    retry: 1,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => partnerService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['partners'] });
      setDeletePartnerId(null);
    },
  });

  const getTypeLabel = (type: PartnerType) => {
    const labels: Record<PartnerType, string> = {
      GROSSISTE: 'Grossiste',
      FOURNISSEUR: 'Fournisseur',
      TRANSPORTEUR: 'Transporteur',
      AUTRE: 'Autre',
    };
    return labels[type] || type;
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Partenaires</h1>
          <p className="text-muted-foreground">Gérer vos partenaires (grossistes, fournisseurs, transporteurs)</p>
        </div>
        <Link to="/partners/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Nouveau partenaire
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="mb-4 flex gap-4">
        <select
          value={typeFilter}
          onChange={(e) => {
            setTypeFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 border rounded-lg"
        >
          <option value="">Tous les types</option>
          <option value="GROSSISTE">Grossiste</option>
          <option value="FOURNISSEUR">Fournisseur</option>
          <option value="TRANSPORTEUR">Transporteur</option>
          <option value="AUTRE">Autre</option>
        </select>
        <select
          value={activeFilter}
          onChange={(e) => {
            setActiveFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 border rounded-lg"
        >
          <option value="">Tous</option>
          <option value="true">Actifs</option>
          <option value="false">Inactifs</option>
        </select>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-8 text-center">Chargement...</div>
          ) : error ? (
            <div className="p-8 text-center">
              <div className="text-red-600 mb-2">Erreur lors du chargement des partenaires</div>
              <div className="text-sm text-muted-foreground">
                {error instanceof Error ? error.message : 'Une erreur est survenue'}
              </div>
            </div>
          ) : !data || !data.items || data.items.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              Aucun partenaire trouvé
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-3 text-left text-sm font-medium">Nom</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Type</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Email</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Téléphone</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Ville</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Statut</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Date création</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((partner: Partner) => (
                    <tr key={partner.id} className="border-b hover:bg-accent/50">
                      <td className="px-4 py-3 font-medium">{partner.name}</td>
                      <td className="px-4 py-3">
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                          {getTypeLabel(partner.type)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">{partner.email || '-'}</td>
                      <td className="px-4 py-3 text-sm">{partner.phone || '-'}</td>
                      <td className="px-4 py-3 text-sm">{partner.city || '-'}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                          partner.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {partner.is_active ? 'Actif' : 'Inactif'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">{formatDate(partner.created_at)}</td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end space-x-1">
                          <Link to={`/partners/${partner.id}`}>
                            <Button variant="ghost" size="sm" title="Voir les détails">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Link to={`/partners/${partner.id}/edit`}>
                            <Button variant="ghost" size="sm" title="Modifier">
                              <Edit className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setDeletePartnerId(partner.id)}
                            className="text-red-600 hover:text-red-700"
                            title="Supprimer"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {data && data.total_pages > 1 && (
                <div className="flex items-center justify-between px-4 py-3 border-t">
                  <p className="text-sm text-muted-foreground">
                    Page {data.page} sur {data.total_pages} ({data.total} résultats)
                  </p>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      Précédent
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(p => p + 1)}
                      disabled={page >= data.total_pages}
                    >
                      Suivant
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <ConfirmDialog
        isOpen={!!deletePartnerId}
        onClose={() => setDeletePartnerId(null)}
        onConfirm={() => deletePartnerId && deleteMutation.mutate(deletePartnerId)}
        title="Supprimer le partenaire"
        message="Êtes-vous sûr de vouloir supprimer ce partenaire ? Cette action est irréversible."
        confirmText="Supprimer"
        cancelText="Annuler"
        variant="danger"
        isLoading={deleteMutation.isPending}
      />
    </div>
  );
};

export default PartnersListPage;

