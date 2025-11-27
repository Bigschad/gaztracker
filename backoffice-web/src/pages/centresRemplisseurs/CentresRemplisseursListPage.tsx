import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { centreRemplisseurService } from '../../services/api';
import { Card, CardContent, Button, ConfirmDialog } from '../../components/common';
import { Plus, Eye, Edit, Trash2, Power, PowerOff } from 'lucide-react';
import { CentreRemplisseurList } from '../../types';

const CentresRemplisseursListPage = () => {
  const [skip, setSkip] = useState(0);
  const [limit] = useState(20);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [activateId, setActivateId] = useState<string | null>(null);
  const [deactivateId, setDeactivateId] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<string>('');
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['centres-remplisseurs', skip, limit, activeFilter],
    queryFn: () => centreRemplisseurService.list({
      skip,
      limit,
      is_active: activeFilter === 'true' ? true : activeFilter === 'false' ? false : undefined,
    }),
    retry: 1,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => centreRemplisseurService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['centres-remplisseurs'] });
      setDeleteId(null);
    },
  });

  const activateMutation = useMutation({
    mutationFn: (id: string) => centreRemplisseurService.activate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['centres-remplisseurs'] });
      setActivateId(null);
    },
  });

  const deactivateMutation = useMutation({
    mutationFn: (id: string) => centreRemplisseurService.deactivate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['centres-remplisseurs'] });
      setDeactivateId(null);
    },
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Centres Remplisseurs</h1>
          <p className="text-muted-foreground">Gérer les centres de remplissage</p>
        </div>
        <Link to="/centres-remplisseurs/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Nouveau centre
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
            <div className="p-8 text-center text-muted-foreground">Aucun centre trouvé</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 py-3 text-left text-sm font-medium">Code</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Nom</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Ville</th>
                    <th className="px-4 py-3 text-left text-sm font-medium">Statut</th>
                    <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((centre: CentreRemplisseurList) => (
                    <tr key={centre.id} className="border-b hover:bg-accent/50">
                      <td className="px-4 py-3 font-medium">{centre.code}</td>
                      <td className="px-4 py-3">{centre.name}</td>
                      <td className="px-4 py-3 text-sm">{centre.city || '-'}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${
                          centre.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {centre.is_active ? 'Actif' : 'Inactif'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end space-x-1">
                          <Link to={`/centres-remplisseurs/${centre.id}`}>
                            <Button variant="ghost" size="sm"><Eye className="h-4 w-4" /></Button>
                          </Link>
                          <Link to={`/centres-remplisseurs/${centre.id}/edit`}>
                            <Button variant="ghost" size="sm"><Edit className="h-4 w-4" /></Button>
                          </Link>
                          {centre.is_active ? (
                            <Button variant="ghost" size="sm" onClick={() => setDeactivateId(centre.id)}>
                              <PowerOff className="h-4 w-4" />
                            </Button>
                          ) : (
                            <Button variant="ghost" size="sm" onClick={() => setActivateId(centre.id)}>
                              <Power className="h-4 w-4" />
                            </Button>
                          )}
                          <Button variant="ghost" size="sm" onClick={() => setDeleteId(centre.id)} className="text-red-600">
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
      <ConfirmDialog isOpen={!!activateId} onClose={() => setActivateId(null)} onConfirm={() => activateId && activateMutation.mutate(activateId)} title="Activer" message="Voulez-vous activer ce centre ?" isLoading={activateMutation.isPending} />
      <ConfirmDialog isOpen={!!deactivateId} onClose={() => setDeactivateId(null)} onConfirm={() => deactivateId && deactivateMutation.mutate(deactivateId)} title="Désactiver" message="Voulez-vous désactiver ce centre ?" isLoading={deactivateMutation.isPending} />
    </div>
  );
};

export default CentresRemplisseursListPage;

