import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { depotService } from '../../services/api';
import { Card, CardContent, Button, ConfirmDialog } from '../../components/common';
import { Plus, Eye, Edit, Trash2, Power, PowerOff, Star } from 'lucide-react';
import { DepotList } from '../../types';

const DepotsListPage = () => {
  const [skip, setSkip] = useState(0);
  const [limit] = useState(20);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [activateId, setActivateId] = useState<string | null>(null);
  const [deactivateId, setDeactivateId] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<string>('');
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['depots', skip, limit, activeFilter],
    queryFn: () => depotService.list({
      skip,
      limit,
      is_active: activeFilter === 'true' ? true : activeFilter === 'false' ? false : undefined,
    }),
    retry: 1,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => depotService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['depots'] });
      setDeleteId(null);
    },
  });

  const activateMutation = useMutation({
    mutationFn: (id: string) => depotService.activate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['depots'] });
      setActivateId(null);
    },
  });

  const deactivateMutation = useMutation({
    mutationFn: (id: string) => depotService.deactivate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['depots'] });
      setDeactivateId(null);
    },
  });

  const setMainMutation = useMutation({
    mutationFn: (id: string) => depotService.setAsMain(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['depots'] });
    },
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Dépôts</h1>
          <p className="text-muted-foreground">Gérer les dépôts</p>
        </div>
        <Link to="/depots/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Nouveau dépôt
          </Button>
        </Link>
      </div>

      <div className="mb-4 flex gap-4">
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
            <div className="p-8 text-center text-red-600">Erreur lors du chargement</div>
          ) : !data || data.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">Aucun dépôt trouvé</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-3 text-left text-sm font-medium">Nom</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Code</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Ville</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Principal</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Statut</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((depot: DepotList) => (
                    <tr key={depot.id} className="border-b hover:bg-accent/50">
                      <td className="px-4 py-3 font-medium">{depot.name}</td>
                      <td className="px-4 py-3">{depot.code || '-'}</td>
                      <td className="px-4 py-3 text-sm">{depot.city || '-'}</td>
                      <td className="px-4 py-3">
                        {depot.is_main_depot && <Star className="h-4 w-4 text-yellow-500" />}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                          depot.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {depot.is_active ? 'Actif' : 'Inactif'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end space-x-1">
                          <Link to={`/depots/${depot.id}`}>
                            <Button variant="ghost" size="sm"><Eye className="h-4 w-4" /></Button>
                          </Link>
                          <Link to={`/depots/${depot.id}/edit`}>
                            <Button variant="ghost" size="sm"><Edit className="h-4 w-4" /></Button>
                          </Link>
                          {depot.is_active ? (
                            <Button variant="ghost" size="sm" onClick={() => setDeactivateId(depot.id)}>
                              <PowerOff className="h-4 w-4" />
                            </Button>
                          ) : (
                            <Button variant="ghost" size="sm" onClick={() => setActivateId(depot.id)}>
                              <Power className="h-4 w-4" />
                            </Button>
                          )}
                          {!depot.is_main_depot && (
                            <Button variant="ghost" size="sm" onClick={() => setMainMutation.mutate(depot.id)} title="Définir comme principal">
                              <Star className="h-4 w-4" />
                            </Button>
                          )}
                          <Button variant="ghost" size="sm" onClick={() => setDeleteId(depot.id)} className="text-red-600">
                            <Trash2 className="h-4 w-4" />
                          </Button>
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

      <ConfirmDialog isOpen={!!deleteId} onClose={() => setDeleteId(null)} onConfirm={() => deleteId && deleteMutation.mutate(deleteId)} title="Supprimer" message="Êtes-vous sûr ?" variant="danger" isLoading={deleteMutation.isPending} />
      <ConfirmDialog isOpen={!!activateId} onClose={() => setActivateId(null)} onConfirm={() => activateId && activateMutation.mutate(activateId)} title="Activer" message="Voulez-vous activer ce dépôt ?" isLoading={activateMutation.isPending} />
      <ConfirmDialog isOpen={!!deactivateId} onClose={() => setDeactivateId(null)} onConfirm={() => deactivateId && deactivateMutation.mutate(deactivateId)} title="Désactiver" message="Voulez-vous désactiver ce dépôt ?" isLoading={deactivateMutation.isPending} />
    </div>
  );
};

export default DepotsListPage;

