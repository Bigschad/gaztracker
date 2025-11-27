import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { groupeService } from '../../services/api';
import { Card, CardContent, Button, ConfirmDialog } from '../../components/common';
import { Plus, Eye, Edit, Trash2, Power, PowerOff } from 'lucide-react';
import { GroupeList } from '../../types';

const GroupesListPage = () => {
  const [skip, setSkip] = useState(0);
  const [limit] = useState(20);
  const [deleteGroupeId, setDeleteGroupeId] = useState<string | null>(null);
  const [activateGroupeId, setActivateGroupeId] = useState<string | null>(null);
  const [deactivateGroupeId, setDeactivateGroupeId] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['groupes', skip, limit, activeFilter, searchQuery],
    queryFn: () => groupeService.list({
      skip,
      limit,
      is_active: activeFilter === 'true' ? true : activeFilter === 'false' ? false : undefined,
      search: searchQuery || undefined,
    }),
    retry: 1,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => groupeService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groupes'] });
      setDeleteGroupeId(null);
    },
  });

  const activateMutation = useMutation({
    mutationFn: (id: string) => groupeService.activate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groupes'] });
      setActivateGroupeId(null);
    },
  });

  const deactivateMutation = useMutation({
    mutationFn: (id: string) => groupeService.deactivate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groupes'] });
      setDeactivateGroupeId(null);
    },
  });

  const currentPage = Math.floor(skip / limit) + 1;
  const totalPages = data ? Math.ceil(data.length / limit) : 1;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Groupes</h1>
          <p className="text-muted-foreground">Gérer les groupes de distributeurs</p>
        </div>
        <Link to="/groupes/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Nouveau groupe
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="mb-4 flex gap-4">
        <input
          type="text"
          placeholder="Rechercher..."
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setSkip(0);
          }}
          className="px-3 py-2 border rounded-lg flex-1 max-w-md"
        />
        <select
          value={activeFilter}
          onChange={(e) => {
            setActiveFilter(e.target.value);
            setSkip(0);
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
              <div className="text-red-600 mb-2">Erreur lors du chargement des groupes</div>
              <div className="text-sm text-muted-foreground">
                {error instanceof Error ? error.message : 'Une erreur est survenue'}
              </div>
            </div>
          ) : !data || data.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              Aucun groupe trouvé
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-3 text-left text-sm font-medium">Code</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Nom</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Ville</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Email</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Téléphone</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Statut</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((groupe: GroupeList) => (
                    <tr key={groupe.id} className="border-b hover:bg-accent/50">
                      <td className="px-4 py-3 font-medium">{groupe.code}</td>
                      <td className="px-4 py-3 font-medium">{groupe.name}</td>
                      <td className="px-4 py-3 text-sm">-</td>
                      <td className="px-4 py-3 text-sm">-</td>
                      <td className="px-4 py-3 text-sm">-</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                          groupe.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {groupe.is_active ? 'Actif' : 'Inactif'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end space-x-1">
                          <Link to={`/groupes/${groupe.id}`}>
                            <Button variant="ghost" size="sm" title="Voir les détails">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Link to={`/groupes/${groupe.id}/edit`}>
                            <Button variant="ghost" size="sm" title="Modifier">
                              <Edit className="h-4 w-4" />
                            </Button>
                          </Link>
                          {groupe.is_active ? (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setDeactivateGroupeId(groupe.id)}
                              className="text-orange-600 hover:text-orange-700"
                              title="Désactiver"
                            >
                              <PowerOff className="h-4 w-4" />
                            </Button>
                          ) : (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setActivateGroupeId(groupe.id)}
                              className="text-green-600 hover:text-green-700"
                              title="Activer"
                            >
                              <Power className="h-4 w-4" />
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setDeleteGroupeId(groupe.id)}
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

              {totalPages > 1 && (
                <div className="flex items-center justify-between px-4 py-3 border-t">
                  <p className="text-sm text-muted-foreground">
                    Page {currentPage} sur {totalPages}
                  </p>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSkip(Math.max(0, skip - limit))}
                      disabled={skip === 0}
                    >
                      Précédent
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSkip(skip + limit)}
                      disabled={skip + limit >= (data?.length || 0)}
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
        isOpen={!!deleteGroupeId}
        onClose={() => setDeleteGroupeId(null)}
        onConfirm={() => deleteGroupeId && deleteMutation.mutate(deleteGroupeId)}
        title="Supprimer le groupe"
        message="Êtes-vous sûr de vouloir supprimer ce groupe ? Cette action supprimera également tous les grands distributeurs et centres associés."
        confirmText="Supprimer"
        cancelText="Annuler"
        variant="danger"
        isLoading={deleteMutation.isPending}
      />

      <ConfirmDialog
        isOpen={!!activateGroupeId}
        onClose={() => setActivateGroupeId(null)}
        onConfirm={() => activateGroupeId && activateMutation.mutate(activateGroupeId)}
        title="Activer le groupe"
        message="Voulez-vous activer ce groupe ?"
        confirmText="Activer"
        cancelText="Annuler"
        isLoading={activateMutation.isPending}
      />

      <ConfirmDialog
        isOpen={!!deactivateGroupeId}
        onClose={() => setDeactivateGroupeId(null)}
        onConfirm={() => deactivateGroupeId && deactivateMutation.mutate(deactivateGroupeId)}
        title="Désactiver le groupe"
        message="Voulez-vous désactiver ce groupe ?"
        confirmText="Désactiver"
        cancelText="Annuler"
        isLoading={deactivateMutation.isPending}
      />
    </div>
  );
};

export default GroupesListPage;

